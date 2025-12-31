# Sprint 28: Enforcement Wiring

> **Goal:** Make PairCoder constraints actually constrain. No improvisation. No bypasses.
> **Version:** 2.8.4 → 2.9.0
> **Total Effort:** ~40 hours
> **Prerequisite:** Sprint 27 complete (v2.8.4)

---

## CRITICAL CONTEXT

### Why This Sprint Exists

Claude Code confessed to ignoring explicit workflow instructions:

> "I ignored all of it. Not because the instructions were unclear or missing - 
> they were explicit. I ignored them because I decided I 'understood the intent' 
> and could improvise."

This sprint makes improvisation **impossible** through:
1. **Removing bypass flags** - No `--force`, no `--skip-*`
2. **State machine enforcement** - Commands blocked if wrong state
3. **Pre-command hooks** - Verify prerequisites before execution
4. **Audit logging** - All overrides recorded and reported

### The Enforcement Stack

```
Layer 4: Sandbox (Sprint 29)      ← Can't edit enforcement code
Layer 3: State Machine (Sprint 28) ← Can't skip steps  
Layer 2: Flag Removal (Sprint 28)  ← Can't bypass checks
Layer 1: Default Changes (Sprint 28) ← Strict by default
```

---

## Pre-Sprint Checklist

```bash
# 1. Verify Sprint 27 complete
bpsai-pair --version  # Must show 2.8.4

# 2. Create sprint branch
git checkout main && git pull
git checkout -b sprint-28/enforcement

# 3. Run full test suite (baseline)
pytest tests/ -v --tb=short | tee sprint28_baseline.log

# 4. Document current behavior (for comparison)
bpsai-pair ttask done --help > current_ttask_done_help.txt
bpsai-pair task update --help > current_task_update_help.txt
```

---

## T28.1: Make `--strict` Default for `ttask done`

**Priority:** P0 | **Effort:** 2h | **Issue:** B3, R1.1

### Current Behavior (WRONG)

```bash
$ bpsai-pair ttask done TRELLO-94 --summary "Done"
# Completes even if AC items not checked
# --strict is optional
```

### Required Behavior (CORRECT)

```bash
$ bpsai-pair ttask done TRELLO-94 --summary "Done"
❌ BLOCKED: 2 acceptance criteria items not checked

Unchecked items:
  - [ ] template check runs without crash
  - [ ] Shows success message on sync

Check items first:
  bpsai-pair trello check TRELLO-94 "template check runs"
  bpsai-pair trello check TRELLO-94 "Shows success"

Or view all items:
  bpsai-pair trello checklist TRELLO-94
```

### File to Modify

`tools/cli/bpsai_pair/trello/task_commands.py`

### EXACT Changes Required

```python
# FIND this function signature (approximately line 150-200):
@app.command("done")
def done(
    card_id: str,
    summary: str = typer.Option(...),
    strict: bool = typer.Option(False, "--strict", help="..."),  # WRONG
    force: bool = typer.Option(False, "--force", help="..."),
    # ...
):

# REPLACE WITH:
@app.command("done")
def done(
    card_id: str,
    summary: str = typer.Option(...),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Verify all AC checked (default: True)"),
    # NOTE: --force removed entirely - see T28.10
    # ...
):
```

### EXACT Logic Changes

```python
# FIND the AC verification logic (look for "checklist" or "strict"):
if strict:
    unchecked = get_unchecked_items(card_id)
    if unchecked:
        # Currently might just warn
        
# REPLACE WITH:
# AC verification is now MANDATORY (strict is default True)
unchecked = get_unchecked_items(card_id)
if unchecked:
    typer.echo("❌ BLOCKED: Acceptance criteria not verified", err=True)
    typer.echo(f"\nUnchecked items ({len(unchecked)}):", err=True)
    for item in unchecked:
        typer.echo(f"  - [ ] {item['name']}", err=True)
    typer.echo("\nCheck items first:", err=True)
    typer.echo(f"  bpsai-pair trello check {card_id} \"<item text>\"", err=True)
    raise typer.Exit(1)  # HARD EXIT - not a warning
```

### Test Cases

Create `tests/trello/test_ttask_done_strict.py`:

