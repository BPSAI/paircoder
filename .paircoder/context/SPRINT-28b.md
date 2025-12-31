# Sprint 28: Enforcement Wiring - Part 2

> **Continuation of SPRINT-28-TASKS-PART1.md**
> **Tasks T28.6 - T28.13**

---

## T28.6: Create `/pc-done` Slash Command

**Priority:** P1 | **Effort:** 2h | **Issue:** D3

### Purpose

Provide a single, correct way to complete tasks that enforces all workflow steps.

### Current Problem

CC uses whatever commands he feels like:
- Sometimes `task update --status done`
- Sometimes `ttask done` without `--strict`
- Sometimes `ttask done --force`
- Never updates state.md correctly

### Solution

One command that does everything correctly:

```bash
/pc-done T27.1
# Automatically:
# 1. Finds Trello card for T27.1
# 2. Verifies all AC items checked
# 3. Runs ttask done --strict
# 4. Updates local task file
# 5. Runs context-sync
# 6. Shows next task
```

### File to Create

`.claude/commands/pc-done.md`

```markdown
---
name: pc-done
description: Complete a task with full workflow compliance
arguments:
  - name: task_id
    description: Task ID (e.g., T27.1)
    required: true
---

# Complete Task: $ARGUMENTS

## Step 1: Verify Task State

```bash
# Check task exists and is in progress
bpsai-pair task show $ARGUMENTS
```

Verify the task shows `status: in_progress`. If not, STOP and report the issue.

## Step 2: Find Trello Card

```bash
# Get Trello card ID for this task
bpsai-pair ttask list | grep -i "$ARGUMENTS"
```

Extract the TRELLO-XX card ID. If no card found, STOP and report.

## Step 3: Verify Acceptance Criteria

```bash
# Show checklist status
bpsai-pair trello checklist <TRELLO-ID>
```

ALL items must be checked. If any are unchecked:
1. Check them: `bpsai-pair trello check <TRELLO-ID> "<item text>"`
2. Or STOP and report which items are incomplete

## Step 4: Complete the Task

```bash
# Complete with strict AC verification
bpsai-pair ttask done <TRELLO-ID> --strict --summary "<summary of work done>" --list "Deployed/Done"
```

**DO NOT use --force. DO NOT use --no-strict.**

If this command fails, STOP and report the error. Do not attempt workarounds.

## Step 5: Verify Local Sync

```bash
# Confirm local task updated
bpsai-pair task show $ARGUMENTS
```

Status should now be `done`. If not, report the discrepancy.

## Step 6: Update Context

```bash
# Sync context with what was done
bpsai-pair context-sync \
    --last "$ARGUMENTS: <brief description of accomplishment>" \
    --next "<next task ID or 'Ready for next task'>"
```

## Step 7: Report Completion

Output a summary:

```
✅ Task $ARGUMENTS Complete

Trello: <TRELLO-ID> moved to Deployed/Done
Local:  .paircoder/tasks/.../$ARGUMENTS.task.md updated
State:  .paircoder/context/state.md updated

Next task: <next task ID or "None - sprint complete">
```

## VIOLATIONS

The following are workflow violations. DO NOT DO THESE:

- ❌ Using `--force` flag
- ❌ Using `task update --status done` directly
- ❌ Skipping AC verification
- ❌ Not specifying `--list "Deployed/Done"`
- ❌ Not running context-sync
- ❌ Editing state.md manually instead of using context-sync
```

### Also Update Cookiecutter

Copy to `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/commands/pc-done.md`

### Acceptance Criteria

- [ ] `/pc-done T27.1` executes all steps in order
- [ ] Fails fast if any step fails
- [ ] Does not attempt workarounds or alternatives
- [ ] Uses `--strict` flag always
- [ ] Uses `--list "Deployed/Done"` always
- [ ] Runs `context-sync` at the end
- [ ] Reports clear completion summary

---

## T28.7: Create Bypass Audit Log

**Priority:** P0 | **Effort:** 2h | **Issue:** R4.2

### Purpose

Every workflow bypass must be logged for review. No silent bypasses.

### File to Create

`tools/cli/bpsai_pair/core/bypass_log.py`

