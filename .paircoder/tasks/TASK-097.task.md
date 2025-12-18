---
id: TASK-097
title: Planner agent implementation
status: done
priority: P1
complexity: 35
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
- planner
created: 2025-12-17
completed: 2025-12-17
---

# TASK-097: Planner agent implementation

## Description

Wire planner agent for design tasks using the AgentInvoker framework.

## Acceptance Criteria

- [x] Load `.claude/agents/planner.md` via AgentInvoker
- [x] Configure for `permissionMode: plan` (read-only)
- [x] Pass task description + relevant file context
- [x] Return structured plan output
- [x] Integration with orchestrate command
- [x] Tests for planner invocation

## Implementation Details

### Trigger conditions

- Task type is DESIGN
- Task title contains "plan", "design", "architecture"
- User explicitly requests planning

### Context to pass

- Task file content
- Relevant source files (based on task tags)
- Current state.md

### Expected output

- Structured plan with phases
- File list to modify
- Estimated complexity

## Dependencies

- TASK-096 (Agent Invocation Framework)