import json
import typing

def main():
    axr_settings: dict[str, typing.Any] = {}
    axr_orig: list[str] = []

    with open("settings.json", "r") as settings_file:
        axr_settings = json.load(settings_file)

    with open("axr_options.ltx", "r") as file_axr_orig:
        axr_orig = file_axr_orig.readlines()

    make_original_file_backup(axr_orig)

    print_settings_and_original_file_diff(axr_orig, axr_settings)

    merged_settings = merge_settings(axr_orig, axr_settings)
    with open("axr_options.ltx", "w") as file_axr_orig:
        file_axr_orig.writelines(merged_settings)

def print_settings_and_original_file_diff(original: list[str], settings: dict[str, str]):
    """
    Check to see if any of our settings are not valid, as in not present in the original file.
    Though they still might be valid but hasn't been created in the original file yet.
    This is mainly a warning to users that they might have settings that are not recognized by the game.
    """

    original_settings: set[str] = set()
    for line in original:
        if '=' in line:
            setting_name = line.strip().split('=')[0].strip() if '=' in line else ''
            if setting_name:
                original_settings.add(setting_name)
    
    diff: list[str] = []
    for new_setting_name, value in settings.items():
        if new_setting_name not in original_settings:
            diff.append(f"{new_setting_name} = {value}")
    
    if diff:
        print("The following settings are not present in the original file:")
        for line in diff:
            print(f"  {line}")
        print("This CAN mean that the game does not recognize these settings. If all settings are working, you can ignore this message.")

def make_original_file_backup(original: list[str]) -> None:
    with open("axr_options_backup.ltx", "w") as file_axr_orig_backup:
        file_axr_orig_backup.writelines(original)

def merge_settings(original: list[str], settings: dict[str, typing.Any]) -> list[str]:
    """
    Merge the settings with the original file.
    This will overwrite any existing settings in the original file.
    """
    result = original.copy()
    settings_applied: set[str] = set()
    EIGHT_SPACES = " " * 8
    
    # First pass: update existing lines that contain our keys
    for i, line in enumerate(result):
        original_setting_name = line.strip().split('=')[0].strip() if '=' in line else ''
        for setting_name, setting_value in settings.items():
            if setting_name == original_setting_name:
                result[i] = f"{EIGHT_SPACES}{setting_name} = {setting_value if type(setting_value) is not bool else str(setting_value).lower()}\n"
                settings_applied.add(setting_name)
                break
    
    # Second pass: add any settings that weren't found in the original file
    mcm_settings_index = result.index("[mcm]\n")
    for (setting_name, setting_value) in settings.items():
        if setting_name in settings_applied:
            continue

        result.insert(mcm_settings_index + 1, f"{EIGHT_SPACES}{setting_name} = {setting_value if type(setting_value) is not bool else str(setting_value).lower()}\n")

    return sort_mcm_settings(result)

def sort_mcm_settings(settings: list[str]) -> list[str]:
    """ Sort the MCM settings in alphabetical order."""

    try:
        mcm_settings, mcm_settings_begin_index, mcm_settings_end_index = get_mcm_settings(settings)
        return settings[:mcm_settings_begin_index + 1] + mcm_settings + settings[mcm_settings_end_index:]
    except ValueError:
        print("No [mcm] section found in the settings file. Cannot sort MCM settings.")
        return settings

def get_mcm_settings(settings: list[str]) -> tuple[list[str], int, int]:
    mcm_settings_begin_index = settings.index("[mcm]\n")
    mcm_settings_end_index = None
    for i in range(mcm_settings_begin_index + 1, len(settings)):
        if settings[i].startswith("[") or settings[i] == "\n":
            mcm_settings_end_index = i - 1
            break

    # If we have start of mcm but no end, we assume the MCM settings are at the end of the file
    if mcm_settings_end_index is None:
        mcm_settings_end_index = len(settings)

    mcm_settings = sorted(settings[mcm_settings_begin_index + 1:mcm_settings_end_index])

    return mcm_settings, mcm_settings_begin_index, mcm_settings_end_index

if __name__ == "__main__":
    main()