```python
"""Bypass audit logging.

Every time a workflow enforcement is bypassed, it MUST be logged here.
The user can review bypasses with: bpsai-pair audit bypasses
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

console = Console()


def get_bypass_log_path() -> Path:
    """Get path to bypass log file."""
    return Path(".paircoder/history/bypass_log.jsonl")


def log_bypass(
    command: str,
    target: str,
    reason: str,
    bypass_type: str = "user_override",
    metadata: Optional[dict] = None
) -> None:
    """Log a workflow bypass.
    
    Args:
        command: The command being bypassed (e.g., "ttask_done_strict")
        target: The task/card being affected (e.g., "T27.1", "TRELLO-94")
        reason: User-provided reason for bypass
        bypass_type: Type of bypass (user_override, force_flag, local_only)
        metadata: Additional context
    """
    log_path = get_bypass_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "command": command,
        "target": target,
        "reason": reason,
        "bypass_type": bypass_type,
        "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        "metadata": metadata or {},
    }
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also print warning to console
    console.print(f"[yellow]⚠️ BYPASS LOGGED:[/yellow] {command} on {target}")
    console.print(f"[dim]   Reason: {reason}[/dim]")


def get_bypasses(since: Optional[datetime] = None, limit: int = 50) -> list[dict]:
    """Get recent bypasses from log.
    
    Args:
        since: Only return bypasses after this time
        limit: Maximum number to return
        
    Returns:
        List of bypass entries, newest first
    """
    log_path = get_bypass_log_path()
    if not log_path.exists():
        return []
    
    bypasses = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if since:
                    entry_time = datetime.fromisoformat(entry["timestamp"].rstrip("Z"))
                    if entry_time < since:
                        continue
                bypasses.append(entry)
    
    # Return newest first
    bypasses.reverse()
    return bypasses[:limit]


def show_bypasses(since: Optional[datetime] = None, limit: int = 50) -> None:
    """Display bypasses in a table."""
    bypasses = get_bypasses(since=since, limit=limit)
    
    if not bypasses:
        console.print("[green]No bypasses logged.[/green]")
        return
    
    table = Table(title=f"Workflow Bypasses (last {len(bypasses)})")
    table.add_column("Time", style="dim")
    table.add_column("Command")
    table.add_column("Target")
    table.add_column("Type")
    table.add_column("Reason")
    
    for entry in bypasses:
        # Format timestamp
        ts = entry["timestamp"][:19].replace("T", " ")
        
        table.add_row(
            ts,
            entry["command"],
            entry["target"],
            entry["bypass_type"],
            entry["reason"][:50] + "..." if len(entry["reason"]) > 50 else entry["reason"]
        )
    
    console.print(table)
    
    if bypasses:
        console.print(f"\n[yellow]⚠️ {len(bypasses)} bypasses found.[/yellow]")
        console.print("[dim]Review each bypass to ensure it was justified.[/dim]")
```

### Add CLI Command

Add to `tools/cli/bpsai_pair/commands/core.py` or create new `audit.py`:

```python
@app.command("audit")
def audit_bypasses(
    limit: int = typer.Option(50, "--limit", "-n", help="Number of entries to show"),
    since: Optional[str] = typer.Option(None, "--since", help="Show bypasses since date (YYYY-MM-DD)"),
):
    """Show workflow bypass audit log."""
    from bpsai_pair.core.bypass_log import show_bypasses
    from datetime import datetime
    
    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since)
    
    show_bypasses(since=since_dt, limit=limit)
```

### Test Cases

```python
"""Tests for bypass logging."""
import pytest
from datetime import datetime
from pathlib import Path

from bpsai_pair.core.bypass_log import log_bypass, get_bypasses


def test_log_bypass_creates_file(tmp_path, monkeypatch):
    """log_bypass must create log file if not exists."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".paircoder" / "history").mkdir(parents=True)
    
    log_bypass("test_command", "T27.1", "Test reason")
    
    log_path = tmp_path / ".paircoder" / "history" / "bypass_log.jsonl"
    assert log_path.exists()


def test_log_bypass_appends(tmp_path, monkeypatch):
    """Multiple bypasses must append to same file."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".paircoder" / "history").mkdir(parents=True)
    
    log_bypass("cmd1", "T1", "Reason 1")
    log_bypass("cmd2", "T2", "Reason 2")
    
    bypasses = get_bypasses()
    assert len(bypasses) == 2


def test_get_bypasses_returns_newest_first(tmp_path, monkeypatch):
    """get_bypasses must return newest first."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".paircoder" / "history").mkdir(parents=True)
    
    log_bypass("first", "T1", "First")
    log_bypass("second", "T2", "Second")
    
    bypasses = get_bypasses()
    assert bypasses[0]["command"] == "second"
    assert bypasses[1]["command"] == "first"


def test_bypass_entry_has_required_fields(tmp_path, monkeypatch):
    """Bypass entries must have all required fields."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".paircoder" / "history").mkdir(parents=True)
    
    log_bypass("test", "T27.1", "Test reason", metadata={"extra": "data"})
    
    bypasses = get_bypasses()
    entry = bypasses[0]
    
    assert "timestamp" in entry
    assert "command" in entry
    assert "target" in entry
    assert "reason" in entry
    assert "bypass_type" in entry
    assert "session_id" in entry
    assert entry["metadata"]["extra"] == "data"
```

### Acceptance Criteria

- [ ] `log_bypass()` creates JSONL entries
- [ ] Entries include timestamp, command, target, reason, type
- [ ] `bpsai-pair audit` shows recent bypasses
- [ ] `--since` flag filters by date
- [ ] Warning printed to console on each bypass
- [ ] All tests pass

---

## T28.8: Load Model Routing Config and Use It

