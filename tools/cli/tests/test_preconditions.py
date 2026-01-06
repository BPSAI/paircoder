"""Tests for pre-command validation hooks.

Location: tools/cli/tests/core/test_preconditions.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from bpsai_pair.core.preconditions import (
    PreconditionResult,
    CheckResult,
    check_paircoder_project,
    check_trello_connected,
    check_task_exists,
    check_task_status,
    check_git_clean,
    check_has_active_plan,
    check_on_feature_branch,
    run_preconditions,
    make_task_exists_check,
)


class TestCheckResult:
    """Tests for CheckResult dataclass."""
    
    def test_passed_property(self):
        """passed should be True only for PASS status."""
        assert CheckResult(PreconditionResult.PASS, "ok").passed
        assert not CheckResult(PreconditionResult.WARN, "warn").passed
        assert not CheckResult(PreconditionResult.BLOCK, "block").passed
    
    def test_blocked_property(self):
        """blocked should be True only for BLOCK status."""
        assert not CheckResult(PreconditionResult.PASS, "ok").blocked
        assert not CheckResult(PreconditionResult.WARN, "warn").blocked
        assert CheckResult(PreconditionResult.BLOCK, "block").blocked


class TestCheckPaircoderProject:
    """Tests for check_paircoder_project."""
    
    def test_passes_when_project_exists(self, tmp_path):
        """Should pass when .paircoder directory exists."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            result = check_paircoder_project()
        
        assert result.passed
    
    def test_blocks_when_no_project(self):
        """Should block when not in a PairCoder project."""
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=None):
            result = check_paircoder_project()
        
        assert result.blocked
        assert "init" in result.suggestion.lower()


@pytest.mark.skip(reason="TrelloService refactor needed")
class TestCheckTrelloConnected:
    """Tests for check_trello_connected."""
    
    def test_passes_when_connected(self):
        """Should pass when Trello client is available."""
        mock_client = MagicMock()
        mock_config = {"trello": {"enabled": True}}
        
        with patch("bpsai_pair.trello.client.get_board_client", return_value=(mock_client, mock_config)):
            result = check_trello_connected()
        
        assert result.passed
    
    def test_blocks_when_not_connected(self):
        """Should block when Trello not configured."""
        with patch("bpsai_pair.trello.client.get_board_client", side_effect=Exception("Not configured")):
            result = check_trello_connected()
        
        assert result.blocked
        assert "connect" in result.suggestion.lower()


class TestCheckTaskExists:
    """Tests for check_task_exists."""
    
    def test_passes_when_task_found(self, tmp_path):
        """Should pass when task file exists."""
        paircoder_dir = tmp_path / ".paircoder"
        tasks_dir = paircoder_dir / "tasks" / "sprint-28"
        tasks_dir.mkdir(parents=True)
        
        task_file = tasks_dir / "T28.1.task.md"
        task_file.write_text("---\nid: T28.1\n---\n")
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            result = check_task_exists("T28.1")
        
        assert result.passed
    
    def test_blocks_when_task_not_found(self, tmp_path):
        """Should block when task file doesn't exist."""
        paircoder_dir = tmp_path / ".paircoder"
        tasks_dir = paircoder_dir / "tasks"
        tasks_dir.mkdir(parents=True)
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            result = check_task_exists("T99.99")
        
        assert result.blocked


class TestCheckTaskStatus:
    """Tests for check_task_status."""
    
    def test_passes_when_status_matches(self, tmp_path):
        """Should pass when task status matches required."""
        paircoder_dir = tmp_path / ".paircoder"
        tasks_dir = paircoder_dir / "tasks"
        tasks_dir.mkdir(parents=True)
        
        task_file = tasks_dir / "T28.1.task.md"
        task_file.write_text("---\nid: T28.1\nstatus: in_progress\n---\n")
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            result = check_task_status("T28.1", "in_progress")
        
        assert result.passed
    
    def test_blocks_when_status_differs(self, tmp_path):
        """Should block when task status doesn't match."""
        paircoder_dir = tmp_path / ".paircoder"
        tasks_dir = paircoder_dir / "tasks"
        tasks_dir.mkdir(parents=True)
        
        task_file = tasks_dir / "T28.1.task.md"
        task_file.write_text("---\nid: T28.1\nstatus: pending\n---\n")
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            result = check_task_status("T28.1", "in_progress")
        
        assert result.blocked
        assert "pending" in result.message
        assert "in_progress" in result.message


class TestCheckGitClean:
    """Tests for check_git_clean."""
    
    def test_passes_when_clean(self):
        """Should pass when git tree is clean."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch("subprocess.run", return_value=mock_result):
            result = check_git_clean()
        
        assert result.passed
    
    def test_warns_when_dirty(self):
        """Should warn when there are uncommitted changes."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = " M file1.py\n M file2.py"
        
        with patch("subprocess.run", return_value=mock_result):
            result = check_git_clean()
        
        assert result.status == PreconditionResult.WARN
        assert "2 files" in result.message


class TestCheckOnFeatureBranch:
    """Tests for check_on_feature_branch."""
    
    def test_passes_on_feature_branch(self):
        """Should pass when on a feature branch."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "feature/my-feature\n"
        
        with patch("subprocess.run", return_value=mock_result):
            result = check_on_feature_branch()
        
        assert result.passed
    
    def test_warns_on_main(self):
        """Should warn when on main branch."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch("subprocess.run", return_value=mock_result):
            result = check_on_feature_branch()
        
        assert result.status == PreconditionResult.WARN
        assert "protected" in result.message.lower()


class TestRunPreconditions:
    """Tests for run_preconditions."""
    
    def test_returns_true_when_all_pass(self):
        """Should return True when all checks pass."""
        checks = [
            lambda: CheckResult(PreconditionResult.PASS, "check1"),
            lambda: CheckResult(PreconditionResult.PASS, "check2"),
        ]
        
        result = run_preconditions(checks, silent=True)
        assert result is True
    
    def test_returns_false_when_blocked(self):
        """Should return False when any check blocks."""
        checks = [
            lambda: CheckResult(PreconditionResult.PASS, "check1"),
            lambda: CheckResult(PreconditionResult.BLOCK, "check2 failed"),
        ]
        
        result = run_preconditions(checks, silent=True)
        assert result is False
    
    def test_warnings_dont_block_by_default(self):
        """Warnings should not block execution by default."""
        checks = [
            lambda: CheckResult(PreconditionResult.PASS, "check1"),
            lambda: CheckResult(PreconditionResult.WARN, "warning"),
        ]
        
        result = run_preconditions(checks, silent=True)
        assert result is True
    
    def test_warnings_block_when_fail_on_warn(self):
        """Warnings should block when fail_on_warn is True."""
        checks = [
            lambda: CheckResult(PreconditionResult.PASS, "check1"),
            lambda: CheckResult(PreconditionResult.WARN, "warning"),
        ]
        
        result = run_preconditions(checks, fail_on_warn=True, silent=True)
        assert result is False


class TestMakeTaskChecks:
    """Tests for curried check functions."""
    
    def test_make_task_exists_check(self, tmp_path):
        """make_task_exists_check should create callable that checks specific task."""
        paircoder_dir = tmp_path / ".paircoder"
        tasks_dir = paircoder_dir / "tasks"
        tasks_dir.mkdir(parents=True)
        
        task_file = tasks_dir / "T28.5.task.md"
        task_file.write_text("---\nid: T28.5\n---\n")
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=paircoder_dir):
            check_fn = make_task_exists_check("T28.5")
            result = check_fn()
        
        assert result.passed
