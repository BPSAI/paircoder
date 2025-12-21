---
name: trello-task-workflow
description: Work on tasks from Trello board with automatic status sync. Use when starting work, completing tasks, checking what to work on next, or when user says "work on task", "start task", "next task", "finish task", "I'm blocked", "pick up task", "claim task", "mark done".
---

# Trello Task Workflow

## When to Use This Workflow

**Use `ttask` commands if Trello is connected.** They handle everything:
- Trello card updates (move, comments, checklist)
- Local task file updates
- Hook triggers (timer, metrics, state.md)

**Do NOT use `task update` for Trello projects** - it only updates local files and misses Trello sync.

```
Check: bpsai-pair trello status
├── Connected → Use ttask commands (this workflow)
└── Not connected → Use task update commands instead
```

## Prerequisites

```bash
bpsai-pair trello status    # Check connection
bpsai-pair trello connect   # If not connected
```

## Finding Tasks

```bash
bpsai-pair task list --agent --status sprint   # AI-ready tasks
bpsai-pair task list --status in_progress      # Active tasks
bpsai-pair task show TRELLO-XXX                # Task details
```

## Starting Work

```bash
bpsai-pair ttask start TRELLO-XXX
```

Moves card Sprint → In Progress and adds comment.

## During Work

```bash
# Progress update
bpsai-pair ttask comment TRELLO-XXX "Completed API, starting tests"

# Check acceptance criteria item
bpsai-pair ttask check TRELLO-XXX "item text"
```

Always include task ID in commits: `feat(auth): add JWT (TRELLO-123)`

## Completing Work

**One command does everything:**

```bash
bpsai-pair ttask done TRELLO-XXX --summary "What was done" --list "Deployed/Done"
```

This single command:
- ✓ Moves card to "Deployed/Done"
- ✓ Checks all acceptance criteria items
- ✓ Adds completion summary
- ✓ Updates local task file
- ✓ Triggers all hooks (timer, metrics, state.md)

**You do NOT need to also run `task update`** - `ttask done` handles it all.

## Blocked

```bash
bpsai-pair ttask block TRELLO-XXX --reason "Waiting for API credentials"
```

## Workflow

```
Sprint → In Progress → Deployed/Done
              ↓
           Blocked
```

## Quick Reference

| Action | Command |
|--------|---------|
| Find next task | `bpsai-pair task next` |
| Start task | `bpsai-pair ttask start TRELLO-XXX` |
| Add comment | `bpsai-pair ttask comment TRELLO-XXX "msg"` |
| Complete | `bpsai-pair ttask done TRELLO-XXX --summary "..." --list "Deployed/Done"` |
| Block | `bpsai-pair ttask block TRELLO-XXX --reason "..."` |

## Important: Don't Mix Commands

| Wrong | Right |
|-------|-------|
| `task update --status in_progress` | `ttask start TRELLO-XXX` |
| `task update --status done` | `ttask done TRELLO-XXX --summary "..."` |
| Using both `ttask done` AND `task update` | Just use `ttask done` |

**Remember:** For Trello projects, `ttask` commands are all you need.

## Troubleshooting

### "Not connected to Trello"

```bash
bpsai-pair trello connect
# Follow prompts for API key and token
```

### "Board not configured"

```bash
bpsai-pair trello boards                    # List available boards
bpsai-pair trello use-board <board-id>      # Set board for project
```

### "Task not found"

The task ID format is `TRELLO-<short_id>`. Find the short ID from the Trello URL: `trello.com/c/abc123` → `TRELLO-abc123`
