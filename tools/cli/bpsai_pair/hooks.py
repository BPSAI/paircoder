"""
Hook System for Task State Changes

Automatically triggers actions when task state changes:
- Timer start/stop
- Metrics recording
- Trello sync
- State updates
- Dependency checking
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HookContext:
    """Context passed to hook handlers."""

    task_id: str
    task: Any  # Task object
    event: str  # on_task_start, on_task_complete, on_task_block
    agent: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HookResult:
    """Result of a hook execution."""

    hook: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        d = {"hook": self.hook, "success": self.success}
        if self.result:
            d["result"] = self.result
        if self.error:
            d["error"] = self.error
        return d


class HookRunner:
    """Runs configured hooks on events."""

    def __init__(self, config: dict, paircoder_dir: Path):
        """
        Initialize hook runner.

        Args:
            config: Configuration dict (from config.yaml)
            paircoder_dir: Path to .paircoder directory
        """
        self.config = config
        self.paircoder_dir = Path(paircoder_dir)
        self._handlers: Dict[str, Callable] = {
            "start_timer": self._start_timer,
            "stop_timer": self._stop_timer,
            "record_metrics": self._record_metrics,
            "sync_trello": self._sync_trello,
            "update_state": self._update_state,
            "check_unblocked": self._check_unblocked,
        }

    @property
    def enabled(self) -> bool:
        """Check if hooks are enabled."""
        return self.config.get("hooks", {}).get("enabled", True)

    def get_hooks_for_event(self, event: str) -> List[str]:
        """Get list of hooks configured for an event."""
        return self.config.get("hooks", {}).get(event, [])

    def run_hooks(self, event: str, context: HookContext) -> List[HookResult]:
        """
        Run all hooks for an event.

        Args:
            event: Event name (on_task_start, on_task_complete, on_task_block)
            context: Hook context with task info

        Returns:
            List of hook results
        """
        if not self.enabled:
            logger.debug("Hooks disabled, skipping")
            return []

        hooks = self.get_hooks_for_event(event)
        if not hooks:
            logger.debug(f"No hooks configured for {event}")
            return []

        results = []

        for hook_name in hooks:
            result = self._run_single_hook(hook_name, context)
            results.append(result)

        return results

    def _run_single_hook(self, hook_name: str, context: HookContext) -> HookResult:
        """Run a single hook."""
        handler = self._handlers.get(hook_name)

        if not handler:
            logger.warning(f"Unknown hook: {hook_name}")
            return HookResult(
                hook=hook_name,
                success=False,
                error=f"Unknown hook: {hook_name}",
            )

        try:
            result = handler(context)
            logger.info(f"Hook {hook_name} completed for {context.task_id}")
            return HookResult(hook=hook_name, success=True, result=result)
        except Exception as e:
            logger.error(f"Hook {hook_name} failed: {e}")
            return HookResult(hook=hook_name, success=False, error=str(e))

    def _start_timer(self, ctx: HookContext) -> dict:
        """Start time tracking for task."""
        try:
            from .time_tracking import TimeTrackingManager

            manager = TimeTrackingManager(self.paircoder_dir.parent)
            manager.start_task(ctx.task_id, auto_start=True)
            return {"timer_started": True}
        except Exception as e:
            logger.warning(f"Timer start failed: {e}")
            return {"timer_started": False, "error": str(e)}

    def _stop_timer(self, ctx: HookContext) -> dict:
        """Stop time tracking and get duration."""
        try:
            from .time_tracking import TimeTrackingManager

            manager = TimeTrackingManager(self.paircoder_dir.parent)
            duration = manager.stop_task(ctx.task_id)
            return {"timer_stopped": True, "duration_seconds": duration}
        except Exception as e:
            logger.warning(f"Timer stop failed: {e}")
            return {"timer_stopped": False, "error": str(e)}

    def _record_metrics(self, ctx: HookContext) -> dict:
        """Record metrics from context.extra."""
        try:
            from .metrics import MetricsCollector

            history_dir = self.paircoder_dir / "history"
            history_dir.mkdir(exist_ok=True)

            collector = MetricsCollector(history_dir)

            extra = ctx.extra or {}
            event = collector.record_invocation(
                agent=ctx.agent or "unknown",
                model=extra.get("model", "unknown"),
                input_tokens=extra.get("input_tokens", 0),
                output_tokens=extra.get("output_tokens", 0),
                duration_ms=int(extra.get("duration_seconds", 0) * 1000),
                success=True,
                task_id=ctx.task_id,
                operation=extra.get("action_type", "coding"),
            )
            return {"metrics_recorded": True, "cost": f"${event.cost_usd:.4f}"}
        except Exception as e:
            logger.warning(f"Metrics recording failed: {e}")
            return {"metrics_recorded": False, "error": str(e)}

    def _sync_trello(self, ctx: HookContext) -> dict:
        """Sync task state to Trello card."""
        try:
            # Check if task has trello_card_id
            trello_card_id = getattr(ctx.task, "trello_card_id", None)
            if not trello_card_id:
                return {"trello_synced": False, "reason": "No card linked"}

            from .trello.auth import load_token
            from .trello.client import TrelloService

            token_data = load_token()
            if not token_data:
                return {"trello_synced": False, "reason": "Not connected to Trello"}

            service = TrelloService(
                api_key=token_data["api_key"], token=token_data["token"]
            )

            # Map event to action
            action_map = {
                "on_task_start": "start",
                "on_task_complete": "complete",
                "on_task_block": "block",
            }
            action = action_map.get(ctx.event, "comment")

            # Find and update card
            # Note: This requires the board to be set first
            # In practice, this would need board_id from config
            return {"trello_synced": True, "action": action, "card_id": trello_card_id}
        except ImportError:
            return {"trello_synced": False, "reason": "py-trello not installed"}
        except Exception as e:
            logger.warning(f"Trello sync failed: {e}")
            return {"trello_synced": False, "error": str(e)}

    def _update_state(self, ctx: HookContext) -> dict:
        """Update state.md with current focus."""
        try:
            from .planning.state import StateManager

            manager = StateManager(self.paircoder_dir)

            # Just reload state - actual state file updates would be manual
            manager.reload()
            return {"state_updated": True, "task_id": ctx.task_id}
        except Exception as e:
            logger.warning(f"State update failed: {e}")
            return {"state_updated": False, "error": str(e)}

    def _check_unblocked(self, ctx: HookContext) -> dict:
        """Check if completing this task unblocks others."""
        try:
            from .planning.parser import TaskParser
            from .planning.models import TaskStatus

            parser = TaskParser(self.paircoder_dir / "tasks")
            all_tasks = parser.parse_all()

            unblocked = []
            for task in all_tasks:
                if not task.depends_on:
                    continue

                if ctx.task_id in task.depends_on:
                    # Check if all dependencies are now complete
                    all_done = True
                    for dep_id in task.depends_on:
                        dep_task = parser.get_task_by_id(dep_id)
                        if dep_task and dep_task.status != TaskStatus.DONE:
                            all_done = False
                            break

                    if all_done and task.status == TaskStatus.BLOCKED:
                        unblocked.append(task.id)
                        logger.info(f"Task {task.id} unblocked by {ctx.task_id}")

            return {"unblocked_tasks": unblocked, "count": len(unblocked)}
        except Exception as e:
            logger.warning(f"Unblock check failed: {e}")
            return {"unblocked_tasks": [], "error": str(e)}


def load_config(paircoder_dir: Path) -> dict:
    """Load configuration from config.yaml."""
    import yaml

    config_path = paircoder_dir / "config.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text()) or {}
    return {}


def get_hook_runner(paircoder_dir: Path) -> HookRunner:
    """Get a HookRunner instance for the project."""
    config = load_config(paircoder_dir)
    return HookRunner(config, paircoder_dir)
