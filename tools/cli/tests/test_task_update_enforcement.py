"""Tests for task update enforcement requiring Trello sync."""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
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
    (paircoder_dir / "plans").mkdir()
    (paircoder_dir / "history").mkdir()
    return paircoder_dir


class TestTaskUpdateEnforcement:
    """Tests for task update enforcement when Trello is linked."""

    def test_task_update_done_blocks_with_trello_card(self, runner, mock_paircoder_dir):
        """task update --status done must block if Trello card linked."""
        # Create a task file with trello_card_id in frontmatter
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: in_progress
trello_card_id: "TRELLO-94"
---

# Objective
Test task
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import task_app
            result = runner.invoke(task_app, ['update', 'T27.1', '--status', 'done'])

        assert result.exit_code == 1
        assert "BLOCKED" in result.output
        assert "TRELLO-94" in result.output

    def test_task_update_done_allows_local_only_with_reason(self, runner, mock_paircoder_dir):
        """task update --local-only --reason should allow bypass."""
        # Create a task file with trello_card_id
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: in_progress
trello_card_id: "TRELLO-94"
---

# Objective
Test task
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.planning.commands._check_state_md_updated', return_value={"updated": True}):
            from bpsai_pair.planning.commands import task_app
            result = runner.invoke(task_app, [
                'update', 'T27.1', '--status', 'done',
                '--local-only', '--reason', 'Card already completed manually'
            ])

        assert result.exit_code == 0
        # Verify bypass was logged
        bypass_log = mock_paircoder_dir / "history" / "bypass_log.jsonl"
        assert bypass_log.exists()
        log_content = bypass_log.read_text()
        assert "task update --local-only" in log_content
        assert "T27.1" in log_content

    def test_task_update_done_requires_reason_with_local_only(self, runner, mock_paircoder_dir):
        """--local-only without --reason must fail."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: in_progress
---

# Objective
Test task
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import task_app
            result = runner.invoke(task_app, [
                'update', 'T27.1', '--status', 'done', '--local-only'
            ])

        assert result.exit_code == 1
        assert "--reason" in result.output

    def test_task_update_done_blocks_when_trello_enabled(self, runner, mock_paircoder_dir):
        """task update --status done blocks if Trello enabled even without linked card."""
        # Create config with Trello enabled
        config_file = mock_paircoder_dir / "config.yaml"
        config_file.write_text("""
trello:
  enabled: true
  board_id: "abc123"
""")

        # Create a task file without trello_card_id
        task_file = mock_paircoder_dir / "tasks" / "T27.2.task.md"
        task_file.write_text("""---
id: T27.2
title: Test task without card
plan: test-plan
status: in_progress
---

# Objective
Test task
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import task_app
            result = runner.invoke(task_app, ['update', 'T27.2', '--status', 'done'])

        assert result.exit_code == 1
        assert "BLOCKED" in result.output
        assert "Trello" in result.output

    def test_task_update_non_done_status_allowed(self, runner, mock_paircoder_dir):
        """task update with non-done status should work normally."""
        # Create a task file with trello_card_id
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
trello_card_id: "TRELLO-94"
---

# Objective
Test task
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import task_app
            result = runner.invoke(task_app, ['update', 'T27.1', '--status', 'in_progress'])

        # Should succeed (status != done doesn't trigger enforcement)
        assert result.exit_code == 0


class TestGetLinkedTrelloCard:
    """Tests for the _get_linked_trello_card helper function."""

    def test_get_linked_card_from_trello_card_id(self, mock_paircoder_dir):
        """Should extract card ID from trello_card_id field."""
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
trello_card_id: "TRELLO-94"
---
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import _get_linked_trello_card
            card_id = _get_linked_trello_card("T27.1")

        assert card_id == "TRELLO-94"

    def test_get_linked_card_from_trello_url(self, mock_paircoder_dir):
        """Should extract card ID from trello_url field."""
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
trello_url: "https://trello.com/c/ABC123/1-task-name"
---
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import _get_linked_trello_card
            card_id = _get_linked_trello_card("T27.1")

        assert card_id == "ABC123"

    def test_get_linked_card_no_trello_link(self, mock_paircoder_dir):
        """Should return None if no Trello link exists."""
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
---
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import _get_linked_trello_card
            card_id = _get_linked_trello_card("T27.1")

        assert card_id is None

    def test_get_linked_card_numeric_id(self, mock_paircoder_dir):
        """Should format numeric card ID as TRELLO-XXX."""
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
trello_card_id: 94
---
""")

        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import _get_linked_trello_card
            card_id = _get_linked_trello_card("T27.1")

        assert card_id == "TRELLO-94"

    def test_get_linked_card_task_not_found(self, mock_paircoder_dir):
        """Should return None if task doesn't exist."""
        with patch('bpsai_pair.planning.commands.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.planning.commands import _get_linked_trello_card
            card_id = _get_linked_trello_card("NONEXISTENT")

        assert card_id is None