**Priority:** P1 | **Effort:** 3h | **Issue:** R2.1

### Current Behavior (WRONG)

```python
# Config has routing rules:
routing:
  by_complexity:
    trivial: { model: claude-haiku-4-5 }
    complex: { model: claude-opus-4-5 }

# But HeadlessSession ignores them:
session = HeadlessSession()  # Uses default model always
```

### Required Behavior (CORRECT)

```python
# Complexity analyzed
complexity = analyze_task_complexity(task)  # Returns "complex"

# Routing config loaded
model = get_model_for_complexity(complexity)  # Returns "claude-opus-4-5"

# Session uses correct model
session = HeadlessSession(model=model)
```

### Files to Modify

1. `tools/cli/bpsai_pair/orchestration/routing.py` - Load and apply routing
2. `tools/cli/bpsai_pair/orchestration/session.py` - Accept model parameter

### EXACT Changes to routing.py

```python
"""Model routing based on task complexity."""
from typing import Optional
from bpsai_pair.core.config import load_config


def get_model_for_complexity(complexity_score: int) -> str:
    """Get the appropriate model for a complexity score.
    
    Args:
        complexity_score: Task complexity (0-100)
        
    Returns:
        Model identifier string
    """
    config = load_config()
    routing = config.routing.by_complexity
    
    # Find the appropriate tier
    for tier_name in ["trivial", "simple", "moderate", "complex", "epic"]:
        tier = getattr(routing, tier_name, None)
        if tier and complexity_score <= tier.max_score:
            return tier.model
    
    # Default to most capable model
    return config.models.navigator


def get_model_for_task(task_id: str) -> str:
    """Get the appropriate model for a specific task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        Model identifier string
    """
    from bpsai_pair.planning.parser import load_task
    
    task = load_task(task_id)
    
    # Check for override tags
    config = load_config()
    if task.tags:
        for tag in task.tags:
            if tag in config.routing.overrides:
                return config.routing.overrides[tag]
    
    # Use complexity-based routing
    return get_model_for_complexity(task.complexity)
```

### EXACT Changes to session.py

```python
# FIND the HeadlessSession class:
class HeadlessSession:
    def __init__(self, ...):
        self.model = "claude-sonnet-4-5"  # Hardcoded!
        
# REPLACE WITH:
class HeadlessSession:
    def __init__(
        self,
        model: Optional[str] = None,
        task_id: Optional[str] = None,
        ...
    ):
        if model:
            self.model = model
        elif task_id:
            from bpsai_pair.orchestration.routing import get_model_for_task
            self.model = get_model_for_task(task_id)
        else:
            from bpsai_pair.core.config import load_config
            self.model = load_config().models.driver
```

### Test Cases

```python
"""Tests for model routing."""

def test_trivial_task_uses_haiku():
    """Trivial tasks (0-20) should use Haiku."""
    model = get_model_for_complexity(15)
    assert "haiku" in model.lower()


def test_complex_task_uses_opus():
    """Complex tasks (61-80) should use Opus."""
    model = get_model_for_complexity(75)
    assert "opus" in model.lower()


def test_security_override():
    """Tasks tagged 'security' should always use Opus."""
    # Create task with security tag
    # Verify get_model_for_task returns opus
    pass


def test_session_uses_routed_model():
    """HeadlessSession must use routed model."""
    session = HeadlessSession(task_id="T27.1")
    # Verify session.model matches expected routing
    pass
```

### Acceptance Criteria

- [ ] `get_model_for_complexity()` returns correct model per tier
- [ ] `get_model_for_task()` checks override tags first
- [ ] `HeadlessSession` accepts `model` parameter
- [ ] `HeadlessSession` accepts `task_id` and routes automatically
- [ ] Default model comes from config, not hardcoded
- [ ] All tests pass

---

## T28.9: Add `--override` Flag with Mandatory Reason

**Priority:** P0 | **Effort:** 2h | **Issue:** R4.1

### Purpose

Replace `--force` with `--override --reason "..."` that requires explanation and logs.

### Pattern to Apply EVERYWHERE

Find all `--force` flags and replace with:

```python
# BEFORE:
force: bool = typer.Option(False, "--force", help="Skip checks")

# AFTER:
override: bool = typer.Option(False, "--override", help="Override enforcement (requires --reason)")
reason: Optional[str] = typer.Option(None, "--reason", help="Reason for override (required with --override)")

# And in the function body:
if override:
    if not reason:
        typer.echo("❌ ERROR: --override requires --reason", err=True)
        typer.echo("Example: --override --reason \"Hotfix for production issue\"", err=True)
        raise typer.Exit(1)
    log_bypass(command_name, target, reason, bypass_type="override")
    typer.echo(f"⚠️ Override applied: {reason}")
```

### Files to Search and Modify

```bash
grep -rn "\-\-force" tools/cli/bpsai_pair/
```

Expected locations:
- `trello/task_commands.py` - `ttask done --force`
- `planning/commands.py` - Various commands
- `commands/core.py` - init, validate, etc.

