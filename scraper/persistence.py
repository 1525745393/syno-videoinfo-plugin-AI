"""
Persistence layer for source management system.
Provides storage for source states, metrics, and history.
"""
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SourceState:
    """Persistable source state."""
    source: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    total_quality: float = 0.0
    last_request: Optional[float] = None
    first_request: Optional[float] = None
    enabled: bool = True
    priority: int = 50
    category: str = "unknown"
    tags: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def avg_duration(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_duration / self.successful_requests

    @property
    def avg_quality(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_quality / self.successful_requests

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SourceState':
        return cls(**data)


@dataclass
class HistoryRecord:
    """History record for a scrape attempt."""
    source: str
    timestamp: float
    success: bool
    duration: float
    quality: float = 0.0
    number: str = ""
    title: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryRecord':
        return cls(**data)


class PersistentStorage:
    """Persistent storage for source management system."""

    def __init__(self, storage_dir: str = "source_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.states_file = self.storage_dir / "source_states.json"
        self.history_file = self.storage_dir / "history.json"
        self.settings_file = self.storage_dir / "settings.json"

        self._lock = threading.Lock()

        # Load or initialize data
        self.states: Dict[str, SourceState] = self._load_states()
        self.history: List[HistoryRecord] = self._load_history()
        self.settings: Dict[str, Any] = self._load_settings()

        logger.info(f"Persistent storage initialized at: {self.storage_dir}")

    def _load_states(self) -> Dict[str, SourceState]:
        """Load source states from file."""
        if not self.states_file.exists():
            return {}

        try:
            with open(self.states_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                states = {}
                for source, state_data in data.items():
                    states[source] = SourceState.from_dict(state_data)
                return states
        except Exception as e:
            logger.warning(f"Failed to load states: {e}")
            return {}

    def _save_states(self):
        """Save source states to file."""
        try:
            data = {
                source: state.to_dict()
                for source, state in self.states.items()
            }
            with open(self.states_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save states: {e}")

    def _load_history(self) -> List[HistoryRecord]:
        """Load history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [HistoryRecord.from_dict(record) for record in data]
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
            return []

    def _save_history(self):
        """Save history to file."""
        try:
            # Keep only last 10,000 records
            records = self.history[-10000:]
            data = [record.to_dict() for record in records]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if not self.settings_file.exists():
            return {
                "version": "1.0",
                "auto_save": True,
                "auto_save_interval": 300,  # 5 minutes
                "history_retention_days": 30
            }

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
            return {}

    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def save(self):
        """Save all data to disk."""
        with self._lock:
            self._save_states()
            self._save_history()
            self._save_settings()

    def record_scrape(self, source: str, success: bool, duration: float,
                     quality: float = 0.0, number: str = "", title: str = ""):
        """Record a scrape attempt."""
        with self._lock:
            timestamp = time.time()

            # Update state
            if source not in self.states:
                self.states[source] = SourceState(
                    source=source,
                    first_request=timestamp
                )

            state = self.states[source]
            state.total_requests += 1
            state.last_request = timestamp

            if success:
                state.successful_requests += 1
                state.total_duration += duration
                state.total_quality += quality

            # Add to history
            record = HistoryRecord(
                source=source,
                timestamp=timestamp,
                success=success,
                duration=duration,
                quality=quality,
                number=number,
                title=title
            )
            self.history.append(record)

            # Auto save if enabled
            if self.settings.get("auto_save", True):
                self._save_states()
                self._save_history()

    def get_state(self, source: str) -> Optional[SourceState]:
        """Get a source's state."""
        return self.states.get(source)

    def get_all_states(self) -> Dict[str, SourceState]:
        """Get all source states."""
        return dict(self.states)

    def update_state(self, source: str, **kwargs):
        """Update a source's state."""
        with self._lock:
            if source not in self.states:
                self.states[source] = SourceState(source=source)

            state = self.states[source]
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)

            self._save_states()

    def get_history(self, source: Optional[str] = None,
                   limit: int = 100,
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None) -> List[HistoryRecord]:
        """Get history records."""
        records = self.history

        if source:
            records = [r for r in records if r.source == source]

        if start_time:
            records = [r for r in records if r.timestamp >= start_time]

        if end_time:
            records = [r for r in records if r.timestamp <= end_time]

        return records[-limit:]

    def get_statistics(self, source: Optional[str] = None,
                      hours: int = 24) -> Dict[str, Any]:
        """Get statistics."""
        cutoff = time.time() - (hours * 3600)

        records = self.get_history(source=source, start_time=cutoff)

        if not records:
            return {
                "total_requests": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "avg_quality": 0.0
            }

        total = len(records)
        successful = sum(1 for r in records if r.success)
        failed = total - successful

        success_rate = successful / total if total > 0 else 0.0
        avg_duration = sum(r.duration for r in records if r.success) / successful if successful > 0 else 0
        avg_quality = sum(r.quality for r in records if r.success) / successful if successful > 0 else 0

        return {
            "total_requests": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "avg_quality": avg_quality,
            "period_hours": hours
        }

    def export_data(self, export_dir: str):
        """Export all data to specified directory."""
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)

        # Copy files
        if self.states_file.exists():
            with open(self.states_file, 'r', encoding='utf-8') as f:
                with open(export_path / "source_states.json", 'w', encoding='utf-8') as out:
                    out.write(f.read())

        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                with open(export_path / "history.json", 'w', encoding='utf-8') as out:
                    out.write(f.read())

        logger.info(f"Data exported to: {export_dir}")

    def clear_old_history(self, days: int = 30):
        """Clear old history records."""
        cutoff = time.time() - (days * 24 * 3600)
        self.history = [r for r in self.history if r.timestamp >= cutoff]
        self._save_history()

    def reset_source(self, source: str):
        """Reset a source's state."""
        with self._lock:
            if source in self.states:
                del self.states[source]
            self._save_states()

    def reset_all(self):
        """Reset all data."""
        with self._lock:
            self.states = {}
            self.history = []
            self._save_states()
            self._save_history()


# Global instance
_storage: Optional[PersistentStorage] = None


def get_storage() -> PersistentStorage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = PersistentStorage()
    return _storage


def init_storage(storage_dir: str = "source_data") -> PersistentStorage:
    """Initialize the storage."""
    global _storage
    _storage = PersistentStorage(storage_dir)
    return _storage
