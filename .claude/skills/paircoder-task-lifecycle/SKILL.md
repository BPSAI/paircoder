---
name: paircoder-task-lifecycle
description: Manage PairCoder task status transitions. Use when starting, completing, or updating tasks. Triggers Trello card moves and hooks automatically. Required for task workflow compliance.
---

# PairCoder Task Lifecycle

## CRITICAL: Always Use CLI Commands

Task state changes MUST go through the CLI to trigger hooks (Trello sync, timers, state updates).

**Never** just edit task files or say "marking as done" - run the command.

## Starting a Task

```bash
bpsai-pair task update TASK-XXX --status in_progress
```

This will:
- Update task file status
- Move Trello card to "In Progress" list
- Start timer (when implemented)
- Update state.md current focus

## During Work

### Progress Comments
```bash
bpsai-pair ttask comment TASK-XXX "Completed API endpoints, starting tests"
```

### Checking Off Acceptance Criteria

**IMPORTANT:** As you complete each acceptance criterion, check it off immediately:

```bash
bpsai-pair ttask check TASK-XXX "No hardcoded credentials"
bpsai-pair ttask check TASK-XXX "SQL injection"
```

- Use partial text matching (just enough to identify the item)
- Check items as you complete them, not all at the end
- This provides real-time progress visibility in Trello

## Completing a Task

```bash
bpsai-pair task update TASK-XXX --status done
```

This will:
- Update task file status
- Move Trello card to "Deployed / Done" list
- Stop timer (when implemented)
- Log completion in state.md

## Quick Reference

### Local Task Commands (`task`)

Use these for status changes - they trigger all hooks.

| Action | Command |
|--------|---------|
| Start task | `bpsai-pair task update TASK-XXX --status in_progress` |
| Complete task | `bpsai-pair task update TASK-XXX --status done` |
| Block task | `bpsai-pair task update TASK-XXX --status blocked` |
| Show next task | `bpsai-pair task next` |
| Auto-assign next | `bpsai-pair task auto-next` |
| List all tasks | `bpsai-pair task list` |
| Show task details | `bpsai-pair task show TASK-XXX` |

### Trello Card Commands (`ttask`)

Use these for direct Trello operations.

| Action | Command |
|--------|---------|
| **Check off item** | `bpsai-pair ttask check TASK-XXX "item text"` |
| Uncheck item | `bpsai-pair ttask uncheck TASK-XXX "item text"` |
| Add progress comment | `bpsai-pair ttask comment TASK-XXX "message"` |
| Start card directly | `bpsai-pair ttask start TASK-XXX` |
| Complete card directly | `bpsai-pair ttask done TASK-XXX --summary "what was done"` |
| Block card | `bpsai-pair ttask block TASK-XXX --reason "why"` |
| Move card to list | `bpsai-pair ttask move TASK-XXX "List Name"` |
| List Trello cards | `bpsai-pair ttask list` |
| Show card details | `bpsai-pair ttask show TASK-XXX` |

### When to Use `task` vs `ttask`

| Scenario | Use |
|----------|-----|
| Changing task status | `task update` (fires hooks) |
| Checking off acceptance criteria | `ttask check` |
| Adding progress notes | `ttask comment` |
| Working with Trello-only cards | `ttask` commands |
| Need timers/metrics to trigger | `task update` |

## Task Status Values

| Status | Meaning | Trello List |
|--------|---------|-------------|
| `pending` | Not started | Backlog / Planned |
| `in_progress` | Currently working | In Progress |
| `blocked` | Waiting on something | Issues / Blocked |
| `review` | Ready for review | Review |
| `done` | Completed | Deployed / Done |

## Workflow Checklist

### When Starting a Task
1. Run: `bpsai-pair task update TASK-XXX --status in_progress`
2. Verify Trello card moved
3. Read the task file for acceptance criteria
4. Begin work

### During Work
1. **Check off criteria as you complete them:**
   ```bash
   bpsai-pair ttask check TASK-XXX "first criterion"
   # ... do work ...
   bpsai-pair ttask check TASK-XXX "second criterion"
   ```
2. Add progress comments for major milestones:
   ```bash
   bpsai-pair ttask comment TASK-XXX "Completed security scan, no issues found"
   ```
3. Commit frequently with task ID in message

### When Completing a Task
1. Ensure all acceptance criteria are checked off
2. Ensure tests pass: `pytest -v`
3. Update state.md with what was done
4. Run: `bpsai-pair task update TASK-XXX --status done`
5. Verify Trello card moved
6. Commit changes with task ID in message

## Trello Sync Commands

```bash
# Check Trello connection status
bpsai-pair trello status

# Sync plan to Trello (creates/updates cards)
bpsai-pair plan sync-trello PLAN-ID

# Force refresh from Trello
bpsai-pair trello refresh
```

## Full CLI Reference

See [reference/all-cli-commands.md](reference/all-cli-commands.md) for complete command documentation.
