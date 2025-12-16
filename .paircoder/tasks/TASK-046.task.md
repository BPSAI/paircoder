---
id: TASK-046
title: Add plan status command
plan: plan-2025-01-paircoder-v2.4-mcp
type: feature
priority: P1
complexity: 25
status: done
sprint: sprint-11
tags:
  - cli
  - planning
depends_on:
  - TASK-045
---

# Objective

Add `bpsai-pair plan status [plan-id]` command that shows comprehensive plan status with sprint breakdown.

# Current State

`bpsai-pair plan status` returns "No such command 'status'" - the command doesn't exist.

# Implementation Plan

```python
@plan_app.command("status")
def plan_status(
    plan_id: str = typer.Argument("current", help="Plan ID or 'current'"),
    verbose: bool = typer.Option(False, "--verbose", "-v")
):
    """Show plan status with sprint/task breakdown."""
    state_manager = get_state_manager()
    
    # If "current", get from state.md or config
    if plan_id == "current":
        plan_id = state_manager.get_active_plan_id()
    
    # Load plan
    plan_parser = PlanParser(find_paircoder_dir() / "plans")
    plan = plan_parser.get_plan_by_id(plan_id)
    
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)
    
    # Load associated tasks
    task_parser = TaskParser(find_paircoder_dir() / "tasks")
    tasks = task_parser.get_tasks_for_plan(plan_id)
    
    # Display rich table with:
    # - Plan metadata
    # - Sprint progress bars
    # - Task counts by status
    # - Blockers
```

# Output Format

```
Plan: plan-2025-01-paircoder-v2.4-mcp
Title: MCP Server & Integration Glue
Status: in_progress
Type: feature

Goals:
  ✓ Make PairCoder autonomous
  ○ Agents can call tools directly
  ○ Auto-track metrics and time

Sprint Progress:
  sprint-11 [████████░░░░░░░░] 50%  (5/10 tasks)

Task Status:
  ✓ Done:        2
  ● In Progress: 3
  ○ Pending:     4
  ⊘ Blocked:     1

Blockers:
  TASK-048 blocked by: TASK-047 (MCP core not complete)
```

# Acceptance Criteria

- [ ] `bpsai-pair plan status` shows current active plan
- [ ] `bpsai-pair plan status <plan-id>` shows specific plan
- [ ] Shows sprint progress bars
- [ ] Shows task counts: pending/in_progress/done/blocked
- [ ] Shows blockers with reasons
- [ ] --verbose shows individual task list

# Files to Modify

- `tools/cli/bpsai_pair/planning/cli_commands.py`
- `tools/cli/bpsai_pair/planning/state.py` (get_active_plan_id)
