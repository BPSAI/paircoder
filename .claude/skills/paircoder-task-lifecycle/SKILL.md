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

## During Work (Progress Updates)

```bash
bpsai-pair ttask comment TASK-XXX "Completed API endpoints, starting tests"
```

This adds a comment to the Trello card without changing status. Use for:
- Milestone updates
- Noting decisions
- Progress visibility for team

## Completing a Task

### ⚠️ CRITICAL: Two-Step Completion Process

**You MUST use `ttask done` before `task update` to check acceptance criteria!**

---

**Step 1:** Find the Trello card ID:
```bash
bpsai-pair ttask list
```

**Step 2:** Complete on Trello using `ttask done` (**REQUIRED**):
```bash
bpsai-pair ttask done TRELLO-XX --summary "What was accomplished" --list "Deployed/Done"
```

This will:
- Move Trello card to "Deployed/Done" list
- **Auto-check ALL acceptance criteria items** ✓
- Add completion summary to card

**Step 3:** Update local task file:
```bash
bpsai-pair task update TASK-XXX --status done
```

This will:
- Update task file status
- Log completion in state.md

---

### ❌ COMMON MISTAKE: Skipping `ttask done`

**WRONG:** Only using `task update --status done`
- This updates local file but does NOT check acceptance criteria on Trello
- The Trello card will have unchecked acceptance criteria items

**RIGHT:** Using both commands in order:
1. `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` (checks AC)
2. `bpsai-pair task update TASK-XXX --status done` (updates local file)

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
| List Trello cards | `bpsai-pair ttask list` |
| Show card details | `bpsai-pair ttask show TRELLO-XX` |
| Start card | `bpsai-pair ttask start TRELLO-XX` |
| **Complete card** | `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` |
| Check acceptance item | `bpsai-pair ttask check TRELLO-XX "item text"` |
| Add progress comment | `bpsai-pair ttask comment TRELLO-XX "message"` |
| Block card | `bpsai-pair ttask block TRELLO-XX --reason "why"` |
| Move card to list | `bpsai-pair ttask move TRELLO-XX "List Name"` |

### When to Use `task` vs `ttask`

| Scenario | Use |
|----------|-----|
| Starting a task | `task update --status in_progress` |
| Adding progress notes | `ttask comment` |
| **Completing a task** | **`ttask done` then `task update`** |
| Checking acceptance criteria | `ttask check` |
| Working with Trello-only cards | `ttask` commands |

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
3. Read the task file for implementation plan
4. Begin work

### During Work
1. Add progress comments: `bpsai-pair ttask comment TASK-XXX "status update"`
2. Commit frequently with task ID in message

### When Completing a Task

**⚠️ CRITICAL: Follow ALL steps in order. Skipping step 4 leaves acceptance criteria unchecked!**

1. Ensure tests pass: `pytest -v`
2. Update state.md with what was done
3. Find card ID: `bpsai-pair ttask list` (note the TRELLO-XX id)
4. **REQUIRED:** Complete on Trello: `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
   - This moves card AND checks all acceptance criteria ✓
5. Update local file: `bpsai-pair task update TASK-XXX --status done`
6. Commit changes with task ID in message

**DO NOT skip step 4!** Using only `task update` will NOT check acceptance criteria on Trello.

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
