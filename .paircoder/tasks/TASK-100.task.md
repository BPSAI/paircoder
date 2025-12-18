---
id: TASK-100
title: Agent handoff protocol
status: done
priority: P1
complexity: 40
plan: plan-2025-12-sprint-16-real-subagents
sprint: sprint-16
stack: CLI
effort: M
trello_labels:
  - Backend
  - AI / ML Integration
tags:
  - CLI
  - agents
  - handoff
created: 2025-12-17
---

# TASK-100: Agent handoff protocol

## Description

Implement actual context passing between agents with structured handoff packages.

## Acceptance Criteria

- [ ] Extend `HandoffPackage` with structured context
- [ ] Create handoff serialization format
- [ ] Implement `prepare_handoff()` method
- [ ] Implement `receive_handoff()` method
- [ ] Track handoff chain for debugging
- [ ] Tests for handoff operations

## Implementation Details

### Handoff data structure

```python
@dataclass
class EnhancedHandoffPackage:
    # Existing fields
    task_id: str
    source_agent: str
    target_agent: str

    # New structured context
    task_description: str
    acceptance_criteria: list[str]
    files_touched: list[str]
    current_state: str
    work_completed: str
    remaining_work: str
    token_budget: int

    # Chain tracking
    handoff_id: str
    previous_handoff_id: Optional[str]
    chain_depth: int
```

### Files to modify

- `tools/cli/bpsai_pair/orchestration/handoff.py`
- `tools/cli/bpsai_pair/orchestration/invoker.py`

### Serialization

- Save to `.paircoder/handoffs/{handoff_id}.json`
- Include compressed file contents
- Track in handoff log

## Dependencies

- TASK-096 (Agent Invocation Framework)
