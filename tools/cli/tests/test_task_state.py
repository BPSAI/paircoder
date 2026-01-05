"""Tests for task execution state machine.

Location: tools/cli/tests/core/test_task_state.py
"""
import json
import pytest
from click.exceptions import Exit as ClickExit
from pathlib import Path
from unittest.mock import patch

from bpsai_pair.core.task_state import (
    TaskState,
    TaskStateManager,
    VALID_TRANSITIONS,
    get_state_manager,
    reset_state_manager,
)


@pytest.fixture(autouse=True)
def reset_global_manager():
    """Reset global state manager before each test."""
    reset_state_manager()
    yield
    reset_state_manager()


class TestTaskState:
    """Tests for TaskState enum."""
    
    def test_all_states_have_transitions_defined(self):
        """Every state should have transitions defined."""
        for state in TaskState:
            assert state in VALID_TRANSITIONS
    
    def test_completed_is_terminal(self):
        """COMPLETED should have no valid transitions (terminal)."""
        assert VALID_TRANSITIONS[TaskState.COMPLETED] == []


class TestTaskStateManager:
    """Tests for TaskStateManager."""
    
    def test_initial_state_is_not_started(self, tmp_path):
        """New tasks should start in NOT_STARTED state."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        assert mgr.get_state("T27.1") == TaskState.NOT_STARTED
        assert mgr.get_state("NEW_TASK") == TaskState.NOT_STARTED
    
    def test_valid_transition_allowed(self, tmp_path):
        """Valid transitions should be allowed."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        # NOT_STARTED → BUDGET_CHECKED is valid
        allowed, reason = mgr.can_transition("T27.1", TaskState.BUDGET_CHECKED)
        assert allowed
        assert "Valid" in reason
    
    def test_invalid_transition_blocked(self, tmp_path):
        """Invalid transitions should be blocked."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        # NOT_STARTED → IN_PROGRESS is invalid (must check budget first)
        allowed, reason = mgr.can_transition("T27.1", TaskState.IN_PROGRESS)
        assert not allowed
        assert "budget" in reason.lower()
    
    def test_skip_to_completed_blocked(self, tmp_path):
        """Cannot skip directly to COMPLETED."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        allowed, reason = mgr.can_transition("T27.1", TaskState.COMPLETED)
        assert not allowed
    
    def test_transition_updates_state(self, tmp_path):
        """transition() should update state."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        
        assert mgr.get_state("T27.1") == TaskState.BUDGET_CHECKED
    
    def test_full_valid_progression(self, tmp_path):
        """Full valid state progression should work."""
        mgr = TaskStateManager(tmp_path / "state.json")
        task = "T27.1"
        
        # Progress through all states
        mgr.transition(task, TaskState.BUDGET_CHECKED)
        assert mgr.get_state(task) == TaskState.BUDGET_CHECKED
        
        mgr.transition(task, TaskState.IN_PROGRESS)
        assert mgr.get_state(task) == TaskState.IN_PROGRESS
        
        mgr.transition(task, TaskState.AC_VERIFIED)
        assert mgr.get_state(task) == TaskState.AC_VERIFIED
        
        mgr.transition(task, TaskState.COMPLETED)
        assert mgr.get_state(task) == TaskState.COMPLETED
    
    def test_state_persisted_to_file(self, tmp_path):
        """State should persist to file."""
        state_file = tmp_path / "state.json"
        
        mgr1 = TaskStateManager(state_file)
        mgr1.transition("T27.1", TaskState.BUDGET_CHECKED)
        
        # New manager should read same state
        mgr2 = TaskStateManager(state_file)
        assert mgr2.get_state("T27.1") == TaskState.BUDGET_CHECKED
    
    def test_history_recorded(self, tmp_path):
        """Transitions should be recorded in history."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED, trigger="budget check")
        mgr.transition("T27.1", TaskState.IN_PROGRESS, trigger="ttask start")
        
        history = mgr.get_history("T27.1")
        
        assert len(history) == 2
        assert history[0]["to_state"] == "in_progress"  # Newest first
        assert history[1]["to_state"] == "budget_checked"
    
    def test_require_state_passes_when_correct(self, tmp_path):
        """require_state should pass when state is correct."""
        mgr = TaskStateManager(tmp_path / "state.json")
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        
        # Should not raise
        mgr.require_state("T27.1", TaskState.BUDGET_CHECKED)
    
    def test_require_state_exits_when_wrong(self, tmp_path):
        """require_state should exit when state is wrong."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        with pytest.raises(ClickExit):
            mgr.require_state("T27.1", TaskState.IN_PROGRESS)
    
    def test_reset_task(self, tmp_path):
        """reset_task should return task to NOT_STARTED."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        mgr.transition("T27.1", TaskState.IN_PROGRESS)
        
        mgr.reset_task("T27.1")
        
        assert mgr.get_state("T27.1") == TaskState.NOT_STARTED
    
    def test_get_all_states(self, tmp_path):
        """get_all_states should return all tracked tasks."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        mgr.transition("T27.2", TaskState.BUDGET_CHECKED)
        
        all_states = mgr.get_all_states()
        
        assert "T27.1" in all_states
        assert "T27.2" in all_states
        assert all_states["T27.1"] == "budget_checked"
        assert all_states["T27.2"] == "budget_checked"
    
    def test_can_regress_from_ac_verified(self, tmp_path):
        """Should allow AC_VERIFIED → IN_PROGRESS (AC unchecked)."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        mgr.transition("T27.1", TaskState.IN_PROGRESS)
        mgr.transition("T27.1", TaskState.AC_VERIFIED)
        
        # Should be able to go back if AC is unchecked
        allowed, _ = mgr.can_transition("T27.1", TaskState.IN_PROGRESS)
        assert allowed
    
    def test_cannot_progress_from_completed(self, tmp_path):
        """Cannot transition from COMPLETED (terminal state)."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        # Set up completed task
        mgr._states["T27.1"] = "completed"
        mgr._save()
        
        allowed, reason = mgr.can_transition("T27.1", TaskState.IN_PROGRESS)
        assert not allowed
        assert "terminal" in reason.lower()


class TestStateTransitionEdgeCases:
    """Edge case tests for state transitions."""
    
    def test_blocked_can_unblock(self, tmp_path):
        """BLOCKED tasks should be able to transition out."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BLOCKED)
        
        # Should be able to go back to NOT_STARTED
        allowed, _ = mgr.can_transition("T27.1", TaskState.NOT_STARTED)
        assert allowed
        
        # Or to IN_PROGRESS (if was in progress when blocked)
        allowed, _ = mgr.can_transition("T27.1", TaskState.IN_PROGRESS)
        assert allowed
    
    def test_budget_checked_can_reset(self, tmp_path):
        """BUDGET_CHECKED can go back to NOT_STARTED (budget expired)."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        mgr.transition("T27.1", TaskState.BUDGET_CHECKED)
        
        allowed, _ = mgr.can_transition("T27.1", TaskState.NOT_STARTED)
        assert allowed
    
    def test_handles_corrupt_state_file(self, tmp_path):
        """Should handle corrupt state file gracefully."""
        state_file = tmp_path / "state.json"
        state_file.write_text("not valid json {{{")
        
        mgr = TaskStateManager(state_file)
        
        # Should default to empty state
        assert mgr.get_state("T27.1") == TaskState.NOT_STARTED
    
    def test_handles_unknown_state_string(self, tmp_path):
        """Should handle unknown state strings gracefully."""
        state_file = tmp_path / "state.json"
        state_file.write_text('{"states": {"T27.1": "unknown_state"}, "history": []}')
        
        mgr = TaskStateManager(state_file)
        
        # Should default to NOT_STARTED for unknown state
        assert mgr.get_state("T27.1") == TaskState.NOT_STARTED


class TestGlobalManager:
    """Tests for global state manager instance."""
    
    def test_get_state_manager_returns_singleton(self, tmp_path):
        """get_state_manager should return same instance."""
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=tmp_path):
            mgr1 = get_state_manager()
            mgr2 = get_state_manager()
        
        assert mgr1 is mgr2
    
    def test_reset_state_manager_clears_singleton(self, tmp_path):
        """reset_state_manager should clear the singleton."""
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=tmp_path):
            mgr1 = get_state_manager()
            reset_state_manager()
            mgr2 = get_state_manager()
        
        assert mgr1 is not mgr2
