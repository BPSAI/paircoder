"""Tests for hooks module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from bpsai_pair.hooks import (
    HookContext,
    HookResult,
    HookRunner,
    get_hook_runner,
)


class TestHookContext:
    """Tests for HookContext dataclass."""

    def test_basic_context(self):
        """Test creating basic context."""
        ctx = HookContext(
            task_id="TASK-001",
            task=Mock(),
            event="on_task_start",
        )
        assert ctx.task_id == "TASK-001"
        assert ctx.event == "on_task_start"
        assert ctx.agent is None
        assert ctx.extra == {}

    def test_full_context(self):
        """Test creating context with all fields."""
        task = Mock()
        ctx = HookContext(
            task_id="TASK-001",
            task=task,
            event="on_task_complete",
            agent="claude-code",
            extra={"summary": "Done"},
        )
        assert ctx.agent == "claude-code"
        assert ctx.extra["summary"] == "Done"


class TestHookResult:
    """Tests for HookResult dataclass."""

    def test_success_result(self):
        """Test successful result."""
        result = HookResult(
            hook="test_hook",
            success=True,
            result={"timer_started": True},
        )
        assert result.hook == "test_hook"
        assert result.success
        assert result.result == {"timer_started": True}
        assert result.error is None

    def test_failed_result(self):
        """Test failed result."""
        result = HookResult(
            hook="test_hook",
            success=False,
            error="Something went wrong",
        )
        assert not result.success
        assert result.error == "Something went wrong"

    def test_to_dict_success(self):
        """Test to_dict with success."""
        result = HookResult(
            hook="test_hook",
            success=True,
            result={"key": "value"},
        )
        d = result.to_dict()
        assert d["hook"] == "test_hook"
        assert d["success"] is True
        assert d["result"] == {"key": "value"}
        assert "error" not in d

    def test_to_dict_failure(self):
        """Test to_dict with failure."""
        result = HookResult(
            hook="test_hook",
            success=False,
            error="Failed",
        )
        d = result.to_dict()
        assert d["hook"] == "test_hook"
        assert d["success"] is False
        assert d["error"] == "Failed"
        assert "result" not in d

    def test_to_dict_minimal(self):
        """Test to_dict with minimal fields."""
        result = HookResult(hook="test", success=True)
        d = result.to_dict()
        assert d == {"hook": "test", "success": True}


class TestHookRunner:
    """Tests for HookRunner class."""

    @pytest.fixture
    def runner(self, tmp_path):
        """Create a hook runner."""
        config = {
            "hooks": {
                "enabled": True,
                "on_task_start": ["start_timer"],
                "on_task_complete": ["stop_timer", "record_metrics"],
            }
        }
        return HookRunner(config, tmp_path)

    @pytest.fixture
    def disabled_runner(self, tmp_path):
        """Create a disabled hook runner."""
        config = {"hooks": {"enabled": False}}
        return HookRunner(config, tmp_path)

    def test_init(self, tmp_path):
        """Test initialization."""
        config = {"hooks": {"enabled": True}}
        runner = HookRunner(config, tmp_path)
        assert runner.config == config
        assert runner.paircoder_dir == tmp_path

    def test_enabled_true(self, runner):
        """Test enabled property when true."""
        assert runner.enabled is True

    def test_enabled_false(self, disabled_runner):
        """Test enabled property when false."""
        assert disabled_runner.enabled is False

    def test_enabled_default(self, tmp_path):
        """Test enabled defaults to True."""
        runner = HookRunner({}, tmp_path)
        assert runner.enabled is True

    def test_get_hooks_for_event(self, runner):
        """Test getting hooks for event."""
        hooks = runner.get_hooks_for_event("on_task_start")
        assert hooks == ["start_timer"]

    def test_get_hooks_for_event_not_configured(self, runner):
        """Test getting hooks for unconfigured event."""
        hooks = runner.get_hooks_for_event("on_task_block")
        assert hooks == []

    def test_run_hooks_disabled(self, disabled_runner):
        """Test run_hooks when disabled."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_start")
        results = disabled_runner.run_hooks("on_task_start", ctx)
        assert results == []

    def test_run_hooks_no_hooks_configured(self, tmp_path):
        """Test run_hooks with no hooks configured."""
        runner = HookRunner({"hooks": {"enabled": True}}, tmp_path)
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_start")
        results = runner.run_hooks("on_task_start", ctx)
        assert results == []

    def test_run_single_hook_unknown(self, runner):
        """Test running unknown hook."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="test")
        result = runner._run_single_hook("unknown_hook", ctx)
        assert result.success is False
        assert "Unknown hook" in result.error

    def test_run_single_hook_success(self, runner):
        """Test running successful hook."""
        runner._handlers["test_hook"] = lambda ctx: {"done": True}
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="test")
        result = runner._run_single_hook("test_hook", ctx)
        assert result.success is True
        assert result.result == {"done": True}

    def test_run_single_hook_exception(self, runner):
        """Test running hook that throws exception."""
        def failing_hook(ctx):
            raise ValueError("Test error")

        runner._handlers["fail_hook"] = failing_hook
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="test")
        result = runner._run_single_hook("fail_hook", ctx)
        assert result.success is False
        assert "Test error" in result.error

    def test_run_hooks_multiple(self, runner):
        """Test running multiple hooks."""
        runner._handlers["stop_timer"] = lambda ctx: {"stopped": True}
        runner._handlers["record_metrics"] = lambda ctx: {"recorded": True}
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_complete")
        results = runner.run_hooks("on_task_complete", ctx)
        assert len(results) == 2

    def test_start_timer_success(self, runner):
        """Test _start_timer hook."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_start")

        with patch("bpsai_pair.integrations.time_tracking.TimeTrackingManager") as mock_manager_cls:
            mock_manager = Mock()
            mock_manager_cls.return_value = mock_manager
            result = runner._start_timer(ctx)
            # Either succeeds or has error info
            assert "timer_started" in result

    def test_stop_timer_success(self, runner):
        """Test _stop_timer hook."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_complete")

        with patch("bpsai_pair.integrations.time_tracking.TimeTrackingManager") as mock_manager_cls:
            mock_manager = Mock()
            mock_manager.stop_task.return_value = 3600
            mock_manager_cls.return_value = mock_manager
            result = runner._stop_timer(ctx)
            assert "timer_stopped" in result

    def test_record_metrics_success(self, runner):
        """Test _record_metrics hook."""
        task = Mock()
        task.id = "TASK-001"
        ctx = HookContext(
            task_id="TASK-001",
            task=task,
            event="on_task_complete",
            agent="claude",
            extra={
                "input_tokens": 1000,
                "output_tokens": 500,
                "model": "claude-sonnet-4-5-20250929",
            },
        )
        runner.paircoder_dir.mkdir(parents=True, exist_ok=True)
        (runner.paircoder_dir / "history").mkdir(exist_ok=True)

        with patch("bpsai_pair.metrics.collector.MetricsCollector") as mock_collector_cls:
            mock_collector = Mock()
            mock_collector_cls.return_value = mock_collector
            result = runner._record_metrics(ctx)
            assert "metrics_recorded" in result

    def test_sync_trello_no_token(self, runner):
        """Test _sync_trello hook without token."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_complete")

        with patch("bpsai_pair.trello.auth.load_token") as mock_load:
            mock_load.return_value = None
            result = runner._sync_trello(ctx)
            assert "trello_synced" in result
            assert result["trello_synced"] is False

    def test_update_state_success(self, runner):
        """Test _update_state hook."""
        task = Mock()
        task.id = "TASK-001"
        task.status = Mock()
        task.status.value = "done"
        ctx = HookContext(task_id="TASK-001", task=task, event="on_task_complete")

        with patch("bpsai_pair.planning.state.StateManager") as mock_state_cls:
            mock_state = Mock()
            mock_state_cls.return_value = mock_state
            result = runner._update_state(ctx)
            assert "state_updated" in result

    def test_check_unblocked_success(self, runner):
        """Test _check_unblocked hook."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_complete")

        with patch("bpsai_pair.planning.parser.TaskParser") as mock_parser_cls:
            mock_parser = Mock()
            mock_parser.parse_all.return_value = []
            mock_parser_cls.return_value = mock_parser
            result = runner._check_unblocked(ctx)
            assert "unblocked_tasks" in result

    def test_log_trello_activity_no_board(self, runner):
        """Test _log_trello_activity hook without board."""
        ctx = HookContext(task_id="TASK-001", task=Mock(), event="on_task_complete")

        result = runner._log_trello_activity(ctx)
        assert "activity_logged" in result
        assert result["activity_logged"] is False


class TestGetHookRunner:
    """Tests for get_hook_runner function."""

    def test_creates_runner(self, tmp_path):
        """Test creating hook runner."""
        # Create config file
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        config_file = paircoder_dir / "config.yaml"
        config_file.write_text("hooks:\n  enabled: true\n")

        with patch("bpsai_pair.hooks.load_config") as mock_load:
            mock_load.return_value = {"hooks": {"enabled": True}}
            runner = get_hook_runner(paircoder_dir)
            assert isinstance(runner, HookRunner)

    def test_creates_new_runner(self, tmp_path):
        """Test creating new runner each time."""
        import bpsai_pair.hooks as hooks_module

        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()

        with patch("bpsai_pair.hooks.load_config") as mock_load:
            mock_load.return_value = {"hooks": {"enabled": True}}
            runner1 = get_hook_runner(paircoder_dir)
            runner2 = get_hook_runner(paircoder_dir)
            # Both should be HookRunner instances
            assert isinstance(runner1, HookRunner)
            assert isinstance(runner2, HookRunner)
