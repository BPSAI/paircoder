---
id: TASK-098
title: Reviewer agent implementation
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
- reviewer
created: 2025-12-17
completed: 2025-12-17
---

# TASK-098: Reviewer agent implementation

## Description

Wire reviewer agent for code review using the AgentInvoker framework.

## Acceptance Criteria

- [x] Load `.claude/agents/reviewer.md` via AgentInvoker
- [x] Configure for `permissionMode: plan` (read-only)
- [x] Pass git diff + changed files as context
- [x] Return structured review feedback
- [x] Integration with orchestrate command
- [x] Tests for reviewer invocation

## Implementation Details

### Trigger conditions

- Task type is REVIEW
- Pre-PR creation
- User requests review

### Context to pass

- Git diff (staged or between branches)
- Changed file contents
- Test results if available

### Expected output

- Review feedback structured by category
- Severity ratings (info, warning, blocker)
- Specific line references

## Dependencies

- TASK-096 (Agent Invocation Framework)