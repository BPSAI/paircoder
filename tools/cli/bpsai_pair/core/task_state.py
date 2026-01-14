"""Task execution state machine.

Enforces valid state transitions for tasks.
Prevents skipping steps in the workflow.

Location: tools/cli/bpsai_pair/core/task_state.py
"""
import json
from dataclasses import dataclass
from datetime import datetime, UTC
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


class TaskState(Enum):
    """Valid states for task execution."""
    NOT_STARTED = "not_started"
    BUDGET_CHECKED = "budget_checked"
    IN_PROGRESS = "in_progress"
    AC_VERIFIED = "ac_verified"
    COMPLETED = "completed"
    BLOCKED = "blocked"


# Valid state transitions
# Key = current state, Value = list of valid target states
VALID_TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.NOT_STARTED: [TaskState.BUDGET_CHECKED, TaskState.BLOCKED],
    TaskState.BUDGET_CHECKED: [TaskState.IN_PROGRESS, TaskState.NOT_STARTED, TaskState.BLOCKED],
    TaskState.IN_PROGRESS: [TaskState.AC_VERIFIED, TaskState.BLOCKED],
    TaskState.AC_VERIFIED: [TaskState.COMPLETED, TaskState.IN_PROGRESS],  # Can regress if AC unchecked
    TaskState.COMPLETED: [],  # Terminal state
    TaskState.BLOCKED: [TaskState.NOT_STARTED, TaskState.IN_PROGRESS, TaskState.BUDGET_CHECKED],
}

# Human-readable descriptions for each transition
TRANSITION_TRIGGERS: dict[tuple[TaskState, TaskState], str] = {
    (TaskState.NOT_STARTED, TaskState.BUDGET_CHECKED): "bpsai-pair budget check <task-id>",
    (TaskState.BUDGET_CHECKED, TaskState.IN_PROGRESS): "bpsai-pair ttask start <card-id>",
    (TaskState.IN_PROGRESS, TaskState.AC_VERIFIED): "Check all AC items on Trello card",
    (TaskState.AC_VERIFIED, TaskState.COMPLETED): "bpsai-pair ttask done <card-id>",
    (TaskState.AC_VERIFIED, TaskState.IN_PROGRESS): "Uncheck AC item (work incomplete)",
    (TaskState.BLOCKED, TaskState.NOT_STARTED): "Resolve blocker and reset",
    (TaskState.BLOCKED, TaskState.IN_PROGRESS): "bpsai-pair ttask unblock <card-id>",
}

# Descriptions for skip attempts
SKIP_EXPLANATIONS: dict[tuple[TaskState, TaskState], str] = {
    (TaskState.NOT_STARTED, TaskState.IN_PROGRESS): "Must check budget first",
    (TaskState.NOT_STARTED, TaskState.COMPLETED): "Cannot skip to completion",
    (TaskState.BUDGET_CHECKED, TaskState.COMPLETED): "Must start and verify AC first",
    (TaskState.BUDGET_CHECKED, TaskState.AC_VERIFIED): "Must start task first",
    (TaskState.IN_PROGRESS, TaskState.COMPLETED): "Must verify AC first",
}


