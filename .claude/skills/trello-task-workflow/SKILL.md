---
name: trello-task-workflow
description: Work on tasks from Trello board with automatic status sync. Use when starting work, completing tasks, checking what to work on next, or when user says "work on task", "start task", "next task", "finish task", "I'm blocked", "pick up task", "claim task", "mark done".
---

# Trello Task Workflow

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

**Two-step completion (required):**

```bash
# 1. Complete on Trello (checks all AC)
bpsai-pair ttask done TRELLO-XXX --summary "What was done" --list "Deployed/Done"

# 2. Update local file
bpsai-pair task update TASK-XXX --status done
```

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
