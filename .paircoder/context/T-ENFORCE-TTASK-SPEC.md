---
id: T-ENFORCE-TTASK
title: Enforce ttask done for Trello-Connected Projects
plan: sprint-23
priority: 1
complexity: 35
effort: S
status: pending
depends_on: []
trello_card_id: null
---

# Enforce ttask done for Trello-Connected Projects

## Goal

Make it **impossible** for Claude (or any user) to bypass Trello AC verification by using `task update --status done` on Trello-connected projects. The wrong path should be blocked, not just warned.

## Background

### The Problem

Claude repeatedly uses `task update --status done` instead of `ttask done`, bypassing:
- Acceptance criteria verification
- Trello card completion summary
- Card movement to Done list

Despite:
- Documentation clearly stating to use `ttask done`
- Skills explaining the workflow
- Root cause analyses identifying the issue
- Promises to do better next time

**Claude forgets instructions between sessions.** Documentation-based fixes don't work.

### Current Behavior

```
User: bpsai-pair task update T23.1 --status done

Result:
- Local task file updated ✓
- Trello card unchanged ✗
- AC items unchecked ✗
- No completion summary ✗
```

### Desired Behavior

```
User: bpsai-pair task update T23.1 --status done

Result (Trello project):
- ERROR: This project uses Trello. Use 'ttask done' instead.
- Command blocked (unless --force)

User: bpsai-pair ttask done TRELLO-XX --summary "Completed feature"

Result:
- AC items auto-checked ✓
- Completion summary added ✓
- Card moved to Done ✓
- Local task file updated ✓
```

## Implementation

### 1. Block `task update --status done` on Trello Projects

**File:** `tools/cli/bpsai_pair/planning/cli_commands.py`

Find the `task update` command and add Trello enforcement:

```python
@task_app.command("update")
def task_update(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status"),
    priority: Optional[int] = typer.Option(None, "--priority", "-p", help="New priority"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update, bypass Trello check"),
    # ... other options ...
):
    """Update task properties."""
    
    # ENFORCEMENT: Block status=done on Trello projects unless forced
    if status and status.lower() == "done" and not force:
        if _is_trello_enabled():
            console.print("\n[red]❌ BLOCKED: This project uses Trello integration.[/red]")
            console.print("")
            console.print("[yellow]Use the Trello command to complete tasks:[/yellow]")
            console.print("")
            console.print("  1. Find the card ID:")
            console.print(f"     [cyan]bpsai-pair ttask list | grep {task_id}[/cyan]")
            console.print("")
            console.print("  2. Complete with ttask done:")
            console.print("     [cyan]bpsai-pair ttask done <TRELLO-ID> --summary \"What was done\" --list \"Deployed/Done\"[/cyan]")
            console.print("")
            console.print("[dim]This ensures:[/dim]")
            console.print("[dim]  • Acceptance criteria are verified/checked[/dim]")
            console.print("[dim]  • Completion summary is recorded[/dim]")
            console.print("[dim]  • Card is moved to the correct list[/dim]")
            console.print("")
            console.print("[dim]To bypass (not recommended): --force[/dim]")
            raise typer.Exit(1)
    
    # ... rest of existing update logic ...


def _is_trello_enabled() -> bool:
    """Check if Trello integration is enabled for this project."""
    try:
        from ..config import Config
        config = Config.load()
        return config.trello.enabled and config.trello.board_id
    except Exception:
        return False
```

### 2. Make `--check-all` the Default for `ttask done`

**File:** `tools/cli/bpsai_pair/trello/task_commands.py`

Change the default behavior so AC items are always checked:

```python
@app.command("done")
def done_cmd(
    card_id: str = typer.Argument(..., help="Card ID to complete"),
    summary: str = typer.Option(..., "--summary", "-s", help="Completion summary"),
    list_name: str = typer.Option("Deployed/Done", "--list", "-l", help="Target list"),
    # CHANGED: check_all is now True by default
    check_all: bool = typer.Option(True, "--check-all/--no-check-all", help="Auto-check all AC items (default: yes)"),
    # NEW: strict mode for when you want to verify manually
    strict: bool = typer.Option(False, "--strict", help="Block if AC items are unchecked"),
    # DEPRECATED: kept for backwards compatibility
    skip_checklist: bool = typer.Option(False, "--skip-checklist", hidden=True, help="[DEPRECATED] Use --no-check-all"),
    force: bool = typer.Option(False, "--force", "-f", help="Force completion ignoring all checks"),
):
    """Complete a task (moves to Done list).
    
    By default, automatically checks all 'Acceptance Criteria' checklist items.
    
    Use --strict to require AC items to be manually checked first (blocks if unchecked).
    Use --no-check-all to skip AC handling entirely.
    Use --force to bypass all verification.
    
    Examples:
        # Standard completion (auto-checks AC)
        bpsai-pair ttask done TRELLO-123 --summary "Implemented feature X"
        
        # Require manual AC verification
        bpsai-pair ttask done TRELLO-123 --summary "..." --strict
        
        # Skip AC handling
        bpsai-pair ttask done TRELLO-123 --summary "..." --no-check-all
    """
    
    # Handle deprecated flag
    if skip_checklist:
        console.print("[yellow]⚠️  --skip-checklist is deprecated. Use --no-check-all[/yellow]")
        check_all = False
    
    # ... existing card lookup code ...
    
    # AC handling logic
    if force:
        # Bypass everything
        console.print("[yellow]⚠️  Force mode: skipping all verification[/yellow]")
    elif strict:
        # Strict mode: block if any AC unchecked
        unchecked = _get_unchecked_ac_items(card)
        if unchecked:
            console.print("[red]❌ Cannot complete: unchecked acceptance criteria[/red]")
            console.print("")
            for item in unchecked:
                console.print(f"  [ ] {item}")
            console.print("")
            console.print("[dim]Check items manually on Trello, or use --force to bypass[/dim]")
            raise typer.Exit(1)
        console.print("[green]✓ All acceptance criteria verified[/green]")
    elif check_all:
        # Default: auto-check all AC items
        checked_count = _check_all_acceptance_criteria(card, client)
        if checked_count > 0:
            console.print(f"[green]✓ Auto-checked {checked_count} acceptance criteria item(s)[/green]")
        else:
            console.print("[green]✓ All acceptance criteria already complete[/green]")
    else:
        # --no-check-all: skip AC handling entirely
        console.print("[dim]AC verification skipped (--no-check-all)[/dim]")
    
    # ... rest of completion logic (move card, add comment, etc.) ...
    
    # ALSO update local task file automatically
    _update_local_task_status(card_id, "done")


def _update_local_task_status(card_id: str, status: str):
    """Update the corresponding local task file after ttask operation."""
    try:
        from ..planning import TaskParser
        from ..config import Config
        
        config = Config.load()
        task_parser = TaskParser(Path.cwd() / config.workflow.tasks_dir)
        
        # Find task by Trello card ID
        for task in task_parser.parse_all():
            if task.trello_card_id == card_id:
                task_parser.update_status(task.id, status)
                console.print(f"[dim]Local task {task.id} updated to {status}[/dim]")
                return
        
        # No matching task found - that's ok, might be Trello-only task
    except Exception as e:
        console.print(f"[dim]Note: Could not update local task file: {e}[/dim]")
```

### 3. Add `ttask complete` Alias (More Intuitive)

Some users might expect `complete` instead of `done`:

```python
@app.command("complete")
def complete_cmd(
    card_id: str = typer.Argument(...),
    summary: str = typer.Option(..., "--summary", "-s"),
    list_name: str = typer.Option("Deployed/Done", "--list", "-l"),
):
    """Alias for 'ttask done'. Complete a task and move to Done."""
    # Just call done_cmd with defaults
    done_cmd(card_id=card_id, summary=summary, list_name=list_name)
```

### 4. Update Skills to Reflect New Defaults

**File:** `.claude/skills/paircoder-task-lifecycle/SKILL.md`

```markdown
## Completing Tasks

### For Trello-Connected Projects (Default)

```bash
# This is the ONLY command you should use:
bpsai-pair ttask done <TRELLO-ID> --summary "What was accomplished"
```

This command:
- ✅ Auto-checks all acceptance criteria items
- ✅ Adds completion summary as comment
- ✅ Moves card to Deployed/Done
- ✅ Updates local task file automatically

### What NOT To Do

```bash
# ❌ WRONG - This is BLOCKED on Trello projects:
bpsai-pair task update T23.1 --status done
# Will error: "Use ttask done instead"
```

### Command Reference

| Command | Use When |
|---------|----------|
| `ttask done <id> -s "..."` | Completing any task (DEFAULT) |
| `ttask done <id> -s "..." --strict` | You want to verify AC manually first |
| `ttask done <id> -s "..." --no-check-all` | Skip AC entirely (not recommended) |
| `task update <id> --status done --force` | Emergency bypass (creates audit trail) |
```