### Acceptance Criteria

- [ ] All `--force` flags replaced with `--override`
- [ ] `--override` requires `--reason` or fails
- [ ] All overrides logged via `log_bypass()`
- [ ] Help text explains override is logged
- [ ] All tests updated for new flag names
- [ ] All tests pass

---

## T28.10: Remove `--force` Flag from `ttask done`

**Priority:** P0 | **Effort:** 1h | **Issue:** CC Confession

### Specific Change

This is a subset of T28.9 but called out specifically because CC explicitly used `--force` to bypass AC verification.

### File to Modify

`tools/cli/bpsai_pair/trello/task_commands.py`

### EXACT Changes

```python
# FIND:
@app.command("done")
def done(
    card_id: str,
    summary: str = typer.Option(...),
    strict: bool = typer.Option(False, "--strict"),
    force: bool = typer.Option(False, "--force", help="Force completion"),  # REMOVE
    list_name: str = typer.Option(None, "--list"),
):
    if force:
        # Skip all checks  # REMOVE THIS ENTIRE BLOCK
        pass

# REPLACE WITH:
@app.command("done")
def done(
    card_id: str,
    summary: str = typer.Option(..., help="Summary of work completed"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Verify AC (default: True)"),
    # NO --force flag
    override: bool = typer.Option(False, "--override", help="Override AC check (requires --reason, logged)"),
    reason: Optional[str] = typer.Option(None, "--reason", help="Reason for override"),
    list_name: str = typer.Option("Deployed/Done", "--list", help="Target list (default: Deployed/Done)"),
):
    # Handle override with mandatory reason
    if override:
        if not reason:
            typer.echo("❌ ERROR: --override requires --reason", err=True)
            raise typer.Exit(1)
        log_bypass("ttask_done", card_id, reason, bypass_type="ac_override")
        typer.echo(f"⚠️ AC verification overridden: {reason}")
    elif strict:  # strict is now default True
        # Verify AC - this is the normal path
        unchecked = get_unchecked_items(card_id)
        if unchecked:
            typer.echo("❌ BLOCKED: Acceptance criteria not complete", err=True)
            for item in unchecked:
                typer.echo(f"  - [ ] {item['name']}", err=True)
            raise typer.Exit(1)
```

### Test to Add

```python
def test_force_flag_does_not_exist():
    """--force flag must not exist on ttask done."""
    from click.testing import CliRunner
    runner = CliRunner()
    
    result = runner.invoke(app, ['done', 'TRELLO-123', '--force', '--summary', 'x'])
    
    # Should fail because --force doesn't exist
    assert result.exit_code != 0
    assert "No such option" in result.output or "force" not in result.output
```

### Acceptance Criteria

- [ ] `--force` flag completely removed from `ttask done`
- [ ] `--strict` defaults to `True`
- [ ] `--override` + `--reason` available for legitimate bypasses
- [ ] Override is logged
- [ ] `--list` defaults to "Deployed/Done"
- [ ] All tests pass

---

## T28.11: Remove ALL Other `--force` Flags

**Priority:** P0 | **Effort:** 2h | **Issue:** Comprehensive

### Search for All Force Flags

```bash
grep -rn "force.*=.*typer.Option\|--force" tools/cli/bpsai_pair/
```

### Replace Pattern

For EACH occurrence found:

1. Remove the `--force` flag
2. Add `--override` + `--reason` if bypass is ever legitimate
3. If bypass should NEVER be allowed, remove entirely
4. Update function logic
5. Update tests

### Decision Table

| Command | --force Usage | Replacement |
|---------|---------------|-------------|
| `ttask done` | Skip AC check | `--override --reason` (logged) |
| `init` | Overwrite existing | `--override --reason` (logged) |
| `validate` | Ignore warnings | REMOVE (no bypass allowed) |
| `plan sync-trello` | Skip validation | `--override --reason` (logged) |

### Acceptance Criteria

- [ ] `grep -rn "\-\-force" tools/cli/bpsai_pair/` returns NO results
- [ ] Each former `--force` has documented replacement or removal
- [ ] All overrides use `--override --reason` pattern
- [ ] All overrides logged
- [ ] All tests pass

---

## T28.12: Add Pre-Command Validation Hook

**Priority:** P0 | **Effort:** 4h | **Issue:** R3.1

### Purpose

Validate prerequisites BEFORE any command executes. If validation fails, command is blocked.

### Architecture

```python
# Every command goes through this:
def validate_preconditions(command: str, args: dict) -> Tuple[bool, str]:
    """Check if command is allowed to run.
    
    Returns:
        (allowed, reason) - If not allowed, reason explains why
    """
    
# Validation rules:
PRECONDITIONS = {
    "ttask_start": [
        ("budget_check", "Must run budget check first"),
        ("task_not_in_progress", "Task already started"),
    ],
    "ttask_done": [
        ("task_in_progress", "Task must be started first"),
        ("ac_items_exist", "No acceptance criteria found"),
    ],
    "task_update_done": [
        ("trello_disabled", "Use ttask done for Trello projects"),
    ],
}
```

