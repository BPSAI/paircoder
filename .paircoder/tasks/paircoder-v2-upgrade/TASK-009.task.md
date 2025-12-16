---
id: TASK-009
plan: plan-2025-01-paircoder-v2-upgrade
title: Add 'bpsai-pair plan' CLI commands
type: feature
priority: P1
complexity: 50
status: done
sprint: sprint-2
tags: [cli, planning, commands]
---

# Objective

Implement CLI subcommands for plan management:
- `bpsai-pair plan new <slug>` - Create a new plan
- `bpsai-pair plan list` - List all plans
- `bpsai-pair plan show <id>` - Show plan details
- `bpsai-pair plan tasks <id>` - List tasks for a plan
- `bpsai-pair plan add-task <id>` - Add a task to a plan

# Implementation Plan

1. Create `planning/cli_commands.py` with Typer app
2. Implement `plan_new` command with options for type, title, flow, goals
3. Implement `plan_list` with status filter and JSON output
4. Implement `plan_show` with JSON output
5. Implement `plan_tasks` with status filter
6. Implement `plan_add_task` with all task fields
7. Register `plan_app` in main `cli.py`

# Files Created/Modified

- `tools/cli/bpsai_pair/planning/cli_commands.py` - Plan commands (Typer)
- `tools/cli/bpsai_pair/cli.py` - Registered plan_app

# Acceptance Criteria

- [x] `bpsai-pair plan --help` shows all subcommands
- [x] `plan new` creates plan file in `.paircoder/plans/`
- [x] `plan list` shows all plans with status emoji
- [x] `plan show` displays full plan details
- [x] `plan tasks` lists tasks grouped by sprint
- [x] `plan add-task` creates task file in `.paircoder/tasks/<slug>/`
- [x] All commands support `--json` output

# Verification

```bash
bpsai-pair plan --help
bpsai-pair plan list
bpsai-pair plan show plan-2025-01-paircoder-v2-upgrade
```

# Notes

Originally written in Click, converted to Typer by Claude Code during integration to match the main CLI framework.
