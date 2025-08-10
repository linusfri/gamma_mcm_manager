import json
import typing
import sys
from datetime import datetime
from classes.setting import Setting
import os

path = sys.argv[1] if len(sys.argv) > 1 else "."


def main():
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    check_create_required_files()

    try:
        with open(f"{path}/settings.json", "r") as user_settings_file:
            user_settings = json.load(user_settings_file)

        with open(f"{path}/axr_options.ltx", "r") as default_file:
            default = default_file.readlines()

        with open(f"{path}/axr_options_saved.ltx", "r") as user_axr_ltx_settings_file:
            user_axr_ltx_settings = user_axr_ltx_settings_file.readlines()

        make_file_backup(default, f"{path}/axr_options_backup_{current_datetime}.ltx")
        print_settings_and_default_file_diff(default, user_settings)

        with open(f"{path}/axr_options.ltx", "w") as default_file:
            default_file.writelines(merge_settings(default, user_settings))

        create_json_file_from_user_and_default_settings_diff(
            default, user_axr_ltx_settings, path
        )
    except OSError as error:
        print("Something went wrong while reading or writing to files.", error)


def check_create_required_files():
    """Creates the required files if not present. Otherwise does nothing."""
    required_files = [
        f"{path}/settings.json",
        f"{path}/generated_user_settings.json",
        f"{path}/axr_options.ltx",
        f"{path}/axr_options_saved.ltx",
    ]

    for file_path in required_files:
        if file_path.endswith(".json"):
            with open(file_path, "w") as file:
                file.writelines("{}")
                continue

        if not os.path.exists(file_path):
            open(file_path, "w").close()


def print_settings_and_default_file_diff(
    default: list[str], user_settings: dict[str, str]
):
    """
    Check to see if any of our settings are not valid, as in not present in the default file.
    Though they still might be valid but hasn't been created in the default file yet.
    This is mainly a warning to users that they might have settings that are not recognized by the game.
    """
    try:
        raw_default_mcm_settings, _, _ = get_settings_section(default, "[mcm]\n")
        default_mcm_settings_names = {
            get_setting_from_line(line, "=").name if "=" in line else ""
            for line in raw_default_mcm_settings
        }

        diff: list[str] = []
        for setting_name, value in user_settings.items():
            if setting_name not in default_mcm_settings_names:
                diff.append(f"{setting_name} = {value}")

        if diff:
            print("The following settings are not present in the default file:")
            for line in diff:
                print(f"  {line}")
            print(
                "This CAN mean that the game does not recognize these settings. If all settings are working, you can ignore this message."
            )
    except ValueError as error:
        print(
            "Could not calculate settings diff. Failed to get mcm settings from default file.",
            error,
        )


def create_json_file_from_user_and_default_settings_diff(
    default: list[str], user_axr_ltx_settings: list[str], path: str
):
    """
    Generates a json file based on the difference in existing user defined axr_options.ltx and default axr_options.ltx
    The point of this is to not have to go through custom settings manually and compare with default.
    """
    raw_default_mcm_settings, _, _ = get_settings_section(default, "[mcm]\n")
    raw_user_mcm_settings, _, _ = get_settings_section(user_axr_ltx_settings, "[mcm]\n")
    json_data: dict[str, typing.Any] = {}

    default_mcm_settings = parse_settings_from_lines(raw_default_mcm_settings)
    user_mcm_settings = parse_settings_from_lines(raw_user_mcm_settings)

    for user_setting_name, user_setting in user_mcm_settings.items():
        if not default_mcm_settings.get(user_setting_name):
            json_data[user_setting_name] = user_setting.value
            continue

        default_setting = default_mcm_settings[user_setting_name]
        if user_setting.value != default_setting.value:
            json_data[user_setting_name] = user_setting.value

    with open(f"{path}/generated_user_settings.json", "w") as generated_user_settings:
        generated_user_settings.writelines(json.dumps(json_data))


def parse_settings_from_lines(lines: list[str]) -> dict[str, Setting]:
    """Parse settings from a list of lines, returning a dictionary of setting name to Setting object."""
    settings: dict[str, Setting] = {}
    for line in lines:
        if "=" in line:
            setting = get_setting_from_line(line, "=")
            settings[setting.name] = setting
    return settings


def get_setting_from_line(line: str, separator: str) -> Setting:
    setting_data = line.strip().split(separator)
    name = setting_data[0].strip()
    value = setting_data[1].strip() if len(setting_data) >= 2 else ""

    return Setting(name, value)


def make_file_backup(file_contents: list[str], path: str) -> None:
    """Makes a backup with specified file contents at path. Raises OSError on failure."""
    with open(path, "w") as file:
        file.writelines(file_contents)


def merge_settings(
    default: list[str], user_settings: dict[str, typing.Any]
) -> list[str]:
    """
    Merge the user settings with the default file.
    This will overwrite any existing settings in the default file with the corresponding new settings.
    """
    applied_settings: set[str] = set()
    EIGHT_SPACES = (
        " " * 8
    )  # This is how MCM settings are indented in the default axr_options.ltx

    try:
        mcm_settings, mcm_settings_start_index, mcm_settings_end_index = (
            get_settings_section(default, "[mcm]\n")
        )

        # First pass: update existing default settings with user settings
        for i, line in enumerate(mcm_settings):
            if "=" not in line:
                continue

            default_setting = get_setting_from_line(line, "=")

            if default_setting.name in user_settings and default_setting.name != "":
                user_setting = Setting(
                    default_setting.name, user_settings[default_setting.name]
                )
                mcm_settings[i] = f"{EIGHT_SPACES}{user_setting}"
                applied_settings.add(default_setting.name)

        # Second pass: add any settings that weren't found in the default axr_options file
        unapplied_settings = {
            Setting(setting_name, value)
            for setting_name, value in user_settings.items()
            if setting_name not in applied_settings
        }
        for user_setting in unapplied_settings:
            mcm_settings.append(
                f"{EIGHT_SPACES}{user_setting}",
            )

        return (
            default[: mcm_settings_start_index + 1]
            + sorted(mcm_settings)
            + default[mcm_settings_end_index:]
        )
    except ValueError as error:
        print(
            """
        Could not merge settings. Failed to get mcm settings from default file.
        This probably means that there is no MCM section in the default file.
        """,
            error,
        )
        return default


def get_settings_section(
    file_contents: list[str], section_name: str
) -> tuple[list[str], int, int]:
    """
    Returns the provided section from an options file, along with start and end index for section.
    Raises ValueError if section is not present.

    Example: mcm_settings = get_settings_section(file_contents, "[mcm]\\n")
    """
    settings_section_start_index = file_contents.index(section_name)
    settings_section_end_index = None
    for i in range(settings_section_start_index + 1, len(file_contents)):
        if file_contents[i].startswith("[") or file_contents[i].strip(" ") == "\n":
            settings_section_end_index = (
                i  # We only want actual settings, not new sections
            )
            break

    # If we have start of mcm but no end, we assume the MCM settings are at the end of the file
    if settings_section_end_index is None:
        settings_section_end_index = len(file_contents)

    mcm_settings = file_contents[
        settings_section_start_index
        + 1 : settings_section_end_index  # settings_section_end_index is exclusive
    ]

    return mcm_settings, settings_section_start_index, settings_section_end_index


if __name__ == "__main__":
    main()