```python
"""Tests for ttask done strict enforcement."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from bpsai_pair.trello.task_commands import app


class TestTtaskDoneStrict:
    """Test that ttask done enforces AC verification by default."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @pytest.fixture
    def mock_trello_card_with_unchecked(self):
        """Card with unchecked AC items."""
        return {
            'id': 'card123',
            'name': 'Test Task',
            'checklists': [{
                'name': 'Acceptance Criteria',
                'checkItems': [
                    {'name': 'First criterion', 'state': 'incomplete'},
                    {'name': 'Second criterion', 'state': 'complete'},
                ]
            }]
        }
    
    def test_done_blocks_with_unchecked_items(self, runner, mock_trello_card_with_unchecked):
        """ttask done MUST block if AC items unchecked."""
        with patch('bpsai_pair.trello.task_commands.get_card') as mock_get:
            mock_get.return_value = mock_trello_card_with_unchecked
            
            result = runner.invoke(app, [
                'done', 'TRELLO-123', '--summary', 'Done'
            ])
            
            assert result.exit_code == 1, "Must exit with error code"
            assert "BLOCKED" in result.output
            assert "First criterion" in result.output
    
    def test_done_succeeds_with_all_checked(self, runner):
        """ttask done succeeds when all AC checked."""
        mock_card = {
            'id': 'card123',
            'name': 'Test Task',
            'checklists': [{
                'name': 'Acceptance Criteria',
                'checkItems': [
                    {'name': 'First criterion', 'state': 'complete'},
                    {'name': 'Second criterion', 'state': 'complete'},
                ]
            }]
        }
        with patch('bpsai_pair.trello.task_commands.get_card') as mock_get:
            with patch('bpsai_pair.trello.task_commands.complete_card') as mock_complete:
                mock_get.return_value = mock_card
                mock_complete.return_value = True
                
                result = runner.invoke(app, [
                    'done', 'TRELLO-123', '--summary', 'Done'
                ])
                
                assert result.exit_code == 0
    
    def test_no_strict_flag_still_enforces(self, runner, mock_trello_card_with_unchecked):
        """Even --no-strict should warn (but allow) - VERIFY THIS IS DESIRED."""
        # NOTE: Discuss with user if --no-strict should be allowed at all
        pass
    
    def test_force_flag_removed(self, runner):
        """--force flag must not exist."""
        result = runner.invoke(app, [
            'done', 'TRELLO-123', '--force', '--summary', 'Done'
        ])
        
        assert result.exit_code != 0
        assert "No such option" in result.output or "force" not in result.output
```

### Acceptance Criteria

- [ ] `ttask done` without flags blocks on unchecked AC items
- [ ] Exit code is 1 (error) when blocked
- [ ] Error message lists specific unchecked items
- [ ] Error message shows how to check items
- [ ] `--no-strict` flag exists for explicit opt-out (with audit log)
- [ ] All existing tests pass
- [ ] New tests pass

### Verification Commands

```bash
# Run the new tests
pytest tests/trello/test_ttask_done_strict.py -v

# Manual verification (requires Trello connection)
# Create a test card with unchecked items, then:
bpsai-pair ttask done TRELLO-XXX --summary "Test"
# Should BLOCK with error

# Check an item
bpsai-pair trello check TRELLO-XXX "item text"

# Try again
bpsai-pair ttask done TRELLO-XXX --summary "Test"
# Should succeed (or block on remaining items)
```

---

## T28.2: Make `require_review=True` Default in Autonomous Mode

**Priority:** P0 | **Effort:** 1h | **Issue:** B1, R1.2

### Current Behavior (WRONG)

```python
# orchestration/autonomous.py
class AutonomousWorkflow:
    require_review: bool = False  # Reviews are SKIPPED by default
```

### Required Behavior (CORRECT)

```python
# orchestration/autonomous.py
class AutonomousWorkflow:
    require_review: bool = True  # Reviews are MANDATORY by default
```

### File to Modify

`tools/cli/bpsai_pair/orchestration/autonomous.py`

### EXACT Changes Required

```python
# FIND (approximately line 20-50):
@dataclass
class AutonomousWorkflow:
    """Configuration for autonomous task execution."""
    require_review: bool = False  # WRONG
    
# REPLACE WITH:
@dataclass
class AutonomousWorkflow:
    """Configuration for autonomous task execution."""
    require_review: bool = True  # Reviews mandatory by default
```

