---
id: TASK-101
title: Agent selection logic
status: done
priority: P0
complexity: 30
plan: plan-2025-12-sprint-16-real-subagents
sprint: sprint-16
stack: CLI
effort: M
trello_labels:
- Backend
- AI / ML Integration
tags:
- CLI
- orchestration
- routing
created: 2025-12-17
---

# TASK-101: Agent selection logic

## Description

Route tasks to appropriate agent based on task characteristics.

## Acceptance Criteria

- [ ] Analyze task characteristics using existing `TaskCharacteristics`
- [ ] Match against agent capabilities
- [ ] Use scoring algorithm to select best agent
- [ ] Fall back to default (claude-code) if no match
- [ ] Wire into `bpsai-pair orchestrate task` command
- [ ] Tests for selection logic

## Implementation Details

### Selection rules

```python
def select_agent(task: Task) -> str:
    """Select appropriate agent based on task characteristics."""

    # Check task type
    if task.type == "design" or "plan" in task.title.lower():
        return "planner"

    if task.type == "review" or "PR" in task.title:
        return "reviewer"

    if "security" in task.tags or "auth" in task.title.lower():
        return "security"

    # Check complexity for model selection
    if task.complexity > 60:
        return "claude-code"  # Full agent for complex tasks

    # Default
    return "default"
```

### Files to modify

- `tools/cli/bpsai_pair/orchestration/orchestrator.py`
- `tools/cli/bpsai_pair/cli_commands.py` (orchestrate command)

### Integration points

- Extend existing `Orchestrator.assign_task()` method
- Use `AgentInvoker` from TASK-096
- Call appropriate agent based on selection

## Dependencies

- TASK-096 (Agent Invocation Framework)