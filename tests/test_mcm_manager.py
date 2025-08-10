import unittest
import tempfile
import os
from typing import Any
import sys
from unittest.mock import patch

# Add the parent directory to Python path to import axr_options
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import mcm_manager


class TestAxrOptions(unittest.TestCase):
    def setUp(self):
        self.EIGHT_SPACES = " " * 8

        """Set up test data based on real axr_options.ltx structure"""
        self.sample_default_axr_content = [
            "[character_creation]\n",
            "        new_game_azazel_mode             =\n",
            "        new_game_campfire_mode           =\n",
            "        new_game_difficulty              = normal\n",
            " \n",
            "[global_keybinds]\n",
            "        debug_demo_record                = DIK_NUMPAD0\n",
            " \n",
            "[mcm]\n",
            "        21_game/card_game_21_minimum_rate = 500\n",
            "        21_game/value_card_21_max_rate   = 1500\n",
            "        3d_scopes/chromatism             = true\n",
            "        3d_scopes/nvg_blur               = false\n",
            "        3d_scopes/parallax_shadow        = true\n",
            "        EA_settings/ea_debug             = false\n",
            "        EA_settings/enable_animations    = true\n",
            "        SMR/smr_amain/smr_enabled        = true\n",
            " \n",
            "[modded_exes]\n",
            "        some_exe_setting                 = value\n",
        ]

        self.sample_user_axr_content = [
            "[character_creation]\n",
            "        new_game_azazel_mode             =\n",
            "        new_game_campfire_mode           =\n",
            "        new_game_difficulty              = normal\n",
            " \n",
            "[global_keybinds]\n",
            "        debug_demo_record                = DIK_NUMPAD0\n",
            " \n",
            "[mcm]\n",
            "        21_game/card_game_21_minimum_rate = 600\n",
            "        21_game/value_card_21_max_rate   = 1600\n",
            "        3d_scopes/chromatism             = true\n",
            "        3d_scopes/nvg_blur               = false\n",
            "        3d_scopes/parallax_shadow        = false\n",
            "        EA_settings/ea_debug             = false\n",
            "        EA_settings/enable_animations    = true\n",
            "        SMR/smr_amain/smr_enabled        = false\n",
            " \n",
            "[modded_exes]\n",
            "        some_exe_setting                 = value\n",
        ]

        self.sample_settings: dict[str, Any] = {
            "3d_scopes/chromatism": False,
            "3d_scopes/nvg_blur": True,
            "new_setting/test": 123,
            "another_setting": "string_value",
        }

    def test_get_settings_section_mcm(self):
        """Test extracting MCM section from axr file"""
        mcm_settings, start_idx, end_idx = mcm_manager.get_settings_section(
            self.sample_default_axr_content, "[mcm]\n"
        )

        self.assertEqual(start_idx, 8)  # Index of [mcm] line
        self.assertEqual(end_idx, 17)  # Index before [modded_exes] or at empty new line
        self.assertEqual(len(mcm_settings), 8)  # 8 settings, no empty line
        self.assertIn("        21_game/card_game_21_minimum_rate = 500\n", mcm_settings)
        self.assertIn("        SMR/smr_amain/smr_enabled        = true\n", mcm_settings)

    def test_get_settings_section_not_found(self):
        """Test error when section doesn't exist"""
        with self.assertRaises(ValueError):
            mcm_manager.get_settings_section(self.sample_default_axr_content, "[nonexistent]\n")

    def test_get_settings_section_at_end(self):
        """Test extracting section when it's at the end of file"""
        content_at_end = self.sample_default_axr_content[:17]  # Remove [modded_exes] section

        _, start_idx, end_idx = mcm_manager.get_settings_section(
            content_at_end, "[mcm]\n"
        )

        # When MCM is at the end, end_idx should be the length of content
        self.assertEqual(start_idx, 8)  # Index of [mcm] line
        self.assertEqual(end_idx, len(content_at_end))

    def test_merge_settings_update_existing(self):
        """Test updating existing settings in MCM section"""
        settings = {"3d_scopes/chromatism": False, "EA_settings/ea_debug": True}

        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        # Check that existing settings were updated
        mcm_section: list[str] = []
        in_mcm = False
        for line in result:
            if line.strip() == "[mcm]":
                in_mcm = True
                continue
            elif (line.strip().startswith("[") and in_mcm) or (
                line.strip(" ") == "\n" and in_mcm
            ):
                break
            elif in_mcm:
                mcm_section.append(line)

        # Find the updated lines
        chromatism_line = next(
            (line for line in mcm_section if "3d_scopes/chromatism" in line), None
        )
        ea_debug_line = next(
            (line for line in mcm_section if "EA_settings/ea_debug" in line), None
        )

        self.assertIsNotNone(chromatism_line)
        self.assertIsNotNone(ea_debug_line)
        self.assertIn("= false", chromatism_line or "")
        self.assertIn("= true", ea_debug_line or "")

    def test_merge_settings_add_new(self):
        """Test adding new settings to MCM section"""
        settings: dict[str, Any] = {
            "new_setting/test": 123,
            "another_setting": "string_value",
        }

        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        self.assertIn(f"{self.EIGHT_SPACES}new_setting/test = 123\n", result)
        self.assertIn(f"{self.EIGHT_SPACES}another_setting = string_value\n", result)

    def test_merge_settings_boolean_formatting(self):
        """Test that boolean values are formatted as lowercase strings"""
        settings = {"test_true": True, "test_false": False}

        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        self.assertIn(f"{self.EIGHT_SPACES}test_true = true\n", result)
        self.assertIn(f"{self.EIGHT_SPACES}test_false = false\n", result)

    def test_merge_settings_proper_indentation(self):
        """Test that settings are properly indented with 8 spaces"""
        settings = {"new_setting": "value"}
        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        # Check that the new setting has proper indentation
        self.assertIn(f"{self.EIGHT_SPACES}new_setting = value\n", result)

    def test_merge_settings_sorting(self):
        """Test that MCM settings are sorted alphabetically"""
        settings = {"z_last_setting": "value", "a_first_setting": "value"}

        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        # Extract MCM section
        mcm_start = None
        mcm_end = None
        for i, line in enumerate(result):
            if line.strip() == "[mcm]":
                mcm_start = i + 1
            elif (line.strip().startswith("[") and mcm_start is not None) or (
                line.strip(" ") == "\n" and mcm_start is not None
            ):
                mcm_end = i
                break

        if mcm_start is None:
            self.fail("Can't find MCM section in test data.")

        if mcm_end is None:
            mcm_end = len(result)

        mcm_section = result[mcm_start:mcm_end]

        # Remove empty lines and check sorting
        settings_lines = [line for line in mcm_section if line.strip() and "=" in line]
        setting_names = [line.strip().split("=")[0].strip() for line in settings_lines]

        self.assertEqual(setting_names, sorted(setting_names))

    def test_merge_settings_no_mcm_section(self):
        """Test handling when no MCM section exists"""
        content_no_mcm = [
            "[character_creation]\n",
            f"{self.EIGHT_SPACES}setting = value\n",
        ]

        result = mcm_manager.merge_settings(content_no_mcm, {"test": "value"})

        # Should return default content unchanged
        self.assertEqual(result, content_no_mcm)

    def test_print_settings_and_default_file_diff_no_diff(self):
        """Test diff function when all settings exist in default"""
        settings: dict[str, Any] = {
            "21_game/card_game_21_minimum_rate": 1000,
            "3d_scopes/chromatism": False,
        }

        with patch("builtins.print") as mock_print:
            mcm_manager.print_settings_and_default_file_diff(
                self.sample_default_axr_content, settings
            )

            # Should not print anything since all settings exist
            mock_print.assert_not_called()

    def test_print_settings_and_default_file_diff_with_diff(self):
        """Test diff function when some settings don't exist in default"""
        settings: dict[str, Any] = {
            "21_game/card_game_21_minimum_rate": 1000,  # Should exist
            "nonexistent_setting": "value",  # Shouldn't exist
            "another_new_setting": 123,  # Shouldn't exist
        }

        with patch("builtins.print") as mock_print:
            mcm_manager.print_settings_and_default_file_diff(
                self.sample_default_axr_content, settings
            )

            # Should print the diff
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            diff_output = "".join(calls)
            self.assertIn("nonexistent_setting = value", diff_output)
            self.assertIn("another_new_setting = 123", diff_output)

    def test_print_settings_and_default_file_diff_no_mcm(self):
        """Test diff function when no MCM section exists"""
        content_no_mcm = ["[character_creation]\n", "        setting = value\n"]

        with patch("builtins.print") as mock_print:
            mcm_manager.print_settings_and_default_file_diff(
                content_no_mcm, {"test": "value"}
            )

            # Should print error message about failed MCM extraction
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            error_output = "".join(calls)
            self.assertIn("Could not calculate settings diff", error_output)

    def test_make_file_backup(self):
        """Test file backup creation"""
        test_content = ["line1\n", "line2\n", "line3\n"]

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            mcm_manager.make_file_backup(test_content, temp_path)

            # Read back the file and verify content
            with open(temp_path, "r") as f:
                backup_content = f.readlines()

            self.assertEqual(backup_content, test_content)
        finally:
            os.unlink(temp_path)

    def test_edge_case_empty_setting_name(self):
        """Test handling of lines without proper setting format"""
        malformed_content = [
            "[mcm]\n",
            "        proper_setting = value\n",
            "        = no_name\n",  # Invalid line
            "        no_equals_sign\n",  # Invalid line
            "        \n",  # Empty line
        ]

        settings = {"new_setting": "value"}
        result = mcm_manager.merge_settings(malformed_content, settings)

        # Should handle malformed lines gracefully
        self.assertIsInstance(result, list)
        self.assertIn(f"{self.EIGHT_SPACES}new_setting = value\n", result)

    def test_numeric_and_float_values(self):
        """Test handling of numeric and float values"""
        settings: dict[str, Any] = {
            "integer_setting": 42,
            "float_setting": 3.14159,
            "zero_setting": 0,
        }

        result = mcm_manager.merge_settings(self.sample_default_axr_content, settings)

        self.assertIn(f"{self.EIGHT_SPACES}integer_setting = 42\n", result)
        self.assertIn(f"{self.EIGHT_SPACES}float_setting = 3.14159\n", result)
        self.assertIn(f"{self.EIGHT_SPACES}zero_setting = 0\n", result)

    def test_create_json_file_from_user_and_default_settings_diff(self):
        """Test creating JSON file with differences between user ltx file and default settings ltx file"""
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mcm_manager.create_json_file_from_user_and_default_settings_diff(
                self.sample_default_axr_content,
                self.sample_user_axr_content,
                temp_dir
            )
            
            json_file_path = os.path.join(temp_dir, "generated_users_settings.json")
            self.assertTrue(os.path.exists(json_file_path))
            
            with open(json_file_path, 'r') as f:
                result = json.load(f)
            
            # Expected differences based on sample data:
            # - 21_game/card_game_21_minimum_rate: 500 -> 600
            # - 21_game/value_card_21_max_rate: 1500 -> 1600  
            # - 3d_scopes/parallax_shadow: true -> false
            # - SMR/smr_amain/smr_enabled: true -> false
            expected = {
                "21_game/card_game_21_minimum_rate": "600",
                "21_game/value_card_21_max_rate": "1600",
                "3d_scopes/parallax_shadow": "false",
                "SMR/smr_amain/smr_enabled": "false"
            }
            
            self.assertEqual(result, expected)

    def test_create_json_file_identical_settings(self):
        """Test creating JSON file when user and default settings are identical"""
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mcm_manager.create_json_file_from_user_and_default_settings_diff(
                self.sample_default_axr_content,
                self.sample_default_axr_content,  # Use same file to emulate identical user file and default
                temp_dir
            )
            
            json_file_path = os.path.join(temp_dir, "generated_users_settings.json")
            self.assertTrue(os.path.exists(json_file_path))
            
            with open(json_file_path, 'r') as f:
                result = json.load(f)
            
            # Should be empty since no differences
            self.assertEqual(result, {})

    def test_create_json_file_user_has_new_settings(self):
        """Test creating JSON file when user has settings not in default"""
        import json
        
        user_content_with_new_settings = self.sample_user_axr_content.copy()
        _, mcm_section_start_index, _ = mcm_manager.get_settings_section(user_content_with_new_settings, "[mcm]\n")
    
        user_content_with_new_settings.insert(mcm_section_start_index + 1, f"{self.EIGHT_SPACES}new_user_setting1 = custom_value\n")
        user_content_with_new_settings.insert(mcm_section_start_index + 1, f"{self.EIGHT_SPACES}new_user_setting2 = another_value\n")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mcm_manager.create_json_file_from_user_and_default_settings_diff(
                self.sample_default_axr_content,
                user_content_with_new_settings,
                temp_dir
            )
            
            json_file_path = os.path.join(temp_dir, "generated_users_settings.json")
            
            with open(json_file_path, 'r') as f:
                result = json.load(f)
            
            # Should include both changed settings and new settings
            self.assertIn("new_user_setting1", result)
            self.assertIn("new_user_setting2", result)
            self.assertEqual(result["new_user_setting1"], "custom_value")
            self.assertEqual(result["new_user_setting2"], "another_value")

if __name__ == "__main__":
    unittest.main(verbosity=2)
