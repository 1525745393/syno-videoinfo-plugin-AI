"""Unit tests for persistence module."""
import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path

from scraper.persistence import PersistentStorage, SourceState, HistoryRecord


class TestSourceState(unittest.TestCase):
    """Test SourceState class."""
    
    def test_create_state(self):
        """Test creating a source state."""
        state = SourceState(
            source="test_source",
            total_requests=10,
            successful_requests=8,
            failed_requests=2,
            total_duration=12.5,
            total_quality=85.0,
            enabled=True,
            priority=90,
        )
        
        self.assertEqual(state.source, "test_source")
        self.assertEqual(state.total_requests, 10)
        self.assertEqual(state.successful_requests, 8)
        self.assertEqual(state.failed_requests, 2)
        self.assertEqual(state.success_rate, 0.8)
        self.assertEqual(state.avg_duration, 1.5625)
        self.assertEqual(state.avg_quality, 10.625)
    
    def test_empty_state(self):
        """Test an empty state."""
        state = SourceState(source="empty_source")
        
        self.assertEqual(state.success_rate, 0.0)
        self.assertEqual(state.avg_duration, 0.0)
        self.assertEqual(state.avg_quality, 0.0)
    
    def test_to_dict(self):
        """Test converting state to dict."""
        state = SourceState(
            source="test_source",
            total_requests=5,
            successful_requests=3,
        )
        
        state_dict = state.to_dict()
        
        self.assertIn("source", state_dict)
        self.assertIn("total_requests", state_dict)
        self.assertIn("successful_requests", state_dict)
    
    def test_from_dict(self):
        """Test creating state from dict."""
        data = {
            "source": "from_dict_source",
            "total_requests": 20,
            "successful_requests": 15,
            "failed_requests": 5,
        }
        
        state = SourceState.from_dict(data)
        
        self.assertEqual(state.source, "from_dict_source")
        self.assertEqual(state.total_requests, 20)
        self.assertEqual(state.successful_requests, 15)
        self.assertEqual(state.failed_requests, 5)


class TestHistoryRecord(unittest.TestCase):
    """Test HistoryRecord class."""
    
    def test_create_record(self):
        """Test creating a history record."""
        record = HistoryRecord(
            source="test_source",
            timestamp=time.time(),
            success=True,
            duration=2.5,
            quality=85.0,
            number="TEST-123",
            title="Test Video",
        )
        
        self.assertEqual(record.source, "test_source")
        self.assertTrue(record.success)
        self.assertEqual(record.duration, 2.5)
        self.assertEqual(record.quality, 85.0)
    
    def test_to_dict(self):
        """Test converting record to dict."""
        record = HistoryRecord(
            source="test_source",
            timestamp=1234567890,
            success=True,
            duration=1.5,
        )
        
        record_dict = record.to_dict()
        
        self.assertEqual(record_dict["source"], "test_source")
        self.assertEqual(record_dict["timestamp"], 1234567890)
        self.assertEqual(record_dict["success"], True)


class TestPersistentStorage(unittest.TestCase):
    """Test PersistentStorage class."""
    
    def setUp(self):
        """Create a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = PersistentStorage(self.temp_dir)
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialize(self):
        """Test storage initialization."""
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertEqual(len(self.storage.states), 0)
        self.assertEqual(len(self.storage.history), 0)
    
    def test_record_scrape_success(self):
        """Test recording a successful scrape."""
        self.storage.record_scrape(
            source="test_source",
            success=True,
            duration=1.5,
            quality=85.0,
            number="TEST-123",
            title="Test Video",
        )
        
        self.assertIn("test_source", self.storage.states)
        state = self.storage.states["test_source"]
        self.assertEqual(state.total_requests, 1)
        self.assertEqual(state.successful_requests, 1)
        self.assertEqual(len(self.storage.history), 1)
    
    def test_record_scrape_failure(self):
        """Test recording a failed scrape."""
        self.storage.record_scrape(
            source="test_source",
            success=False,
            duration=5.0,
            quality=0.0,
        )
        
        self.assertIn("test_source", self.storage.states)
        state = self.storage.states["test_source"]
        self.assertEqual(state.total_requests, 1)
        self.assertEqual(state.successful_requests, 0)
        self.assertEqual(state.failed_requests, 1)
    
    def test_get_state(self):
        """Test getting a source state."""
        self.storage.record_scrape(
            source="get_test",
            success=True,
            duration=1.0,
            quality=90.0,
        )
        
        state = self.storage.get_state("get_test")
        self.assertIsNotNone(state)
        self.assertEqual(state.source, "get_test")
        
        missing_state = self.storage.get_state("missing_source")
        self.assertIsNone(missing_state)
    
    def test_get_all_states(self):
        """Test getting all states."""
        self.storage.record_scrape("source1", True, 1.0)
        self.storage.record_scrape("source2", True, 1.5)
        
        states = self.storage.get_all_states()
        
        self.assertEqual(len(states), 2)
        self.assertIn("source1", states)
        self.assertIn("source2", states)
    
    def test_update_state(self):
        """Test updating a state."""
        self.storage.record_scrape("update_test", True, 1.0)
        self.storage.update_state("update_test", enabled=False, priority=50)
        
        state = self.storage.get_state("update_test")
        self.assertFalse(state.enabled)
        self.assertEqual(state.priority, 50)
    
    def test_get_history(self):
        """Test getting history."""
        self.storage.record_scrape("history_test1", True, 1.0)
        self.storage.record_scrape("history_test2", True, 2.0)
        self.storage.record_scrape("history_test1", False, 3.0)
        
        # Get all history
        history = self.storage.get_history(limit=100)
        self.assertEqual(len(history), 3)
        
        # Filter by source
        source_history = self.storage.get_history(source="history_test1")
        self.assertEqual(len(source_history), 2)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        self.storage.record_scrape("stats_test", True, 1.0, 85.0)
        self.storage.record_scrape("stats_test", True, 1.5, 90.0)
        self.storage.record_scrape("stats_test", False, 2.0, 0.0)
        
        stats = self.storage.get_statistics(source="stats_test")
        
        self.assertEqual(stats["total_requests"], 3)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertGreater(stats["success_rate"], 0.0)
    
    def test_reset_source(self):
        """Test resetting a source."""
        self.storage.record_scrape("reset_test", True, 1.0)
        
        self.storage.reset_source("reset_test")
        
        self.assertNotIn("reset_test", self.storage.states)
    
    def test_save_and_load(self):
        """Test saving and loading data."""
        self.storage.record_scrape("save_test", True, 1.0, 95.0)
        self.storage.save()
        
        # Create new storage instance
        new_storage = PersistentStorage(self.temp_dir)
        
        # Verify data is loaded
        self.assertIn("save_test", new_storage.states)
        self.assertEqual(len(new_storage.history), 1)


if __name__ == "__main__":
    unittest.main()
