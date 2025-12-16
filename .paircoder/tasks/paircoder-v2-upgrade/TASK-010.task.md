---
id: TASK-010
plan: plan-2025-01-paircoder-v2-upgrade
title: Add 'bpsai-pair task' CLI commands
type: feature
priority: P1
complexity: 40
status: done
sprint: sprint-2
tags: [cli, planning, tasks, commands]
---

# Objective

Implement CLI subcommands for task management:
- `bpsai-pair task list` - List all tasks
- `bpsai-pair task show <id>` - Show task details
- `bpsai-pair task update <id> --status <status>` - Update task status
- `bpsai-pair task next` - Show next task to work on

# Implementation Plan

1. Add task commands to `planning/cli_commands.py`
2. Implement `task_list` with plan and status filters, JSON output
3. Implement `task_show` with full body display
4. Implement `task_update` for status changes
5. Implement `task_next` using StateManager priority logic
6. Register `task_app` in main `cli.py`

# Files Created/Modified

- `tools/cli/bpsai_pair/planning/cli_commands.py` - Task commands (Typer)
- `tools/cli/bpsai_pair/cli.py` - Registered task_app

# Acceptance Criteria

- [x] `bpsai-pair task --help` shows all subcommands
- [x] `task list` shows tasks with status emoji and filtering
- [x] `task show` displays task details including markdown body
- [x] `task update` modifies status in task file frontmatter
- [x] `task next` returns highest priority pending/in-progress task
- [x] All commands support `--json` output where applicable

# Verification

```bash
bpsai-pair task --help
bpsai-pair task list
bpsai-pair task show TASK-001
bpsai-pair task next
```

# Notes

The `task next` command uses StateManager to intelligently prioritize tasks:
1. First, return any in-progress tasks
2. Then, return highest priority (P0 > P1 > P2) pending task