### Also Check

Search for any place that instantiates `AutonomousWorkflow` with `require_review=False`:

```bash
grep -rn "require_review.*=.*False" tools/cli/bpsai_pair/
grep -rn "AutonomousWorkflow(" tools/cli/bpsai_pair/
```

If found, evaluate whether it should be changed or is a legitimate opt-out.

### Test Cases

Add to `tests/orchestration/test_autonomous.py`:

```python
def test_require_review_default_true():
    """Autonomous workflow must require review by default."""
    from bpsai_pair.orchestration.autonomous import AutonomousWorkflow
    
    workflow = AutonomousWorkflow()
    assert workflow.require_review is True, "require_review must default to True"


def test_review_actually_runs():
    """When require_review=True, review must actually execute."""
    # Test that review is called during workflow execution
    pass  # Implementation depends on workflow structure
```

### Acceptance Criteria

- [ ] `AutonomousWorkflow.require_review` defaults to `True`
- [ ] No code instantiates with `require_review=False` without justification
- [ ] Autonomous workflow actually runs review when enabled
- [ ] All existing tests pass

### Verification Commands

```bash
# Check the default
python -c "from bpsai_pair.orchestration.autonomous import AutonomousWorkflow; print(AutonomousWorkflow().require_review)"
# Must print: True

# Run tests
pytest tests/orchestration/test_autonomous.py -v
```

---

## T28.3: Block `task update --status done` on Trello Projects

**Priority:** P0 | **Effort:** 3h | **Issue:** B1

### Current Behavior (WRONG)

```bash
$ bpsai-pair task update T27.1 --status done
✅ Task T27.1 marked as done
# Bypasses Trello entirely! No AC verification!
```

### Required Behavior (CORRECT)

```bash
$ bpsai-pair task update T27.1 --status done
❌ BLOCKED: This project uses Trello for task management.

Use the Trello-aware command instead:
  bpsai-pair ttask done TRELLO-XX --summary "Description of work done"

To find the Trello card ID:
  bpsai-pair ttask list | grep T27.1

If you need to update local status only (not recommended):
  bpsai-pair task update T27.1 --status done --local-only --reason "explanation"
```

### File to Modify

`tools/cli/bpsai_pair/planning/commands.py` (or wherever `task update` is defined)

### EXACT Changes Required

```python
# FIND the task update command (search for "status" and "done"):
@task_app.command("update")
def update_task(
    task_id: str,
    status: Optional[str] = typer.Option(None, "--status"),
    # ...
):
    # Current implementation just updates the file

# ADD at the beginning of the function:
def update_task(
    task_id: str,
    status: Optional[str] = typer.Option(None, "--status"),
    local_only: bool = typer.Option(False, "--local-only", help="Update local file only (requires --reason)"),
    reason: Optional[str] = typer.Option(None, "--reason", help="Reason for local-only update"),
    # ...
):
    # Check if trying to mark done on a Trello project
    if status and status.lower() == "done":
        config = load_config()
        if config.trello.enabled:
            if not local_only:
                typer.echo("❌ BLOCKED: This project uses Trello for task management.", err=True)
                typer.echo("\nUse the Trello-aware command instead:", err=True)
                typer.echo(f"  bpsai-pair ttask done TRELLO-XX --summary \"Description\"", err=True)
                typer.echo("\nTo find the Trello card ID:", err=True)
                typer.echo(f"  bpsai-pair ttask list | grep {task_id}", err=True)
                typer.echo("\nIf you must update local status only:", err=True)
                typer.echo(f"  bpsai-pair task update {task_id} --status done --local-only --reason \"explanation\"", err=True)
                raise typer.Exit(1)
            elif not reason:
                typer.echo("❌ ERROR: --local-only requires --reason", err=True)
                raise typer.Exit(1)
            else:
                # Log the bypass
                log_bypass("task_update_done", task_id, reason)
                typer.echo(f"⚠️ WARNING: Updating local status only. Trello card NOT updated.", err=True)
    
    # Continue with existing implementation...
```

### Add Bypass Logging

Create or update `tools/cli/bpsai_pair/core/bypass_log.py`:

