"""
测试工具函数
"""
import unittest
import time

from scraper.utils import (
    strftime,
    dict_update,
    strip,
    re_sub,
    str_to_etree,
    json_to_etree,
    html_to_etree,
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_strftime(self):
        """Test strftime function."""
        timestamp = time.time()
        result = strftime(timestamp, "%Y-%m-%d")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")

    def test_dict_update(self):
        """Test dict_update function."""
        d1 = {"a": 1, "b": [1, 2]}
        d2 = {"b": [2, 3], "c": 3}
        
        result = dict_update(d1, d2)
        
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["c"], 3)
        # 合并列表，去重
        self.assertEqual(sorted(result["b"]), [1, 2, 3])

    def test_strip(self):
        """Test strip function."""
        test_str = "  Hello World!  "
        self.assertEqual(strip(test_str), "Hello World!")
        
        test_list = ["  a  ", None, "  b  "]
        self.assertEqual(strip(test_list), ["a", "b"])
        
        test_dict = {"  key  ": "  value  ", "n": 123}
        stripped = strip(test_dict)
        self.assertEqual(stripped["  key  "], "value")
        self.assertEqual(stripped["n"], 123)

    def test_re_sub(self):
        """Test re_sub function."""
        test_str = "Hello 123 World"
        self.assertEqual(re_sub(test_str, r"\d+", "XXX"), "Hello XXX World")
        
        test_list = ["123", "456"]
        self.assertEqual(re_sub(test_list, r"\d+", "X"), ["X", "X"])
        
        test_dict = {"a": "123", "b": "456"}
        self.assertEqual(re_sub(test_dict, r"\d+", "X"), {"a": "X", "b": "X"})

    def test_json_to_etree(self):
        """Test json_to_etree function."""
        test_obj = {"name": "test", "value": 123}
        result = json_to_etree(test_obj)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.tag, "root")
        
        children = list(result)
        self.assertEqual(len(children), 2)

    def test_html_to_etree(self):
        """Test html_to_etree function."""
        test_html = "<html><body><p>Hello</p></body></html>"
        result = html_to_etree(test_html)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.tag, "html")

    def test_str_to_etree(self):
        """Test str_to_etree function."""
        # 测试 JSON 字符串
        test_json = '{"name": "test"}'
        result_json = str_to_etree(test_json)
        self.assertIsNotNone(result_json)
        
        # 测试 HTML 字符串
        test_html = "<p>test</p>"
        result_html = str_to_etree(test_html)
        self.assertIsNotNone(result_html)
        
        # 测试无效字符串
        result_none = str_to_etree("invalid")
        self.assertIsNone(result_none)


if __name__ == "__main__":
    unittest.main()
