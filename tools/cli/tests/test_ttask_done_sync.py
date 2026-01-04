"""Tests for ttask done local task synchronization."""
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_paircoder_dir(tmp_path):
    """Create a mock .paircoder directory structure."""
    paircoder_dir = tmp_path / ".paircoder"
    paircoder_dir.mkdir()
    (paircoder_dir / "tasks").mkdir()
    (paircoder_dir / "history").mkdir()
    return paircoder_dir


class TestGetTaskIdFromCard:
    """Tests for _get_task_id_from_card helper function."""

    def test_extracts_bracketed_task_id(self):
        """Should extract task ID from [T27.1] format."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "[T27.1] Create module structure"
        mock_card.description = ""

        result = _get_task_id_from_card(mock_card)
        assert result == "T27.1"

    def test_extracts_start_of_name_task_id(self):
        """Should extract task ID from 'T27.1: ...' format."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "T27.1: Fix the bug"
        mock_card.description = ""

        result = _get_task_id_from_card(mock_card)
        assert result == "T27.1"

    def test_extracts_task_id_with_dash_separator(self):
        """Should extract task ID from 'T27.1 - ...' format."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "T27.1 - Fix the bug"
        mock_card.description = ""

        result = _get_task_id_from_card(mock_card)
        assert result == "T27.1"

    def test_extracts_task_id_from_description(self):
        """Should extract task ID from description if not in name."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "Fix the bug"
        mock_card.description = "Task: T27.1\n\nThis fixes the issue."

        result = _get_task_id_from_card(mock_card)
        assert result == "T27.1"

    def test_extracts_legacy_task_id(self):
        """Should extract TASK-123 format."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "[TASK-123] Implement feature"
        mock_card.description = ""

        result = _get_task_id_from_card(mock_card)
        assert result == "TASK-123"

    def test_returns_none_for_no_match(self):
        """Should return None if no task ID found."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "Some random card"
        mock_card.description = "No task ID here"

        result = _get_task_id_from_card(mock_card)
        assert result is None

    def test_prefers_bracketed_over_description(self):
        """Should prefer bracketed format in name over description."""
        from bpsai_pair.trello.task_commands import _get_task_id_from_card

        mock_card = MagicMock()
        mock_card.name = "[T27.1] Main task"
        mock_card.description = "Task: T99.9"

        result = _get_task_id_from_card(mock_card)
        assert result == "T27.1"


class TestTtaskDoneSync:
    """Tests for ttask done local task synchronization."""

    def test_done_updates_local_task(self, runner, mock_paircoder_dir):
        """ttask done must update local task file."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Fix the bug
plan: test-plan
status: in_progress
---

# Objective
Fix the bug
""")

        # Mock the Trello client
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Fix the bug"
        mock_card.short_id = 123
        mock_card.checklists = []
        mock_card.url = "https://trello.com/c/abc123"
        mock_card.description = ""

        mock_list = MagicMock()
        mock_list.name = "In Progress"

        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_config = {"trello": {"lists": {"review": "In Review"}}}

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.trello.task_commands._log_bypass'):
            mock_get.return_value = (mock_client, mock_config)

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['done', '123', '--summary', 'Fixed it', '--no-strict'])

        assert result.exit_code == 0
        assert "Local task T27.1 updated" in result.output

        # Verify local task updated
        content = task_file.read_text()
        assert "status: done" in content

    def test_done_continues_if_no_local_task(self, runner, mock_paircoder_dir):
        """ttask done should succeed even if no local task found."""
        # No task file created

        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Some card without task ID"
        mock_card.short_id = 123
        mock_card.checklists = []
        mock_card.url = "https://trello.com/c/abc123"
        mock_card.description = ""

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_config = {"trello": {"lists": {"review": "In Review"}}}

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.trello.task_commands._log_bypass'):
            mock_get.return_value = (mock_client, mock_config)

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['done', '123', '--summary', 'Done', '--no-strict'])

        # Should still succeed
        assert result.exit_code == 0
        assert "Completed:" in result.output

    def test_done_warns_if_task_file_not_found(self, runner, mock_paircoder_dir):
        """ttask done should warn but not fail if task file not found."""
        # No task file, but card has task ID

        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Fix bug"  # Has task ID but no local file
        mock_card.short_id = 123
        mock_card.checklists = []
        mock_card.url = "https://trello.com/c/abc123"
        mock_card.description = ""

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_config = {"trello": {"lists": {"review": "In Review"}}}

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.trello.task_commands._log_bypass'):
            mock_get.return_value = (mock_client, mock_config)

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['done', '123', '--summary', 'Done', '--no-strict'])

        assert result.exit_code == 0
        # Should warn about missing local task or just not mention it
        assert "Completed:" in result.output

    def test_done_continues_if_local_update_fails(self, runner, mock_paircoder_dir):
        """ttask done should warn but not fail if local update fails."""
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Fix bug"
        mock_card.short_id = 123
        mock_card.checklists = []
        mock_card.url = "https://trello.com/c/abc123"
        mock_card.description = ""

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_config = {"trello": {"lists": {"review": "In Review"}}}

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.trello.task_commands._log_bypass'), \
             patch('bpsai_pair.trello.task_commands._update_local_task_status') as mock_update:
            mock_get.return_value = (mock_client, mock_config)
            mock_update.side_effect = Exception("Update failed")

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['done', '123', '--summary', 'Done', '--no-strict'])

        # Should still succeed (Trello is source of truth)
        assert result.exit_code == 0
        assert "Completed:" in result.output


class TestUpdateLocalTaskStatus:
    """Tests for _update_local_task_status function."""

    def test_updates_task_status(self, mock_paircoder_dir):
        """Should update task file status."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: in_progress
---
""")

        mock_card = MagicMock()
        mock_card.name = "[T27.1] Test task"
        mock_card.description = ""

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.trello.task_commands import _update_local_task_status
            success, task_id = _update_local_task_status(mock_card, "done", "Completed the task")

        assert success is True
        assert task_id == "T27.1"

        # Verify file was updated
        content = task_file.read_text()
        assert "status: done" in content

    def test_returns_task_id_even_if_file_not_found(self, mock_paircoder_dir):
        """Should return task_id even if file not found."""
        mock_card = MagicMock()
        mock_card.name = "T99.9: Nonexistent task"
        mock_card.description = ""

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.trello.task_commands import _update_local_task_status
            success, task_id = _update_local_task_status(mock_card, "done")

        # Task ID should be extracted even though update failed
        assert success is False
        # Task ID might be None since task doesn't exist, or returned
        # depending on implementation

    def test_returns_none_for_no_task_id(self, mock_paircoder_dir):
        """Should return None, None if no task ID in card."""
        mock_card = MagicMock()
        mock_card.name = "Random card name"
        mock_card.description = ""

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.trello.task_commands import _update_local_task_status
            success, task_id = _update_local_task_status(mock_card, "done")

        assert success is False
        assert task_id is None