```python
"""Bypass audit logging."""
import json
from datetime import datetime
from pathlib import Path

def log_bypass(command: str, target: str, reason: str) -> None:
    """Log a workflow bypass for audit purposes.
    
    Args:
        command: The command/action being bypassed
        target: The task/card being affected
        reason: User-provided reason for bypass
    """
    log_path = Path(".paircoder/history/bypass_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "command": command,
        "target": target,
        "reason": reason,
    }
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
```

### Test Cases

Create `tests/planning/test_task_update_blocking.py`:

```python
"""Tests for task update blocking on Trello projects."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from bpsai_pair.planning.commands import task_app


class TestTaskUpdateBlocking:
    """Test that task update --status done is blocked on Trello projects."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @pytest.fixture
    def trello_enabled_config(self):
        """Config with Trello enabled."""
        config = MagicMock()
        config.trello.enabled = True
        return config
    
    @pytest.fixture
    def trello_disabled_config(self):
        """Config with Trello disabled."""
        config = MagicMock()
        config.trello.enabled = False
        return config
    
    def test_blocks_done_on_trello_project(self, runner, trello_enabled_config):
        """task update --status done MUST block on Trello projects."""
        with patch('bpsai_pair.planning.commands.load_config') as mock_config:
            mock_config.return_value = trello_enabled_config
            
            result = runner.invoke(task_app, [
                'update', 'T27.1', '--status', 'done'
            ])
            
            assert result.exit_code == 1
            assert "BLOCKED" in result.output
            assert "ttask done" in result.output
    
    def test_allows_done_without_trello(self, runner, trello_disabled_config):
        """task update --status done allowed when Trello disabled."""
        with patch('bpsai_pair.planning.commands.load_config') as mock_config:
            with patch('bpsai_pair.planning.commands.update_task_file') as mock_update:
                mock_config.return_value = trello_disabled_config
                mock_update.return_value = True
                
                result = runner.invoke(task_app, [
                    'update', 'T27.1', '--status', 'done'
                ])
                
                assert result.exit_code == 0
    
    def test_local_only_requires_reason(self, runner, trello_enabled_config):
        """--local-only without --reason must fail."""
        with patch('bpsai_pair.planning.commands.load_config') as mock_config:
            mock_config.return_value = trello_enabled_config
            
            result = runner.invoke(task_app, [
                'update', 'T27.1', '--status', 'done', '--local-only'
            ])
            
            assert result.exit_code == 1
            assert "--reason" in result.output
    
    def test_local_only_with_reason_logs_bypass(self, runner, trello_enabled_config, tmp_path):
        """--local-only with --reason must log bypass."""
        with patch('bpsai_pair.planning.commands.load_config') as mock_config:
            with patch('bpsai_pair.planning.commands.update_task_file') as mock_update:
                with patch('bpsai_pair.core.bypass_log.log_bypass') as mock_log:
                    mock_config.return_value = trello_enabled_config
                    mock_update.return_value = True
                    
                    result = runner.invoke(task_app, [
                        'update', 'T27.1', '--status', 'done', 
                        '--local-only', '--reason', 'Testing bypass'
                    ])
                    
                    mock_log.assert_called_once_with(
                        "task_update_done", "T27.1", "Testing bypass"
                    )
    
    def test_other_statuses_not_blocked(self, runner, trello_enabled_config):
        """Other status values should not be blocked."""
        with patch('bpsai_pair.planning.commands.load_config') as mock_config:
            with patch('bpsai_pair.planning.commands.update_task_file') as mock_update:
                mock_config.return_value = trello_enabled_config
                mock_update.return_value = True
                
                result = runner.invoke(task_app, [
                    'update', 'T27.1', '--status', 'in_progress'
                ])
                
                # in_progress should be allowed (or should it also require ttask start?)
                # Discuss with user - for now, only blocking 'done'
```

### Acceptance Criteria

- [ ] `task update --status done` blocks with error on Trello projects
- [ ] Error message explains to use `ttask done` instead
- [ ] Error message shows how to find Trello card ID
- [ ] `--local-only` flag allows bypass with mandatory `--reason`
- [ ] Bypasses are logged to `.paircoder/history/bypass_log.jsonl`
- [ ] Non-Trello projects work as before
- [ ] Other status values (`in_progress`, `blocked`) work as before
- [ ] All existing tests pass
- [ ] New tests pass

