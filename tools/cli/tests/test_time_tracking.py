"""Tests for time tracking integration."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bpsai_pair.integrations.time_tracking import (
    TimerEntry,
    TimeTrackingConfig,
    TimeTrackingManager,
    LocalTimeCache,
    NullProvider,
)


class TestTimerEntry:
    """Tests for TimerEntry dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        entry = TimerEntry(
            id="timer-123",
            task_id="TASK-001",
            description="Working on feature",
            start=datetime(2025, 1, 15, 10, 0, 0),
            end=datetime(2025, 1, 15, 11, 30, 0),
            duration=timedelta(hours=1, minutes=30),
        )

        d = entry.to_dict()

        assert d["id"] == "timer-123"
        assert d["task_id"] == "TASK-001"
        assert d["duration_seconds"] == 5400

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": "timer-123",
            "task_id": "TASK-001",
            "description": "Working",
            "start": "2025-01-15T10:00:00",
            "end": "2025-01-15T11:30:00",
            "duration_seconds": 5400,
        }

        entry = TimerEntry.from_dict(data)

        assert entry.id == "timer-123"
        assert entry.task_id == "TASK-001"
        assert entry.duration.total_seconds() == 5400


class TestTimeTrackingConfig:
    """Tests for TimeTrackingConfig."""

    def test_defaults(self):
        """Test default configuration values."""
        config = TimeTrackingConfig()

        assert config.provider == "none"
        assert config.auto_start is True
        assert config.auto_stop is True
        assert config.task_pattern == "{task_id}: {task_title}"


class TestLocalTimeCache:
    """Tests for LocalTimeCache."""

    def test_add_and_get_entry(self):
        """Test adding and retrieving entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            cache = LocalTimeCache(cache_path)

            entry = TimerEntry(
                id="timer-1",
                task_id="TASK-001",
                description="Test",
                start=datetime.now(),
                duration=timedelta(hours=1),
            )

            cache.add_entry("TASK-001", entry)

            entries = cache.get_entries("TASK-001")
            assert len(entries) == 1
            assert entries[0].id == "timer-1"

    def test_get_total(self):
        """Test total time calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            cache = LocalTimeCache(cache_path)

            # Add multiple entries
            for i in range(3):
                entry = TimerEntry(
                    id=f"timer-{i}",
                    task_id="TASK-001",
                    description="Test",
                    start=datetime.now(),
                    duration=timedelta(hours=1),
                )
                cache.add_entry("TASK-001", entry)

            total = cache.get_total("TASK-001")
            assert total.total_seconds() == 3 * 3600

    def test_active_timer(self):
        """Test active timer tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            cache = LocalTimeCache(cache_path)

            cache.set_active_timer("TASK-001", "timer-123")

            active = cache.get_active_timer()
            assert active["task_id"] == "TASK-001"
            assert active["timer_id"] == "timer-123"

            cache.clear_active_timer()
            assert cache.get_active_timer() is None

    def test_persistence(self):
        """Test that cache persists to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"

            # Add entry
            cache1 = LocalTimeCache(cache_path)
            entry = TimerEntry(
                id="timer-1",
                task_id="TASK-001",
                description="Test",
                start=datetime.now(),
                duration=timedelta(hours=1),
            )
            cache1.add_entry("TASK-001", entry)

            # Load in new cache instance
            cache2 = LocalTimeCache(cache_path)
            entries = cache2.get_entries("TASK-001")

            assert len(entries) == 1

    def test_get_all_tasks(self):
        """Test getting all task IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            cache = LocalTimeCache(cache_path)

            for task_id in ["TASK-001", "TASK-002", "TASK-003"]:
                entry = TimerEntry(
                    id=f"timer-{task_id}",
                    task_id=task_id,
                    description="Test",
                    start=datetime.now(),
                    duration=timedelta(minutes=30),
                )
                cache.add_entry(task_id, entry)

            tasks = cache.get_all_tasks()
            assert len(tasks) == 3
            assert "TASK-001" in tasks


class TestNullProvider:
    """Tests for NullProvider (local-only tracking)."""

    def test_start_and_stop(self):
        """Test starting and stopping timer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LocalTimeCache(Path(tmpdir) / "time.json")
            provider = NullProvider(cache)

            # Start timer
            timer_id = provider.start_timer("TASK-001", "Working on feature")
            assert timer_id.startswith("local-")

            # Check current timer
            current = provider.get_current_timer()
            assert current is not None
            assert current.task_id == "TASK-001"

            # Stop timer
            entry = provider.stop_timer(timer_id)
            assert entry.task_id == "TASK-001"
            assert entry.duration is not None
            assert entry.end is not None

            # No active timer after stop
            assert provider.get_current_timer() is None

    def test_get_entries_from_cache(self):
        """Test that entries are retrieved from cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LocalTimeCache(Path(tmpdir) / "time.json")
            provider = NullProvider(cache)

            # Start and stop to create entry
            timer_id = provider.start_timer("TASK-001", "Test")
            provider.stop_timer(timer_id)

            entries = provider.get_entries("TASK-001")
            assert len(entries) == 1

    def test_get_total(self):
        """Test total time calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LocalTimeCache(Path(tmpdir) / "time.json")
            provider = NullProvider(cache)

            # Create a few entries
            for _ in range(2):
                timer_id = provider.start_timer("TASK-001", "Test")
                # Simulate passage of time by directly setting duration
                import time
                time.sleep(0.01)  # Small delay
                provider.stop_timer(timer_id)

            total = provider.get_total("TASK-001")
            assert total.total_seconds() > 0


class TestTimeTrackingManager:
    """Tests for TimeTrackingManager."""

    def test_creates_null_provider_by_default(self):
        """Test that manager creates NullProvider when no config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            config = TimeTrackingConfig(provider="none")
            manager = TimeTrackingManager(config, cache_path)

            assert isinstance(manager.provider, NullProvider)

    def test_start_task_with_auto_start(self):
        """Test auto-start of timer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            config = TimeTrackingConfig(auto_start=True)
            manager = TimeTrackingManager(config, cache_path)

            timer_id = manager.start_task("TASK-001", "Test Task")

            assert timer_id is not None
            assert manager.get_status() is not None

    def test_start_task_without_auto_start(self):
        """Test that auto-start can be disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "time.json"
            config = TimeTrackingConfig(auto_start=False)
            manager = TimeTrackingManager(config, cache_path)

            timer_id = manager.start_task("TASK-001", "Test Task")

            assert timer_id is None

    def test_format_duration(self):
        """Test duration formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TimeTrackingManager(
                TimeTrackingConfig(),
                Path(tmpdir) / "time.json"
            )

            assert manager.format_duration(timedelta(minutes=30)) == "30m"
            assert manager.format_duration(timedelta(hours=1, minutes=30)) == "1h 30m"
            assert manager.format_duration(timedelta(hours=2)) == "2h 0m"

    def test_task_pattern_formatting(self):
        """Test task description pattern formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TimeTrackingConfig(
                task_pattern="{task_id} - {task_title}",
                auto_start=True,
            )
            manager = TimeTrackingManager(config, Path(tmpdir) / "time.json")

            manager.start_task("TASK-001", "My Feature")

            current = manager.get_status()
            assert current.description == "TASK-001 - My Feature"