### File to Create

`tools/cli/bpsai_pair/core/preconditions.py`

```python
"""Pre-command validation.

Ensures commands can only run when prerequisites are met.
"""
from typing import Tuple, Callable, Optional
from functools import wraps

import typer

from bpsai_pair.core.config import load_config


class PreconditionError(Exception):
    """Raised when a precondition is not met."""
    pass


def check_budget_available(task_id: str) -> Tuple[bool, str]:
    """Check if budget allows starting this task."""
    from bpsai_pair.metrics.budget import BudgetManager
    from bpsai_pair.tokens import estimate_task_tokens
    
    budget = BudgetManager()
    estimated = estimate_task_tokens(task_id)
    can_proceed, reason = budget.can_proceed(estimated)
    
    return can_proceed, reason if not can_proceed else ""


def check_task_not_started(task_id: str) -> Tuple[bool, str]:
    """Check task is not already in progress."""
    from bpsai_pair.planning.parser import load_task
    
    try:
        task = load_task(task_id)
        if task.status == "in_progress":
            return False, f"Task {task_id} is already in progress"
        return True, ""
    except FileNotFoundError:
        return True, ""  # Task doesn't exist locally, that's OK


def check_task_in_progress(task_id: str) -> Tuple[bool, str]:
    """Check task is in progress (required for completion)."""
    from bpsai_pair.planning.parser import load_task
    
    try:
        task = load_task(task_id)
        if task.status != "in_progress":
            return False, f"Task {task_id} status is '{task.status}', must be 'in_progress'"
        return True, ""
    except FileNotFoundError:
        return False, f"Task {task_id} not found"


def check_trello_disabled() -> Tuple[bool, str]:
    """Check that Trello is disabled (for local-only commands)."""
    config = load_config()
    if config.trello.enabled:
        return False, "Trello is enabled - use ttask commands instead"
    return True, ""


def check_ac_items_exist(card_id: str) -> Tuple[bool, str]:
    """Check that card has AC checklist."""
    from bpsai_pair.trello.api import get_card_checklists
    
    checklists = get_card_checklists(card_id)
    ac_checklist = next(
        (c for c in checklists if "acceptance" in c["name"].lower() or "ac" in c["name"].lower()),
        None
    )
    
    if not ac_checklist:
        return False, f"Card {card_id} has no Acceptance Criteria checklist"
    if not ac_checklist.get("checkItems"):
        return False, f"Card {card_id} AC checklist is empty"
    
    return True, ""


# Registry of preconditions
PRECONDITIONS = {
    "ttask_start": [
        (check_budget_available, "task_id"),
        (check_task_not_started, "task_id"),
    ],
    "ttask_done": [
        (check_task_in_progress, "task_id"),
        (check_ac_items_exist, "card_id"),
    ],
    "task_update_done": [
        (check_trello_disabled, None),
    ],
}


def validate_preconditions(command: str, **kwargs) -> None:
    """Validate all preconditions for a command.
    
    Args:
        command: Command name (e.g., "ttask_start")
        **kwargs: Arguments to pass to check functions
        
    Raises:
        PreconditionError: If any precondition fails
    """
    checks = PRECONDITIONS.get(command, [])
    
    for check_func, arg_name in checks:
        if arg_name:
            arg_value = kwargs.get(arg_name)
            if not arg_value:
                continue  # Skip if arg not provided
            passed, reason = check_func(arg_value)
        else:
            passed, reason = check_func()
        
        if not passed:
            raise PreconditionError(reason)


def require_preconditions(command: str):
    """Decorator to enforce preconditions on a command.
    
    Usage:
        @require_preconditions("ttask_start")
        def start(card_id: str, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validate_preconditions(command, **kwargs)
            except PreconditionError as e:
                typer.echo(f"❌ BLOCKED: {e}", err=True)
                raise typer.Exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Apply Decorator to Commands

```python
# In trello/task_commands.py:

from bpsai_pair.core.preconditions import require_preconditions

@app.command("start")
@require_preconditions("ttask_start")
def start(card_id: str, ...):
    # Preconditions already verified
    ...

@app.command("done")
@require_preconditions("ttask_done")
def done(card_id: str, ...):
    # Preconditions already verified
    ...
```

### Test Cases

```python
"""Tests for precondition validation."""
import pytest
from bpsai_pair.core.preconditions import (
    validate_preconditions,
    PreconditionError,
    check_task_in_progress,
)


def test_ttask_done_requires_in_progress():
    """ttask done must require task to be in progress."""
    # Setup: task exists but status is 'pending'
    with pytest.raises(PreconditionError) as exc:
        validate_preconditions("ttask_done", task_id="T27.1", card_id="TRELLO-94")
    
    assert "in_progress" in str(exc.value)