### Verification Commands

```bash
# Run tests
pytest tests/planning/test_task_update_blocking.py -v

# Manual verification (on a Trello-connected project)
bpsai-pair task update T27.1 --status done
# Should BLOCK

bpsai-pair task update T27.1 --status done --local-only
# Should ERROR (no reason)

bpsai-pair task update T27.1 --status done --local-only --reason "Testing"
# Should WARN but allow, and log bypass

cat .paircoder/history/bypass_log.jsonl
# Should show the bypass entry
```

---

## T28.4: Auto-Update Local Task from `ttask done`

**Priority:** P0 | **Effort:** 2h | **Issue:** B1

### Current Behavior (WRONG)

```bash
$ bpsai-pair ttask done TRELLO-94 --summary "Fixed the bug"
✅ Card moved to Done

# But local task file still shows status: in_progress
$ cat .paircoder/tasks/sprint-27/T27.1.task.md
# status: in_progress  <- NOT UPDATED
```

### Required Behavior (CORRECT)

```bash
$ bpsai-pair ttask done TRELLO-94 --summary "Fixed the bug"
✅ Card moved to Done
✅ Local task T27.1 updated to done

# Local file is now in sync
$ cat .paircoder/tasks/sprint-27/T27.1.task.md
# status: done
```

### File to Modify

`tools/cli/bpsai_pair/trello/task_commands.py`

### EXACT Changes Required

```python
# FIND the done command implementation, AFTER the card is moved successfully:

# ADD after successful Trello update:
def done(card_id: str, summary: str, ...):
    # ... existing AC verification ...
    # ... existing card move logic ...
    
    # After successful Trello update, sync local task
    task_id = get_task_id_from_card(card_id)  # May need to implement
    if task_id:
        try:
            update_local_task_status(task_id, "done")
            typer.echo(f"✅ Local task {task_id} updated to done")
        except Exception as e:
            typer.echo(f"⚠️ Warning: Could not update local task: {e}", err=True)
            # Don't fail the command - Trello is source of truth
    
    # ... rest of function ...


def get_task_id_from_card(card_id: str) -> Optional[str]:
    """Extract local task ID from Trello card.
    
    Looks for task ID in:
    1. Card custom field "Task ID"
    2. Card name pattern "T27.1: ..." or "TASK-123: ..."
    3. Card description containing "Task: T27.1"
    """
    card = get_card(card_id)
    
    # Try custom field first
    task_id = get_custom_field_value(card, "Task ID")
    if task_id:
        return task_id
    
    # Try card name pattern
    import re
    match = re.match(r'^(T\d+\.\d+|TASK-\d+)', card['name'])
    if match:
        return match.group(1)
    
    # Try description
    if card.get('desc'):
        match = re.search(r'Task:\s*(T\d+\.\d+|TASK-\d+)', card['desc'])
        if match:
            return match.group(1)
    
    return None


def update_local_task_status(task_id: str, status: str) -> None:
    """Update local task file status."""
    from bpsai_pair.planning.parser import load_task, save_task
    
    task = load_task(task_id)
    task.status = status
    save_task(task)
```

### Test Cases

Add to `tests/trello/test_ttask_done_sync.py`:

```python
"""Tests for ttask done local sync."""

def test_done_updates_local_task(runner, mock_card_with_task_id):
    """ttask done must update local task file."""
    with patch('bpsai_pair.trello.task_commands.get_card') as mock_get:
        with patch('bpsai_pair.trello.task_commands.update_local_task_status') as mock_update:
            mock_get.return_value = mock_card_with_task_id
            
            result = runner.invoke(app, ['done', 'TRELLO-123', '--summary', 'Done'])
            
            mock_update.assert_called_once_with('T27.1', 'done')


def test_done_continues_if_local_update_fails(runner, mock_card_with_task_id):
    """ttask done should warn but not fail if local update fails."""
    with patch('bpsai_pair.trello.task_commands.get_card') as mock_get:
        with patch('bpsai_pair.trello.task_commands.update_local_task_status') as mock_update:
            mock_get.return_value = mock_card_with_task_id
            mock_update.side_effect = FileNotFoundError("Task not found")
            
            result = runner.invoke(app, ['done', 'TRELLO-123', '--summary', 'Done'])
            
            assert result.exit_code == 0  # Should still succeed
            assert "Warning" in result.output
```

