---
id: TASK-099
title: Security agent implementation
status: done
priority: P0
complexity: 40
plan: plan-2025-12-sprint-16-real-subagents
sprint: sprint-16
stack: CLI
effort: M
trello_labels:
- Backend
- Security / Admin
- AI / ML Integration
tags:
- CLI
- agents
- security
created: 2025-12-17
---

# TASK-099: Security agent implementation

## Description

Wire security agent for pre-execution review using the AgentInvoker framework. This agent acts as a gatekeeper that can block unsafe operations.

## Acceptance Criteria

- [ ] Load `.claude/agents/security.md` via AgentInvoker
- [ ] Configure for `permissionMode: plan` (read-only, gatekeeper)
- [ ] Pass command or code changes for review
- [ ] Return ALLOW/WARN/BLOCK decision
- [ ] Integration with command execution pipeline
- [ ] Can block operations before they run
- [ ] Tests for security decisions

## Implementation Details

### Trigger conditions

- Before any potentially dangerous command
- Pre-commit for code changes
- When task involves auth/credentials

### Context to pass

- Command to be executed (for command review)
- Code diff (for code review)
- File paths involved

### Expected output

```python
@dataclass
class SecurityDecision:
    action: Literal["ALLOW", "WARN", "BLOCK"]
    reason: str
    details: list[str]
    soc2_controls: list[str]  # CC6.1, CC7.1, etc.
```

### Integration

- Hook into `SecurityReviewHook` from `security/review.py`
- Use existing allowlist as first filter
- Agent provides deeper analysis

## Dependencies

- TASK-096 (Agent Invocation Framework)