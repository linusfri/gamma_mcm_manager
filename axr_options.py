import json
import typing


def main():
    try:
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)

        with open("axr_options.ltx", "r") as file_original:
            original = file_original.readlines()

        make_file_backup(original, "axr_options_backup.ltx")
        print_settings_and_original_file_diff(original, settings)

        merged_settings = merge_settings(original, settings)
        with open("axr_options.ltx", "w") as file_original:
            file_original.writelines(merged_settings)
    except OSError as error:
        print("Something went wrong while reading or writing to files.", error)


def print_settings_and_original_file_diff(
    original: list[str], settings: dict[str, str]
):
    """
    Check to see if any of our settings are not valid, as in not present in the original file.
    Though they still might be valid but hasn't been created in the original file yet.
    This is mainly a warning to users that they might have settings that are not recognized by the game.
    """
    try:
        raw_original_mcm_settings, _, _ = get_settings_section(original, "[mcm]\n")
        original_mcm_settings = {
            line.strip().split("=")[0].strip() if "=" in line else ""
            for line in raw_original_mcm_settings
        }

        diff: list[str] = []
        for new_setting_name, value in settings.items():
            if new_setting_name not in original_mcm_settings:
                diff.append(f"{new_setting_name} = {value}")

        if diff:
            print("The following settings are not present in the original file:")
            for line in diff:
                print(f"  {line}")
            print(
                "This CAN mean that the game does not recognize these settings. If all settings are working, you can ignore this message."
            )
    except ValueError as error:
        print(
            "Could not calculate settings diff. Failed to get mcm settings from original file.",
            error,
        )


def make_file_backup(file_contents: list[str], path: str) -> None:
    """Makes a backup with specified file contents at path. Raises OSError on failure."""
    with open(path, "w") as file:
        file.writelines(file_contents)


def merge_settings(original: list[str], settings: dict[str, typing.Any]) -> list[str]:
    """
    Merge the settings with the original file.
    This will overwrite any existing settings in the original file.
    """
    result = original.copy()
    applied_settings: set[str] = set()
    EIGHT_SPACES = (
        " " * 8
    )  # This is how MCM settings are indented in the original axr_options.ltx

    try:
        mcm_settings, mcm_settings_start_index, mcm_settings_end_index = (
            get_settings_section(result, "[mcm]\n")
        )

        # First pass: update existing lines with new settings
        for i, line in enumerate(mcm_settings):
            original_setting_name = (
                line.strip().split("=")[0].strip() if "=" in line else ""
            )

            if original_setting_name in settings and original_setting_name != "":
                setting_value = settings[original_setting_name]
                mcm_settings[i] = (
                    f"{EIGHT_SPACES}{original_setting_name} = {setting_value if not isinstance(setting_value, bool) else str(setting_value).lower()}\n"
                )
                applied_settings.add(original_setting_name)

        # Second pass: add any settings that weren't found in the original axr_options file
        unapplied_settings = {
            k: v for k, v in settings.items() if k not in applied_settings
        }
        for setting_name, setting_value in unapplied_settings.items():
            mcm_settings.insert(
                len(mcm_settings) - 1,
                f"{EIGHT_SPACES}{setting_name} = {setting_value if not isinstance(setting_value, bool) else str(setting_value).lower()}\n",
            )

        result = (
            result[: mcm_settings_start_index + 1]
            + sorted(mcm_settings)
            + result[mcm_settings_end_index:]
        )

        return result
    except ValueError as error:
        print(
            """
        Could not merge settings. Failed to get mcm settings from original file.
        This probably means that there is no MCM section in the original file.
        """,
            error,
        )
        return original


def get_settings_section(
    axr_file_contents: list[str], section_name: str
) -> tuple[list[str], int, int]:
    """
    Returns the provided section from an axr file.
    Raises ValueError if section is not present.

    Example: mcm_settings = get_settings_section(axr_file_contents, "[mcm]\\n")
    """
    settings_section_begin_index = axr_file_contents.index(section_name)
    settings_section_end_index = None
    for i in range(settings_section_begin_index + 1, len(axr_file_contents)):
        if axr_file_contents[i].startswith("[") or axr_file_contents[i] == "\n":
            settings_section_end_index = (
                i - 1
            )  # We only want actual settings, not new lines or brackets
            break

    # If we have start of mcm but no end, we assume the MCM settings are at the end of the file
    if settings_section_end_index is None:
        settings_section_end_index = len(axr_file_contents)

    mcm_settings = axr_file_contents[
        settings_section_begin_index + 1 : settings_section_end_index
    ]

    return mcm_settings, settings_section_begin_index, settings_section_end_index


if __name__ == "__main__":
    main()
