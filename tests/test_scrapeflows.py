"""
测试刮削源配置
"""
import unittest
import json
from pathlib import Path


class TestScrapeflows(unittest.TestCase):
    """Test scrapeflow configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.scrapeflows_dir = (
            Path(__file__).resolve().parent.parent / "scrapeflows"
        )

    def test_scrapeflow_dir_exists(self):
        """Test scrapeflow directory exists."""
        self.assertTrue(self.scrapeflows_dir.exists())
        self.assertTrue(self.scrapeflows_dir.is_dir())

    def test_all_files_valid_json(self):
        """Test all JSON files are valid."""
        invalid_files = []
        
        for json_file in self.scrapeflows_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid_files.append(json_file.name)
        
        self.assertEqual(len(invalid_files), 0, 
                         f"Invalid JSON files: {', '.join(invalid_files)}")

    def test_required_fields_present(self):
        """Test required fields are present."""
        required_fields = ["type", "site", "steps"]
        
        for json_file in self.scrapeflows_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for field in required_fields:
                self.assertIn(
                    field,
                    data,
                    f"{json_file.name} missing required field: {field}"
                )

    def test_video_type_is_valid(self):
        """Test video type is valid."""
        valid_types = ["movie", "tvshow", "tvshow_episode"]
        
        for json_file in self.scrapeflows_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            type_name = data["type"]
            is_valid = False
            for valid_type in valid_types:
                if type_name.startswith(valid_type):
                    is_valid = True
                    break
            
            self.assertTrue(is_valid, f"{json_file.name}: Invalid type {type_name}")

    def test_steps_is_list(self):
        """Test steps is a list."""
        for json_file in self.scrapeflows_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.assertIsInstance(data["steps"], list, f"{json_file.name}: steps not a list")


if __name__ == "__main__":
    unittest.main()
