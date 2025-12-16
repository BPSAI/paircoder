"""
MCP Test Fixtures

Provides fixtures for testing MCP server and tools.
"""

import pytest
from pathlib import Path


@pytest.fixture
def mcp_paircoder_dir(tmp_path):
    """Create a minimal .paircoder directory for MCP testing."""
    paircoder_dir = tmp_path / ".paircoder"
    paircoder_dir.mkdir()
    (paircoder_dir / "tasks").mkdir()
    (paircoder_dir / "plans").mkdir()
    (paircoder_dir / "context").mkdir()
    (paircoder_dir / "history").mkdir()

    # Create minimal config
    config = paircoder_dir / "config.yaml"
    config.write_text("""
version: "2.4"
project:
  name: test-project
hooks:
  enabled: true
  on_task_start:
    - update_state
  on_task_complete:
    - update_state
    - check_unblocked
""")

    # Create minimal state.md
    state = paircoder_dir / "context" / "state.md"
    state.write_text("""# Project State

Last updated: 2025-01-01

**Plan:** `test-plan`
**Current Sprint:** sprint-1

## What Was Just Done
- Initial setup

## What's Next
- Implement features

## Blockers
None
""")

    return paircoder_dir


@pytest.fixture
def sample_task_file(mcp_paircoder_dir):
    """Create a sample task file."""
    task_content = """---
id: TASK-001
title: Test task
plan: test-plan
status: pending
complexity: 20
priority: P1
sprint: sprint-1
tags:
  - test
depends_on: []
---

# Objective
Test objective for the task.

# Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
"""
    task_file = mcp_paircoder_dir / "tasks" / "TASK-001.task.md"
    task_file.write_text(task_content)
    return "TASK-001"


@pytest.fixture
def sample_plan_file(mcp_paircoder_dir):
    """Create a sample plan file."""
    plan_content = """---
id: test-plan
title: Test Plan
type: feature
status: in_progress
created_at: 2025-01-01
goals:
  - Test goal 1
  - Test goal 2
sprints:
  - id: sprint-1
    title: Sprint 1
    goal: Complete initial work
    task_ids:
      - TASK-001
---

# Test Plan

A test plan for MCP testing.
"""
    plan_file = mcp_paircoder_dir / "plans" / "test-plan.plan.md"
    plan_file.write_text(plan_content)
    return "test-plan"


@pytest.fixture
def multiple_tasks(mcp_paircoder_dir):
    """Create multiple task files for testing."""
    tasks = [
        ("TASK-001", "pending", "P0", None),
        ("TASK-002", "in_progress", "P1", None),
        ("TASK-003", "done", "P1", None),
        ("TASK-004", "blocked", "P2", ["TASK-001"]),
    ]

    for task_id, status, priority, depends_on in tasks:
        deps_str = ", ".join(depends_on) if depends_on else "[]"
        content = f"""---
id: {task_id}
title: Task {task_id}
plan: test-plan
status: {status}
complexity: 30
priority: {priority}
sprint: sprint-1
depends_on: [{deps_str}]
---

# Objective
Objective for {task_id}.
"""
        task_file = mcp_paircoder_dir / "tasks" / f"{task_id}.task.md"
        task_file.write_text(content)

    return ["TASK-001", "TASK-002", "TASK-003", "TASK-004"]