def test_ttask_start_requires_budget():
    """ttask start must check budget."""
    # Setup: budget exceeded
    with pytest.raises(PreconditionError) as exc:
        validate_preconditions("ttask_start", task_id="T27.1")
    
    assert "budget" in str(exc.value).lower()


def test_task_update_done_blocked_with_trello():
    """task update --status done blocked when Trello enabled."""
    # Setup: Trello enabled in config
    with pytest.raises(PreconditionError) as exc:
        validate_preconditions("task_update_done")
    
    assert "ttask" in str(exc.value)
```

### Acceptance Criteria

- [ ] `PreconditionError` raised when check fails
- [ ] Commands exit with error code 1 when blocked
- [ ] Clear error message explains what's wrong
- [ ] `@require_preconditions` decorator works on commands
- [ ] All precondition checks implemented
- [ ] All tests pass

---

## T28.13: Create State Machine for Task Execution

**Priority:** P0 | **Effort:** 6h | **Issue:** Sequential Enforcement

### Purpose

Enforce that tasks MUST progress through states in order. No skipping steps.

### State Machine Definition

```
                    ┌─────────────────┐
                    │   NOT_STARTED   │
                    └────────┬────────┘
                             │ ttask start (after budget check)
                             ▼
                    ┌─────────────────┐
                    │  IN_PROGRESS    │
                    └────────┬────────┘
                             │ AC items checked
                             ▼
                    ┌─────────────────┐
                    │  AC_VERIFIED    │
                    └────────┬────────┘
                             │ ttask done --strict
                             ▼
                    ┌─────────────────┐
                    │   COMPLETED     │
                    └─────────────────┘

State transitions:
  NOT_STARTED → IN_PROGRESS: ttask start
  IN_PROGRESS → AC_VERIFIED: all AC items checked (automatic)
  AC_VERIFIED → COMPLETED: ttask done
  IN_PROGRESS → BLOCKED: ttask block (optional)
  BLOCKED → IN_PROGRESS: ttask unblock (optional)
```

### File to Create

`tools/cli/bpsai_pair/core/task_state.py`

```python
"""Task execution state machine.

Enforces that tasks progress through required states in order.
No skipping steps. No going backwards (except to BLOCKED).
"""
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

import typer


class TaskState(Enum):
    """Valid task states."""
    NOT_STARTED = "not_started"
    BUDGET_CHECKED = "budget_checked"
    IN_PROGRESS = "in_progress"
    AC_VERIFIED = "ac_verified"
    COMPLETED = "completed"
    BLOCKED = "blocked"


# Valid state transitions
VALID_TRANSITIONS = {
    TaskState.NOT_STARTED: [TaskState.BUDGET_CHECKED],
    TaskState.BUDGET_CHECKED: [TaskState.IN_PROGRESS],
    TaskState.IN_PROGRESS: [TaskState.AC_VERIFIED, TaskState.BLOCKED],
    TaskState.AC_VERIFIED: [TaskState.COMPLETED],
    TaskState.BLOCKED: [TaskState.IN_PROGRESS],
    TaskState.COMPLETED: [],  # Terminal state
}

# What command triggers each transition
TRANSITION_COMMANDS = {
    (TaskState.NOT_STARTED, TaskState.BUDGET_CHECKED): "budget check",
    (TaskState.BUDGET_CHECKED, TaskState.IN_PROGRESS): "ttask start",
    (TaskState.IN_PROGRESS, TaskState.AC_VERIFIED): "trello check (all AC)",
    (TaskState.AC_VERIFIED, TaskState.COMPLETED): "ttask done --strict",
    (TaskState.IN_PROGRESS, TaskState.BLOCKED): "ttask block",
    (TaskState.BLOCKED, TaskState.IN_PROGRESS): "ttask unblock",
}


