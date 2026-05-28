"""Unit tests for source management modules."""
import unittest
import tempfile
import shutil
import time
from pathlib import Path

from scraper.source_manager import SourceGroupManager, SourceCategory
from scraper.monitor import SourceMonitor, SourceStatus
from scraper.priority_manager import DynamicPriorityManager, PriorityConfig


class TestSourceGroupManager(unittest.TestCase):
    """Test SourceGroupManager class."""
    
    def setUp(self):
        """Create a simple source groups config."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_groups.json"
        
        self.test_config = {
            "categories": {
                "test_cat1": {
                    "name": "Test Category 1",
                    "enabled": True,
                    "sources": ["source1", "source2", "source3"],
                },
                "test_cat2": {
                    "name": "Test Category 2",
                    "enabled": True,
                    "sources": ["source4", "source5"],
                },
                "disabled_cat": {
                    "name": "Disabled Category",
                    "enabled": False,
                    "sources": ["source6"],
                },
            },
        }
        
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Test loading configuration."""
        manager = SourceGroupManager(str(self.config_file))
        
        self.assertEqual(len(manager.categories), 3)
        self.assertIn("test_cat1", manager.categories)
        self.assertIn("test_cat2", manager.categories)
    
    def test_get_all_sources(self):
        """Test getting all sources."""
        manager = SourceGroupManager(str(self.config_file))
        
        sources = manager.get_all_sources()
        
        self.assertIn("source1", sources)
        self.assertIn("source2", sources)
        self.assertIn("source3", sources)
        self.assertIn("source4", sources)
        self.assertIn("source5", sources)
    
    def test_get_sources_by_category(self):
        """Test getting sources by category."""
        manager = SourceGroupManager(str(self.config_file))
        
        cat1_sources = manager.get_sources_by_category("test_cat1")
        cat2_sources = manager.get_sources_by_category("test_cat2")
        
        self.assertEqual(len(cat1_sources), 3)
        self.assertEqual(len(cat2_sources), 2)
        self.assertIn("source1", cat1_sources)
        self.assertIn("source4", cat2_sources)
    
    def test_disabled_category(self):
        """Test that disabled category sources are excluded."""
        manager = SourceGroupManager(str(self.config_file))
        
        sources = manager.get_all_sources()
        
        self.assertNotIn("source6", sources)
    
    def test_enable_disable_category(self):
        """Test enabling and disabling categories."""
        manager = SourceGroupManager(str(self.config_file))
        
        manager.disable_category("test_cat1")
        self.assertFalse(manager.categories["test_cat1"].enabled)
        
        manager.enable_category("test_cat1")
        self.assertTrue(manager.categories["test_cat1"].enabled)
    
    def test_search_sources(self):
        """Test searching sources."""
        manager = SourceGroupManager(str(self.config_file))
        
        results = manager.search_sources("source")
        self.assertEqual(len(results), 5)
        
        results = manager.search_sources("nonexistent")
        self.assertEqual(len(results), 0)


class TestSourceMonitor(unittest.TestCase):
    """Test SourceMonitor class."""
    
    def test_record_request(self):
        """Test recording a request."""
        monitor = SourceMonitor()
        
        monitor.record_request("test_source", True, 1.5, 85.0)
        
        self.assertIn("test_source", monitor.statuses)
        status = monitor.statuses["test_source"]
        self.assertEqual(status.total_requests, 1)
        self.assertEqual(status.successful_requests, 1)
        self.assertEqual(status.success_rate, 1.0)
    
    def test_get_health_report(self):
        """Test getting health report."""
        monitor = SourceMonitor()
        
        monitor.record_request("healthy_source", True, 1.0, 90.0)
        monitor.record_request("healthy_source", True, 1.5, 85.0)
        
        report = monitor.get_health_report()
        
        self.assertIn("healthy", report)
        self.assertIn("total_sources", report)
    
    def test_get_healthy_sources(self):
        """Test getting healthy sources."""
        monitor = SourceMonitor()
        
        # Need at least 5 successful requests to be marked as healthy
        for i in range(5):
            monitor.record_request("good", True, 1.0, 90.0)
        
        # Check status directly
        status = monitor.get_status("good")
        self.assertTrue(status is not None)
        self.assertTrue(status.success_rate >= 0.8)


class TestPriorityManager(unittest.TestCase):
    """Test DynamicPriorityManager class."""
    
    def test_set_base_priority(self):
        """Test setting base priority."""
        manager = DynamicPriorityManager()
        
        manager.set_base_priority("test_source", 90)
        
        self.assertEqual(manager.get_priority("test_source"), 90)
    
    def test_adjust_priority(self):
        """Test adjusting priority."""
        manager = DynamicPriorityManager()
        
        manager.set_base_priority("test_source", 50)
        
        old, new = manager.adjust_priority(
            "test_source", 0.95, 1.0, 90.0, 0.9
        )
        
        self.assertIsNotNone(new)
    
    def test_get_priority_order(self):
        """Test getting priority order."""
        manager = DynamicPriorityManager()
        
        manager.set_base_priority("source_high", 90)
        manager.set_base_priority("source_medium", 50)
        manager.set_base_priority("source_low", 10)
        
        ordered = manager.get_priority_order(["source_low", "source_high", "source_medium"])
        
        self.assertEqual(ordered[0], "source_high")
        self.assertEqual(ordered[1], "source_medium")
        self.assertEqual(ordered[2], "source_low")
    
    def test_export_import(self):
        """Test exporting and importing priorities."""
        manager = DynamicPriorityManager()
        
        manager.set_base_priority("source1", 90)
        manager.set_base_priority("source2", 80)
        
        exported = manager.export_priorities()
        
        new_manager = DynamicPriorityManager()
        new_manager.import_priorities(exported)
        
        self.assertEqual(new_manager.get_priority("source1"), 90)
        self.assertEqual(new_manager.get_priority("source2"), 80)


if __name__ == "__main__":
    unittest.main()
