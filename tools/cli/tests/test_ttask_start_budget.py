"""Tests for ttask start budget enforcement."""
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
    (paircoder_dir / "metrics").mkdir()
    (paircoder_dir / "history").mkdir()
    return paircoder_dir


class TestCheckTaskBudget:
    """Tests for _check_task_budget helper function."""

    def test_returns_true_when_within_budget(self, mock_paircoder_dir):
        """Should return True when task is within budget."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 30
type: feature
---
""")

        # Mock the budget enforcer to allow
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (True, "OK")
        mock_enforcer.check_budget.return_value = MagicMock(
            daily_remaining=8.0,
            daily_limit=10.0
        )

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'):
            from bpsai_pair.trello.task_commands import _check_task_budget
            result = _check_task_budget("T27.1", "TRELLO-123", budget_override=False)

        assert result is True

    def test_returns_false_when_over_budget(self, mock_paircoder_dir):
        """Should return False when task would exceed budget."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 80
type: feature
---
""")

        # Mock the budget enforcer to deny
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (False, "Would exceed daily limit")
        mock_enforcer.check_budget.return_value = MagicMock(
            daily_remaining=0.50,
            daily_limit=10.0
        )

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'):
            from bpsai_pair.trello.task_commands import _check_task_budget
            result = _check_task_budget("T27.1", "TRELLO-123", budget_override=False)

        assert result is False

    def test_returns_true_with_override(self, mock_paircoder_dir):
        """Should return True when budget_override is True despite exceeding budget."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 80
type: feature
---
""")

        # Mock the budget enforcer to deny
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (False, "Would exceed daily limit")

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'), \
             patch('bpsai_pair.trello.task_commands._log_bypass') as mock_log:
            from bpsai_pair.trello.task_commands import _check_task_budget
            result = _check_task_budget("T27.1", "TRELLO-123", budget_override=True)

        assert result is True
        mock_log.assert_called_once()
        assert "budget_override" in mock_log.call_args[0][0]

    def test_returns_true_when_task_not_found(self, mock_paircoder_dir):
        """Should return True (skip check) when task doesn't exist."""
        # No task file created

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir):
            from bpsai_pair.trello.task_commands import _check_task_budget
            result = _check_task_budget("NONEXISTENT", "TRELLO-123", budget_override=False)

        assert result is True

    def test_returns_true_when_budget_module_unavailable(self, mock_paircoder_dir):
        """Should return True (skip check) when budget module not available."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
---
""")

        with patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', side_effect=ImportError("No budget")):
            from bpsai_pair.trello.task_commands import _check_task_budget
            result = _check_task_budget("T27.1", "TRELLO-123", budget_override=False)

        assert result is True


class TestTtaskStartBudget:
    """Tests for ttask start with budget enforcement."""

    def test_start_blocks_over_budget(self, runner, mock_paircoder_dir):
        """ttask start must block when task exceeds budget."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 80
type: feature
---
""")

        # Mock Trello client
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Test task"
        mock_card.short_id = 123
        mock_card.description = ""

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_client.is_card_blocked.return_value = False

        # Mock budget to deny
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (False, "Would exceed daily limit")
        mock_enforcer.check_budget.return_value = MagicMock(
            daily_remaining=0.50,
            daily_limit=10.0
        )

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'):
            mock_get.return_value = (mock_client, {"trello": {"lists": {}}})

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['start', '123'])

        assert result.exit_code == 1
        assert "BLOCKED" in result.output
        assert "budget" in result.output.lower()

    def test_start_allows_under_budget(self, runner, mock_paircoder_dir):
        """ttask start must allow when under budget."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 30
type: feature
---
""")

        # Mock Trello client
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Test task"
        mock_card.short_id = 123
        mock_card.description = ""
        mock_card.url = "https://trello.com/c/abc"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_client.is_card_blocked.return_value = False

        # Mock budget to allow
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (True, "OK")

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'):
            mock_get.return_value = (mock_client, {"trello": {"lists": {"in_progress": "In Progress"}}})

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['start', '123'])

        assert result.exit_code == 0
        assert "Started:" in result.output

    def test_budget_override_allows_with_warning(self, runner, mock_paircoder_dir):
        """--budget-override must allow with warning and log bypass."""
        # Create a task file
        task_file = mock_paircoder_dir / "tasks" / "T27.1.task.md"
        task_file.write_text("""---
id: T27.1
title: Test task
plan: test-plan
status: pending
complexity: 80
type: feature
---
""")

        # Mock Trello client
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "T27.1: Test task"
        mock_card.short_id = 123
        mock_card.description = ""
        mock_card.url = "https://trello.com/c/abc"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_client.is_card_blocked.return_value = False

        # Mock budget to deny
        mock_enforcer = MagicMock()
        mock_enforcer.can_proceed.return_value = (False, "Would exceed limit")

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get, \
             patch('bpsai_pair.core.ops.find_paircoder_dir', return_value=mock_paircoder_dir), \
             patch('bpsai_pair.metrics.budget.BudgetEnforcer', return_value=mock_enforcer), \
             patch('bpsai_pair.metrics.collector.MetricsCollector'), \
             patch('bpsai_pair.trello.task_commands._log_bypass') as mock_log:
            mock_get.return_value = (mock_client, {"trello": {"lists": {"in_progress": "In Progress"}}})

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['start', '123', '--budget-override'])

        assert result.exit_code == 0
        # Should show warning
        assert "warning" in result.output.lower() or "⚠" in result.output
        # Verify bypass logged
        mock_log.assert_called_once()
        assert "budget_override" in mock_log.call_args[0][0]

    def test_start_continues_without_task_id(self, runner, mock_paircoder_dir):
        """ttask start should skip budget check if no task ID found."""
        # Mock Trello client - card without task ID
        mock_client = MagicMock()
        mock_card = MagicMock()
        mock_card.id = "card-123"
        mock_card.name = "Random card name"
        mock_card.short_id = 123
        mock_card.description = ""
        mock_card.url = "https://trello.com/c/abc"

        mock_list = MagicMock()
        mock_client.find_card.return_value = (mock_card, mock_list)
        mock_client.is_card_blocked.return_value = False

        with patch('bpsai_pair.trello.task_commands.get_board_client') as mock_get:
            mock_get.return_value = (mock_client, {"trello": {"lists": {"in_progress": "In Progress"}}})

            from bpsai_pair.trello.task_commands import app
            result = runner.invoke(app, ['start', '123'])

        # Should succeed (no task ID, so no budget check)
        assert result.exit_code == 0
        assert "Started:" in result.output