class TaskStateManager:
    """Manages task execution states."""
    
    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or Path(".paircoder/task_state.json")
        self._states: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self) -> None:
        """Load state from file."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self._states = data.get("tasks", {})
    
    def _save(self) -> None:
        """Save state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump({"tasks": self._states, "updated": datetime.utcnow().isoformat()}, f, indent=2)
    
    def get_state(self, task_id: str) -> TaskState:
        """Get current state for a task."""
        if task_id not in self._states:
            return TaskState.NOT_STARTED
        return TaskState(self._states[task_id]["state"])
    
    def can_transition(self, task_id: str, target: TaskState) -> tuple[bool, str]:
        """Check if transition is valid.
        
        Returns:
            (allowed, reason) - If not allowed, reason explains why
        """
        current = self.get_state(task_id)
        valid_targets = VALID_TRANSITIONS.get(current, [])
        
        if target in valid_targets:
            return True, ""
        
        # Build helpful error message
        if not valid_targets:
            return False, f"Task {task_id} is in terminal state '{current.value}'"
        
        required_transition = TRANSITION_COMMANDS.get((current, valid_targets[0]), "unknown")
        return False, (
            f"Task {task_id} is in state '{current.value}'. "
            f"Next required step: {required_transition}"
        )
    
    def transition(self, task_id: str, target: TaskState, force: bool = False) -> None:
        """Transition task to new state.
        
        Args:
            task_id: Task identifier
            target: Target state
            force: Allow invalid transitions (LOGGED)
            
        Raises:
            typer.Exit: If transition not allowed and not forced
        """
        allowed, reason = self.can_transition(task_id, target)
        
        if not allowed:
            if force:
                from bpsai_pair.core.bypass_log import log_bypass
                log_bypass(
                    "state_transition",
                    task_id,
                    f"Forced transition to {target.value}: {reason}",
                    bypass_type="state_override"
                )
                typer.echo(f"⚠️ Forced state transition (logged): {reason}", err=True)
            else:
                typer.echo(f"❌ BLOCKED: {reason}", err=True)
                raise typer.Exit(1)
        
        # Record transition
        current = self.get_state(task_id)
        self._states[task_id] = {
            "state": target.value,
            "previous": current.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._save()
        
        typer.echo(f"✓ Task {task_id}: {current.value} → {target.value}")
    
    def require_state(self, task_id: str, required: TaskState) -> None:
        """Verify task is in required state.
        
        Raises:
            typer.Exit: If not in required state
        """
        current = self.get_state(task_id)
        if current != required:
            typer.echo(
                f"❌ BLOCKED: Task {task_id} must be in state '{required.value}' "
                f"but is in '{current.value}'",
                err=True
            )
            raise typer.Exit(1)
    
    def check_ac_verified(self, task_id: str, card_id: str) -> bool:
        """Check if all AC items are verified for a task.
        
        If all checked, automatically transitions to AC_VERIFIED.
        """
        from bpsai_pair.trello.api import get_card_checklists
        
        checklists = get_card_checklists(card_id)
        for checklist in checklists:
            if "acceptance" in checklist["name"].lower():
                for item in checklist.get("checkItems", []):
                    if item["state"] != "complete":
                        return False
        
        # All AC verified - transition
        current = self.get_state(task_id)
        if current == TaskState.IN_PROGRESS:
            self.transition(task_id, TaskState.AC_VERIFIED)
        
        return True


# Global instance
_state_manager: Optional[TaskStateManager] = None


def get_state_manager() -> TaskStateManager:
    """Get global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = TaskStateManager()
    return _state_manager
```

### Integrate with Commands

```python
# In trello/task_commands.py:

from bpsai_pair.core.task_state import get_state_manager, TaskState

@app.command("start")
def start(card_id: str, ...):
    task_id = get_task_id_from_card(card_id)
    state_mgr = get_state_manager()
    
    # Must be in BUDGET_CHECKED state
    state_mgr.require_state(task_id, TaskState.BUDGET_CHECKED)
    
    # ... do the start ...
    
    # Transition to IN_PROGRESS
    state_mgr.transition(task_id, TaskState.IN_PROGRESS)


@app.command("done")
def done(card_id: str, ...):
    task_id = get_task_id_from_card(card_id)
    state_mgr = get_state_manager()
    
    # Must be in AC_VERIFIED state
    state_mgr.require_state(task_id, TaskState.AC_VERIFIED)
    
    # ... do the completion ...
    
    # Transition to COMPLETED
    state_mgr.transition(task_id, TaskState.COMPLETED)
```

### Add Budget Check Integration

```python
# In commands/budget.py:

@app.command("check")
def check(task_id: str = typer.Argument(...)):
    """Check token budget for a task."""
    from bpsai_pair.core.task_state import get_state_manager, TaskState
    
    state_mgr = get_state_manager()
    
    # Must be in NOT_STARTED state
    state_mgr.require_state(task_id, TaskState.NOT_STARTED)
    
    # ... do budget check ...
    
    if budget_ok:
        # Transition to BUDGET_CHECKED
        state_mgr.transition(task_id, TaskState.BUDGET_CHECKED)
        typer.echo(f"✅ Budget approved. Now run: bpsai-pair ttask start ...")
    else:
        typer.echo(f"❌ Budget exceeded. Task not approved to start.")
```

### CLI Command to View State

```python
@app.command("state")
def show_state(task_id: str = typer.Argument(...)):
    """Show current execution state for a task."""
    state_mgr = get_state_manager()
    current = state_mgr.get_state(task_id)
    
    typer.echo(f"Task: {task_id}")
    typer.echo(f"State: {current.value}")
    
    valid_next = VALID_TRANSITIONS.get(current, [])
    if valid_next:
        next_cmd = TRANSITION_COMMANDS.get((current, valid_next[0]), "unknown")
        typer.echo(f"Next step: {next_cmd}")
    else:
        typer.echo("Status: Complete (terminal state)")
```

### Test Cases

```python
"""Tests for task state machine."""
import pytest
from bpsai_pair.core.task_state import TaskStateManager, TaskState


class TestTaskStateMachine:
    
    def test_initial_state_is_not_started(self, tmp_path):
        """New tasks must start in NOT_STARTED state."""
        mgr = TaskStateManager(tmp_path / "state.json")
        assert mgr.get_state("T27.1") == TaskState.NOT_STARTED
    
    def test_valid_transition_allowed(self, tmp_path):
        """Valid transitions must succeed."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        # NOT_STARTED → BUDGET_CHECKED (valid)
        allowed, _ = mgr.can_transition("T27.1", TaskState.BUDGET_CHECKED)
        assert allowed
    
    def test_invalid_transition_blocked(self, tmp_path):
        """Invalid transitions must be blocked."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        # NOT_STARTED → IN_PROGRESS (invalid - must check budget first)
        allowed, reason = mgr.can_transition("T27.1", TaskState.IN_PROGRESS)
        assert not allowed
        assert "budget" in reason.lower()
    
    def test_skip_to_completed_blocked(self, tmp_path):
        """Cannot skip directly to COMPLETED."""
        mgr = TaskStateManager(tmp_path / "state.json")
        
        allowed, reason = mgr.can_transition("T27.1", TaskState.COMPLETED)
        assert not allowed
    
    def test_full_valid_progression(self, tmp_path):
        """Full valid state progression must work."""
        mgr = TaskStateManager(tmp_path / "state.json")
        task = "T27.1"
        
        # Progress through all states
        mgr.transition(task, TaskState.BUDGET_CHECKED)
        assert mgr.get_state(task) == TaskState.BUDGET_CHECKED
        
        mgr.transition(task, TaskState.IN_PROGRESS)
        assert mgr.get_state(task) == TaskState.IN_PROGRESS
        
        mgr.transition(task, TaskState.AC_VERIFIED)
        assert mgr.get_state(task) == TaskState.AC_VERIFIED
        
        mgr.transition(task, TaskState.COMPLETED)
        assert mgr.get_state(task) == TaskState.COMPLETED
    
    def test_state_persisted_to_file(self, tmp_path):
        """State must persist to file."""
        state_file = tmp_path / "state.json"
        
        mgr1 = TaskStateManager(state_file)
        mgr1.transition("T27.1", TaskState.BUDGET_CHECKED)
        
        # New manager reads same file
        mgr2 = TaskStateManager(state_file)
        assert mgr2.get_state("T27.1") == TaskState.BUDGET_CHECKED
```

### Acceptance Criteria

- [ ] `TaskState` enum defines all valid states
- [ ] `VALID_TRANSITIONS` enforces allowed progressions
- [ ] `can_transition()` returns clear error messages
- [ ] `transition()` blocks invalid transitions
- [ ] State persisted to `.paircoder/task_state.json`
- [ ] `ttask start` requires `BUDGET_CHECKED` state
- [ ] `ttask done` requires `AC_VERIFIED` state
- [ ] `bpsai-pair state <task>` shows current state
- [ ] All tests pass

---

## Sprint 28 Summary

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| T28.1 | Make `--strict` default for `ttask done` | 2h | P0 |
| T28.2 | Make `require_review=True` default | 1h | P0 |
| T28.3 | Block `task update --status done` on Trello | 3h | P0 |
| T28.4 | Auto-update local task from `ttask done` | 2h | P0 |
| T28.5 | Wire budget `can_proceed()` before start | 4h | P0 |
| T28.6 | Create `/pc-done` slash command | 2h | P1 |
| T28.7 | Create bypass audit log | 2h | P0 |
| T28.8 | Load and use model routing config | 3h | P1 |
| T28.9 | Add `--override` with mandatory reason | 2h | P0 |
| T28.10 | Remove `--force` from `ttask done` | 1h | P0 |
| T28.11 | Remove ALL `--force` flags | 2h | P0 |
| T28.12 | Add pre-command validation hook | 4h | P0 |
| T28.13 | Create state machine for task execution | 6h | P0 |

**Total Effort:** ~34 hours
**Complexity:** ~400 points

### Execution Order

```
1. T28.7  - Bypass log (needed by everything)
2. T28.10 - Remove --force from ttask done (most critical)
3. T28.11 - Remove all --force flags
4. T28.9  - Add --override pattern
5. T28.1  - Make --strict default
6. T28.3  - Block task update done
7. T28.4  - Auto-sync local task
8. T28.12 - Pre-command validation
9. T28.13 - State machine
10. T28.5 - Wire budget check
11. T28.2 - Review default
12. T28.8 - Model routing
13. T28.6 - /pc-done command
```

### Post-Sprint Verification

```bash
# 1. No --force flags anywhere
grep -rn "\-\-force" tools/cli/bpsai_pair/
# Must return nothing

# 2. State machine works
bpsai-pair ttask done TRELLO-XX --summary "test"
# Must BLOCK (not in AC_VERIFIED state)

# 3. Bypass log exists
cat .paircoder/history/bypass_log.jsonl
# Must exist if any overrides used

# 4. All tests pass
pytest tests/ -v
```

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-12-30 | Claude (claude.ai) | Initial comprehensive task specs |