class TaskStateManager:
    """Manages task execution states.
    
    Persists state to .paircoder/task_state.json and enforces valid transitions.
    """
    
    def __init__(self, state_file: Optional[Path] = None):
        """Initialize state manager.
        
        Args:
            state_file: Path to state file. Defaults to .paircoder/task_state.json
        """
        if state_file is None:
            from .ops import find_paircoder_dir
            paircoder_dir = find_paircoder_dir() or Path(".paircoder")
            state_file = paircoder_dir / "task_state.json"
        
        self.state_file = state_file
        self._states: dict[str, str] = {}
        self._history: list[dict] = []
        self._load()
    
    def _load(self) -> None:
        """Load state from file."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self._states = data.get("states", {})
                self._history = data.get("history", [])
            except (json.JSONDecodeError, KeyError):
                self._states = {}
                self._history = []
    
    def _save(self) -> None:
        """Save state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "states": self._states,
            "history": self._history[-100:],  # Keep last 100 transitions
            "updated": datetime.now(UTC).isoformat() + "Z",
        }
        self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def get_state(self, task_id: str) -> TaskState:
        """Get current state of a task.
        
        Returns NOT_STARTED for unknown tasks.
        """
        state_str = self._states.get(task_id, "not_started")
        try:
            return TaskState(state_str)
        except ValueError:
            return TaskState.NOT_STARTED
    
    def can_transition(self, task_id: str, target: TaskState) -> tuple[bool, str]:
        """Check if transition is valid.
        
        Args:
            task_id: Task identifier
            target: Desired target state
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        current = self.get_state(task_id)
        valid_targets = VALID_TRANSITIONS.get(current, [])
        
        if target in valid_targets:
            trigger = TRANSITION_TRIGGERS.get((current, target), "")
            return True, f"Valid: {current.value} → {target.value}"
        
        if not valid_targets:
            return False, f"Task is in terminal state '{current.value}'"
        
        # Check for skip attempt explanation
        skip_reason = SKIP_EXPLANATIONS.get((current, target))
        if skip_reason:
            next_state = valid_targets[0]
            trigger = TRANSITION_TRIGGERS.get((current, next_state), "unknown")
            return False, (
                f"{skip_reason}. "
                f"Current: '{current.value}' → Next: '{next_state.value}'. "
                f"Run: {trigger}"
            )
        
        # Generic invalid transition
        next_state = valid_targets[0]
        trigger = TRANSITION_TRIGGERS.get((current, next_state), "unknown")
        return False, (
            f"Invalid transition: '{current.value}' → '{target.value}'. "
            f"Next valid state: '{next_state.value}'. "
            f"Run: {trigger}"
        )
    
    def transition(self, task_id: str, target: TaskState, trigger: str = "") -> None:
        """Transition task to new state.
        
        Args:
            task_id: Task identifier
            target: Target state
            trigger: Description of what triggered this transition
            
        Raises:
            typer.Exit: If transition is invalid
        """
        allowed, reason = self.can_transition(task_id, target)
        
        if not allowed:
            console.print(f"[red]❌ BLOCKED:[/red] {reason}")
            raise typer.Exit(1)
        
        current = self.get_state(task_id)
        
        # Record transition in history
        self._history.append({
            "task_id": task_id,
            "from_state": current.value,
            "to_state": target.value,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "trigger": trigger,
        })
        
        self._states[task_id] = target.value
        self._save()
        
        console.print(f"[green]✓[/green] Task {task_id}: {current.value} → {target.value}")
    
    def require_state(self, task_id: str, required: TaskState) -> None:
        """Verify task is in required state.
        
        Args:
            task_id: Task identifier
            required: Required state
            
        Raises:
            typer.Exit: If not in required state
        """
        current = self.get_state(task_id)
        if current == required:
            return
        
        console.print(
            f"[red]❌ BLOCKED:[/red] Task {task_id} must be in state "
            f"'{required.value}' but is in '{current.value}'"
        )
        
        # Show how to get to required state
        valid_next = VALID_TRANSITIONS.get(current, [])
        if valid_next:
            next_state = valid_next[0]
            trigger = TRANSITION_TRIGGERS.get((current, next_state), "unknown command")
            console.print(f"[dim]   → Next step: {trigger}[/dim]")
        
        raise typer.Exit(1)
    
    def reset_task(self, task_id: str) -> None:
        """Reset task to NOT_STARTED state.
        
        Used for re-doing work or fixing state issues.
        """
        current = self.get_state(task_id)
        
        self._history.append({
            "task_id": task_id,
            "from_state": current.value,
            "to_state": TaskState.NOT_STARTED.value,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "trigger": "manual_reset",
        })
        
        self._states[task_id] = TaskState.NOT_STARTED.value
        self._save()
        
        console.print(f"[yellow]↺[/yellow] Task {task_id} reset to not_started")
    
    def get_history(self, task_id: Optional[str] = None, limit: int = 20) -> list[dict]:
        """Get transition history.
        
        Args:
            task_id: Optional filter by task
            limit: Maximum entries to return
            
        Returns:
            List of transition records, newest first
        """
        history = self._history.copy()
        if task_id:
            history = [h for h in history if h["task_id"] == task_id]
        
        history.reverse()
        return history[:limit]
    
    def get_all_states(self) -> dict[str, str]:
        """Get all tracked task states.
        
        Returns:
            Dict mapping task_id to state
        """
        return self._states.copy()


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_state_manager: Optional[TaskStateManager] = None


def get_state_manager() -> TaskStateManager:
    """Get global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = TaskStateManager()
    return _state_manager


def reset_state_manager() -> None:
    """Reset global state manager (for testing)."""
    global _state_manager
    _state_manager = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_state_machine_enabled() -> bool:
    """Check if state machine enforcement is enabled in config.
    
    Defaults to False until explicitly enabled.
    """
    from .config import load_raw_config
    from .ops import find_paircoder_dir
    
    try:
        paircoder_dir = find_paircoder_dir()
        if not paircoder_dir:
            return False
        config, _ = load_raw_config(paircoder_dir.parent)
        if not config:
            return False
        enforcement = config.get("enforcement", {})
        return enforcement.get("state_machine", False)
    except Exception:
        return False


def ensure_task_state(task_id: str, required: TaskState) -> bool:
    """Check task state, but only if state machine is enabled.
    
    Returns:
        True if state is correct or enforcement disabled
    """
    if not is_state_machine_enabled():
        return True
    
    manager = get_state_manager()
    current = manager.get_state(task_id)
    return current == required
