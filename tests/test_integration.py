"""
集成测试
"""
import unittest
import sys
import os
from pathlib import Path


class TestIntegration(unittest.TestCase):
    """Integration tests for the scraper."""

    def setUp(self):
        """Set up test fixtures."""
        # 添加项目根目录到路径
        self.project_root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(self.project_root))

    def test_import_scraper(self):
        """Test importing the scraper."""
        try:
            from scraper import scrape
            self.assertIsNotNone(scrape)
        except ImportError as e:
            self.fail(f"Failed to import scraper: {e}")

    def test_import_utils(self):
        """Test importing utils."""
        try:
            from scraper import utils
            self.assertIsNotNone(utils)
        except ImportError as e:
            self.fail(f"Failed to import utils: {e}")

    def test_version_module_import(self):
        """Test importing version module."""
        try:
            from version import version
            self.assertIsNotNone(version)
        except ImportError as e:
            self.fail(f"Failed to import version: {e}")


if __name__ == "__main__":
    unittest.main()