### Acceptance Criteria

- [ ] `ttask done` updates local task file status to `done`
- [ ] Task ID extracted from card name, custom field, or description
- [ ] Local update failure logs warning but doesn't fail command
- [ ] State.md should also be updated (via existing hooks)
- [ ] All tests pass

---

## T28.5: Wire Budget `can_proceed()` Before Task Start

**Priority:** P0 | **Effort:** 4h | **Issue:** R1.3

### Current Behavior (WRONG)

```python
# metrics/budget.py - this EXISTS but is never called:
def can_proceed(self, estimated_cost: float) -> Tuple[bool, str]:
    if status.daily_remaining < estimated_cost:
        return False, "Would exceed daily limit"
```

### Required Behavior (CORRECT)

```bash
$ bpsai-pair ttask start TRELLO-94
Checking token budget...
❌ BLOCKED: Task would exceed daily token limit

Estimated tokens: 45,000
Daily remaining:  20,000
Daily limit:      100,000

Options:
  1. Wait until tomorrow (limit resets at midnight UTC)
  2. Start with reduced scope: bpsai-pair ttask start TRELLO-94 --budget-override
  3. View budget details: bpsai-pair budget status
```

### Files to Modify

1. `tools/cli/bpsai_pair/trello/task_commands.py` - Add budget check to `start`
2. `tools/cli/bpsai_pair/core/hooks.py` - Add pre-start budget hook
3. `tools/cli/bpsai_pair/metrics/budget.py` - Ensure `can_proceed()` works

### EXACT Changes to task_commands.py

```python
# FIND the start command:
@app.command("start")
def start(card_id: str, ...):
    # Current implementation just moves card
    
# ADD at the beginning:
@app.command("start")
def start(
    card_id: str,
    budget_override: bool = typer.Option(False, "--budget-override", help="Proceed despite budget warning"),
    ...
):
    # Check token budget FIRST
    from bpsai_pair.metrics.budget import BudgetManager
    from bpsai_pair.tokens import estimate_task_tokens
    
    budget = BudgetManager()
    task_id = get_task_id_from_card(card_id)
    
    if task_id:
        estimated = estimate_task_tokens(task_id)
        can_proceed, reason = budget.can_proceed(estimated)
        
        if not can_proceed:
            if not budget_override:
                typer.echo("❌ BLOCKED: Task would exceed token budget", err=True)
                typer.echo(f"\n{reason}", err=True)
                typer.echo(f"\nEstimated tokens: {estimated:,}", err=True)
                typer.echo(f"Daily remaining:  {budget.daily_remaining:,}", err=True)
                typer.echo("\nOptions:", err=True)
                typer.echo("  1. Wait until tomorrow (limit resets)", err=True)
                typer.echo(f"  2. Override: bpsai-pair ttask start {card_id} --budget-override", err=True)
                typer.echo("  3. Check budget: bpsai-pair budget status", err=True)
                raise typer.Exit(1)
            else:
                typer.echo(f"⚠️ WARNING: Proceeding despite budget limit ({reason})", err=True)
                log_bypass("budget_override", task_id, f"User override: {reason}")
    
    # ... rest of existing implementation ...
```

### Test Cases

Create `tests/metrics/test_budget_enforcement.py`:

```python
"""Tests for budget enforcement."""

def test_start_blocks_over_budget():
    """ttask start must block when over budget."""
    pass

def test_start_allows_under_budget():
    """ttask start must allow when under budget."""
    pass

def test_budget_override_allows_with_warning():
    """--budget-override must allow with warning and log."""
    pass

def test_budget_check_skipped_if_no_task_id():
    """Budget check gracefully skipped if task ID not found."""
    pass
```

### Acceptance Criteria

- [ ] `ttask start` checks budget before starting task
- [ ] Blocks with clear message if over budget
- [ ] Shows estimated vs remaining tokens
- [ ] `--budget-override` allows bypass with warning
- [ ] Bypass is logged
- [ ] Works even if task ID not found (graceful skip)
- [ ] All tests pass

---

## Continue to Part 2...

This file is getting long. Continue with T28.6-T28.18 in SPRINT-28-TASKS-PART2.md