### 5. Audit Trail for Forced Bypasses

When someone uses `--force` to bypass, log it:

```python
def _log_bypass(command: str, task_id: str, reason: str = "forced"):
    """Log when safety checks are bypassed."""
    from datetime import datetime
    
    log_path = Path.cwd() / ".paircoder" / "history" / "bypass_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "task_id": task_id,
        "reason": reason,
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

## Behavior Summary

| Command | Trello Enabled | Result |
|---------|----------------|--------|
| `task update --status done` | Yes | ❌ BLOCKED (use ttask) |
| `task update --status done --force` | Yes | ⚠️ Allowed (logged) |
| `task update --status done` | No | ✅ Works normally |
| `ttask done` | Yes | ✅ Auto-checks AC, moves card |
| `ttask done --strict` | Yes | ✅ Blocks if AC unchecked |
| `ttask done --no-check-all` | Yes | ⚠️ Skips AC |
| `ttask done --force` | Yes | ⚠️ Bypasses all (logged) |

## Acceptance Criteria

- [ ] `task update --status done` blocked on Trello projects
- [ ] Block message explains how to use `ttask done` correctly
- [ ] `--force` bypasses block (with warning)
- [ ] `ttask done` auto-checks AC by default
- [ ] `ttask done --strict` blocks if AC unchecked
- [ ] `ttask done --no-check-all` skips AC handling
- [ ] `ttask done` also updates local task file
- [ ] Bypasses logged to `.paircoder/history/bypass_log.jsonl`
- [ ] Skills documentation updated
- [ ] `--skip-checklist` deprecated with warning

## Test Cases

```python
def test_task_update_done_blocked_on_trello(tmp_path, trello_config):
    """task update --status done blocked when Trello enabled."""
    result = runner.invoke(task_app, ["update", "T1", "--status", "done"])
    assert result.exit_code == 1
    assert "BLOCKED" in result.output
    assert "ttask done" in result.output

def test_task_update_done_allowed_with_force(tmp_path, trello_config):
    """task update --status done allowed with --force."""
    result = runner.invoke(task_app, ["update", "T1", "--status", "done", "--force"])
    assert result.exit_code == 0

def test_task_update_done_allowed_without_trello(tmp_path, no_trello_config):
    """task update --status done works when Trello not enabled."""
    result = runner.invoke(task_app, ["update", "T1", "--status", "done"])
    assert result.exit_code == 0

def test_ttask_done_auto_checks_ac(mock_trello):
    """ttask done auto-checks AC items by default."""
    result = runner.invoke(ttask_app, ["done", "TRELLO-1", "-s", "Done"])
    assert result.exit_code == 0
    assert "Auto-checked" in result.output

def test_ttask_done_strict_blocks_unchecked(mock_trello_with_unchecked_ac):
    """ttask done --strict blocks when AC unchecked."""
    result = runner.invoke(ttask_app, ["done", "TRELLO-1", "-s", "Done", "--strict"])
    assert result.exit_code == 1
    assert "Cannot complete" in result.output

def test_bypass_logged(tmp_path, trello_config):
    """Forced bypasses are logged."""
    runner.invoke(task_app, ["update", "T1", "--status", "done", "--force"])
    log_path = tmp_path / ".paircoder" / "history" / "bypass_log.jsonl"
    assert log_path.exists()
```

## Migration Notes

### For Existing Users

No breaking changes. The new defaults are safer:
- `ttask done` now auto-checks (was blocking)
- `task update --status done` now warns/blocks on Trello projects

### Deprecated Flags

- `--skip-checklist` → Use `--no-check-all`

## Effort Estimate

- Complexity: 35
- Effort: S (2-4 hours)
- Risk: Low (behavior change is safer, not breaking)

## Why This Works

1. **Code enforces behavior** - Not documentation that Claude forgets
2. **Wrong path is blocked** - Not just warned
3. **Right path is easy** - `ttask done` just works
4. **Escape hatch exists** - `--force` for emergencies
5. **Audit trail** - Know when bypasses happen
6. **Auto-updates local file** - One command does everything
