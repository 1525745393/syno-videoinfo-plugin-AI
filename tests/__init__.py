# Test for the scraper package
"""
测试模块
"""
import unittest


def suite():
    """Test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover("tests"))
    return suite
