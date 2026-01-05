"""Tests for centralized bypass logging.

Location: tools/cli/tests/core/test_bypass_log.py
"""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch


class TestLogBypass:
    """Tests for log_bypass function."""
    
    def test_creates_log_file_if_missing(self, tmp_path):
        """log_bypass should create log file and parent dirs if missing."""
        log_file = tmp_path / ".paircoder" / "history" / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass
            log_bypass("test_cmd", "T27.1", "test reason", silent=True)
        
        assert log_file.exists()
        assert log_file.parent.exists()
    
    def test_logs_entry_with_all_fields(self, tmp_path):
        """log_bypass should write entry with all required fields."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass
            log_bypass(
                command="ttask_done",
                target="TRELLO-123",
                reason="Testing bypass",
                bypass_type="no_strict",
                metadata={"unchecked": 2},
                silent=True,
            )
        
        # Read and verify
        content = log_file.read_text()
        entry = json.loads(content.strip())
        
        assert entry["command"] == "ttask_done"
        assert entry["target"] == "TRELLO-123"
        assert entry["reason"] == "Testing bypass"
        assert entry["bypass_type"] == "no_strict"
        assert entry["metadata"] == {"unchecked": 2}
        assert "timestamp" in entry
        assert entry["timestamp"].endswith("Z")
    
    def test_appends_to_existing_log(self, tmp_path):
        """log_bypass should append to existing log file."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass
            log_bypass("cmd1", "T1", "reason1", silent=True)
            log_bypass("cmd2", "T2", "reason2", silent=True)
        
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2
        
        entry1 = json.loads(lines[0])
        entry2 = json.loads(lines[1])
        
        assert entry1["command"] == "cmd1"
        assert entry2["command"] == "cmd2"


class TestGetBypasses:
    """Tests for get_bypasses function."""
    
    def test_returns_empty_if_no_file(self, tmp_path):
        """get_bypasses should return empty list if log doesn't exist."""
        log_file = tmp_path / "nonexistent.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import get_bypasses
            result = get_bypasses()
        
        assert result == []
    
    def test_returns_entries_newest_first(self, tmp_path):
        """get_bypasses should return entries newest first."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass, get_bypasses
            log_bypass("cmd1", "T1", "first", silent=True)
            log_bypass("cmd2", "T2", "second", silent=True)
            log_bypass("cmd3", "T3", "third", silent=True)
            
            result = get_bypasses()
        
        assert len(result) == 3
        assert result[0]["command"] == "cmd3"  # Newest first
        assert result[1]["command"] == "cmd2"
        assert result[2]["command"] == "cmd1"
    
    def test_respects_limit(self, tmp_path):
        """get_bypasses should respect limit parameter."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass, get_bypasses
            for i in range(10):
                log_bypass(f"cmd{i}", f"T{i}", f"reason{i}", silent=True)
            
            result = get_bypasses(limit=3)
        
        assert len(result) == 3
    
    def test_filters_by_type(self, tmp_path):
        """get_bypasses should filter by bypass_type."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass, get_bypasses
            log_bypass("cmd1", "T1", "r1", bypass_type="no_strict", silent=True)
            log_bypass("cmd2", "T2", "r2", bypass_type="budget_override", silent=True)
            log_bypass("cmd3", "T3", "r3", bypass_type="no_strict", silent=True)
            
            result = get_bypasses(bypass_type="no_strict")
        
        assert len(result) == 2
        assert all(e["bypass_type"] == "no_strict" for e in result)
    
    def test_handles_malformed_json(self, tmp_path):
        """get_bypasses should skip malformed JSON lines."""
        log_file = tmp_path / "bypass_log.jsonl"
        log_file.write_text('{"command": "good"}\nnot valid json\n{"command": "also_good"}\n')
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import get_bypasses
            result = get_bypasses()
        
        assert len(result) == 2


class TestGetBypassSummary:
    """Tests for get_bypass_summary function."""
    
    def test_returns_counts_by_type(self, tmp_path):
        """get_bypass_summary should count bypasses by type."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass, get_bypass_summary
            log_bypass("cmd1", "T1", "r1", bypass_type="no_strict", silent=True)
            log_bypass("cmd2", "T2", "r2", bypass_type="budget_override", silent=True)
            log_bypass("cmd3", "T3", "r3", bypass_type="no_strict", silent=True)
            
            summary = get_bypass_summary()
        
        assert summary["total"] == 3
        assert summary["by_type"]["no_strict"] == 2
        assert summary["by_type"]["budget_override"] == 1
    
    def test_returns_counts_by_command(self, tmp_path):
        """get_bypass_summary should count bypasses by command."""
        log_file = tmp_path / "bypass_log.jsonl"
        
        with patch("bpsai_pair.core.bypass_log.get_bypass_log_path", return_value=log_file):
            from bpsai_pair.core.bypass_log import log_bypass, get_bypass_summary
            log_bypass("ttask_done", "T1", "r1", silent=True)
            log_bypass("ttask_done", "T2", "r2", silent=True)
            log_bypass("task_update", "T3", "r3", silent=True)
            
            summary = get_bypass_summary()
        
        assert summary["by_command"]["ttask_done"] == 2
        assert summary["by_command"]["task_update"] == 1
