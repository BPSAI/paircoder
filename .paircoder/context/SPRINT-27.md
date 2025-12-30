# Sprint 27: Stabilization Tasks

> **Goal:** CI green, upgrade command works, no blocking bugs
> **Version:** 2.8.3 → 2.8.4
> **Total Effort:** ~22 hours
> **Start Date:** 2024-12-30

---

## Pre-Sprint Checklist

Before starting any tasks:

```bash
# 1. Ensure you're on latest main
cd /path/to/paircoder
git checkout main
git pull origin main

# 2. Create sprint branch
git checkout -b sprint-27/stabilization

# 3. Verify current state
bpsai-pair --version  # Should show 2.8.3
pytest tests/ -x --tb=short  # Run tests, stop on first failure

# 4. Check CI status
# Visit: https://github.com/BPSAI/paircoder/actions
```

---

## T27.1: Fix `template check` Crash

**Priority:** P0 | **Effort:** 2h | **Issue:** K1

### Problem

`bpsai-pair template check` crashes instead of reporting template drift gracefully.

### Symptoms

```bash
$ bpsai-pair template check
Traceback (most recent call last):
  File "...", line XXX, in ...
  [Error details]
```

### Investigation Steps

```bash
# 1. Reproduce the error
bpsai-pair template check

# 2. Find the command implementation
grep -rn "def check" tools/cli/bpsai_pair/release/template.py

# 3. Check for missing imports or None handling
cat tools/cli/bpsai_pair/release/template.py
```

### Likely Causes

1. **Missing file handling** - Template file doesn't exist but code assumes it does
2. **Path resolution error** - Cookiecutter template path not found
3. **None value** - Variable is None when code expects a value

### Files to Check

- `tools/cli/bpsai_pair/release/template.py` - Main command
- `tools/cli/bpsai_pair/core/config.py` - Config loading
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` - Template location

### Fix Pattern

```python
# Before (crashes)
def check():
    template_path = get_template_path()
    files = list(template_path.glob("**/*"))  # Crashes if template_path is None
    
# After (graceful)
def check():
    template_path = get_template_path()
    if template_path is None or not template_path.exists():
        typer.echo("❌ Template directory not found", err=True)
        typer.echo(f"   Expected: {template_path}")
        raise typer.Exit(1)
    files = list(template_path.glob("**/*"))
```

### Acceptance Criteria

- [ ] `bpsai-pair template check` runs without crashing
- [ ] If templates are in sync: Shows success message
- [ ] If templates are out of sync: Shows diff/list of drifted files
- [ ] If template dir missing: Shows helpful error message
- [ ] Exit code 0 on success, 1 on drift/error

### Test Commands

```bash
# Should not crash
bpsai-pair template check

# Should show help
bpsai-pair template check --help

# Run unit tests for template module
pytest tests/release/test_template.py -v
```

### Verification

```bash
# After fix, this should work:
$ bpsai-pair template check
✅ Templates in sync (or)
⚠️ Template drift detected:
  - .paircoder/config.yaml (modified)
  - .claude/skills/design-plan-implement/SKILL.md (missing)
```

---

## T27.2: Fix Smoke Test Failure

**Priority:** P0 | **Effort:** 2h | **Issue:** K2

### Problem

The smoke test suite fails, blocking CI.

### Investigation Steps

```bash
# 1. Run the smoke tests
pytest tests/smoke/ -v

# 2. Or if there's a specific smoke test command
bpsai-pair smoke-test

# 3. Check CI logs for the specific failure
# Visit: https://github.com/BPSAI/paircoder/actions
# Find the failing workflow, expand the test step
```

### Likely Causes

1. **Import error** - Module refactoring broke an import
2. **Missing fixture** - Test expects fixture that was removed/renamed
3. **Config change** - Test expects old config format
4. **Path change** - Hardcoded path no longer valid

### Files to Check

```bash
# Find smoke test files
find tests/ -name "*smoke*" -type f

# Check for recent changes to test fixtures
git log --oneline -10 -- tests/

# Check conftest for fixtures
cat tests/conftest.py
```

### Fix Pattern

Depends on the specific error. Common fixes:

```python
# Import error fix
# Before
from bpsai_pair.cli import some_function  # Moved!

# After  
from bpsai_pair.commands.core import some_function

# ---

# Missing fixture fix
# Before
def test_something(old_fixture_name):
    
# After
def test_something(new_fixture_name):

# ---

# Path fix
# Before
TEMPLATE_PATH = Path("tools/cli/bpsai_pair/templates")

# After
TEMPLATE_PATH = Path("tools/cli/bpsai_pair/data/cookiecutter-paircoder")
```

### Acceptance Criteria

- [ ] `pytest tests/smoke/ -v` passes all tests
- [ ] CI smoke test job passes
- [ ] No import errors
- [ ] No fixture errors

### Test Commands

```bash
# Run smoke tests
pytest tests/smoke/ -v

# Run with coverage
pytest tests/smoke/ -v --cov=bpsai_pair

# Run full test suite to ensure no regressions
pytest tests/ -x --tb=short
```

### Verification

```bash
$ pytest tests/smoke/ -v
================================= test session starts =================================
...
tests/smoke/test_cli.py::test_version PASSED
tests/smoke/test_cli.py::test_init PASSED
tests/smoke/test_cli.py::test_status PASSED
================================= X passed in Y.YYs =================================
```

---

## T27.3: Fix Unicode Errors in Trello

**Priority:** P0 | **Effort:** 2h | **Issue:** K3

### Problem

Trello operations fail when card titles or descriptions contain Unicode characters (emojis, non-ASCII text).

### Symptoms

```bash
$ bpsai-pair ttask show TRELLO-123
UnicodeEncodeError: 'ascii' codec can't encode character '\U0001f680' in position 5
```

Or:
```bash
$ bpsai-pair plan sync-trello my-plan
Error: 'charmap' codec can't encode characters in position 10-15
```

### Investigation Steps

```bash
# 1. Find a Trello card with Unicode (emoji in title)
# 2. Try to fetch it
bpsai-pair ttask list

# 3. Check the Trello module for encoding issues
grep -rn "encode\|decode\|ascii\|utf" tools/cli/bpsai_pair/trello/

# 4. Look for print statements without encoding
grep -rn "print\|echo\|typer.echo" tools/cli/bpsai_pair/trello/
```

### Likely Causes

1. **Print without encoding** - Printing Unicode to console that doesn't support it
2. **File write without encoding** - Writing to file without `encoding='utf-8'`
3. **API response handling** - Not properly decoding Trello API responses
4. **Windows console** - Windows cmd.exe has limited Unicode support

### Files to Check

- `tools/cli/bpsai_pair/trello/commands.py`
- `tools/cli/bpsai_pair/trello/task_commands.py`
- `tools/cli/bpsai_pair/trello/sync.py`
- `tools/cli/bpsai_pair/trello/activity.py`

### Fix Pattern

```python
# Fix 1: File writing
# Before
with open(path, 'w') as f:
    f.write(content)

# After
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# ---

# Fix 2: Console output (Windows-safe)
# Before
typer.echo(card.name)  # May fail on Windows with emoji

# After
try:
    typer.echo(card.name)
except UnicodeEncodeError:
    # Fallback for terminals that can't handle Unicode
    typer.echo(card.name.encode('ascii', 'replace').decode('ascii'))

# ---

# Fix 3: Better approach - use Rich library
from rich.console import Console
console = Console()
console.print(card.name)  # Handles Unicode properly

# ---

# Fix 4: JSON handling
# Before
json.dumps(data)

# After
json.dumps(data, ensure_ascii=False)
```

### Acceptance Criteria

- [ ] Cards with emojis in titles display correctly
- [ ] Cards with non-ASCII characters (é, ñ, 日本語) work
- [ ] `ttask list` works with Unicode cards
- [ ] `ttask show` works with Unicode cards
- [ ] `plan sync-trello` handles Unicode descriptions
- [ ] Works on Windows, Mac, and Linux

### Test Commands

```bash
# Create a test card with Unicode via Trello web UI
# Title: "🚀 Test Unicode Card"
# Description: "Testing émojis and spëcial çharacters 日本語"

# Then test:
bpsai-pair ttask list
bpsai-pair ttask show TRELLO-XXX

# Run Trello-related tests
pytest tests/trello/ -v -k "unicode or encoding"

# If no specific tests exist, run all Trello tests
pytest tests/trello/ -v
```

### Verification

```bash
$ bpsai-pair ttask list
┌────────────┬──────────────────────────────┬──────────┐
│ Card ID    │ Title                        │ Status   │
├────────────┼──────────────────────────────┼──────────┤
│ TRELLO-123 │ 🚀 Test Unicode Card         │ Ready    │
│ TRELLO-124 │ Fix café ordering système    │ Done     │
└────────────┴──────────────────────────────┴──────────┘
```

---

## T27.4: Fix `upgrade` Source File Resolution

**Priority:** P0 | **Effort:** 4h | **Issue:** K13, K14

### Problem

`bpsai-pair upgrade` can't find source files to copy because it looks in the wrong location.

### Symptoms

```bash
$ bpsai-pair upgrade
Upgrading PairCoder...
❌ Source files not found
   Expected: /some/wrong/path
```

### Investigation Steps

```bash
# 1. Run upgrade and capture the error
bpsai-pair upgrade 2>&1 | tee upgrade_error.log

# 2. Find the upgrade command implementation
cat tools/cli/bpsai_pair/commands/upgrade.py

# 3. Check how it resolves paths
grep -n "Path\|__file__\|pkg_resources\|importlib" tools/cli/bpsai_pair/commands/upgrade.py
```

### Likely Causes

1. **Installed vs development mode** - Path works in dev but not when pip-installed
2. **Package data not included** - Files not in `package_data` in pyproject.toml
3. **Relative path assumption** - Code assumes running from repo root

### Files to Check

- `tools/cli/bpsai_pair/commands/upgrade.py` - Main command
- `tools/cli/pyproject.toml` - Package configuration
- `tools/cli/bpsai_pair/data/` - Data files location

### Fix Pattern

```python
# Before (fragile path resolution)
def get_source_path():
    return Path(__file__).parent.parent / "data" / "cookiecutter-paircoder"

# After (robust package data resolution)
import importlib.resources as pkg_resources

def get_source_path():
    """Get path to package data, works in both dev and installed mode."""
    # Try importlib.resources first (Python 3.9+)
    try:
        with pkg_resources.files('bpsai_pair.data') as data_path:
            source = data_path / 'cookiecutter-paircoder'
            if source.exists():
                return source
    except (TypeError, FileNotFoundError):
        pass
    
    # Fallback to __file__ based resolution (dev mode)
    dev_path = Path(__file__).parent.parent / "data" / "cookiecutter-paircoder"
    if dev_path.exists():
        return dev_path
    
    # Last resort: check common locations
    for path in [
        Path.home() / ".local" / "share" / "paircoder" / "templates",
        Path("/usr/share/paircoder/templates"),
    ]:
        if path.exists():
            return path
    
    return None
```

### Also Check pyproject.toml

```toml
[tool.setuptools.package-data]
bpsai_pair = [
    "data/**/*",
    "data/cookiecutter-paircoder/**/*",
]
```

### Acceptance Criteria

- [ ] `bpsai-pair upgrade` finds source files when pip-installed
- [ ] `bpsai-pair upgrade` finds source files in dev mode
- [ ] Clear error message if files not found
- [ ] Works on all platforms (Windows, Mac, Linux)

### Test Commands

```bash
# Test in dev mode
bpsai-pair upgrade --dry-run  # If flag exists

# Test installed mode
pip install -e tools/cli/
bpsai-pair upgrade --dry-run

# Run upgrade tests
pytest tests/commands/test_upgrade.py -v
```

---

## T27.5: Fix `upgrade` to Actually Copy Files

**Priority:** P0 | **Effort:** 3h | **Issue:** K13

**Depends on:** T27.4

### Problem

Even when source files are found, `upgrade` doesn't copy skills, agents, commands, and docs.

### Symptoms

```bash
$ bpsai-pair upgrade
Upgrading PairCoder...
✅ Config updated

$ ls .claude/skills/
# Empty or missing new skills
```

### Investigation Steps

```bash
# 1. Check what upgrade currently does
cat tools/cli/bpsai_pair/commands/upgrade.py

# 2. Look for copy operations
grep -n "copy\|shutil\|move" tools/cli/bpsai_pair/commands/upgrade.py

# 3. Compare source and target directories
diff -r path/to/source/.claude/ .claude/
```

### What Should Be Copied

```
Source (package data)          →  Target (project)
─────────────────────────────────────────────────
.claude/skills/                →  .claude/skills/
.claude/agents/                →  .claude/agents/
.claude/commands/              →  .claude/commands/
.paircoder/capabilities.yaml   →  .paircoder/capabilities.yaml
CLAUDE.md (template)           →  CLAUDE.md (if not customized)
AGENTS.md (template)           →  AGENTS.md (if not customized)
```

### Fix Pattern

```python
import shutil
from pathlib import Path

def upgrade_project(project_root: Path, source_root: Path, force: bool = False):
    """Upgrade a project with latest PairCoder files."""
    
    # Define what to copy
    copy_map = {
        # (source_relative, target_relative, merge_strategy)
        (".claude/skills", ".claude/skills", "merge"),      # Add new, keep existing
        (".claude/agents", ".claude/agents", "merge"),
        (".claude/commands", ".claude/commands", "merge"),
        (".paircoder/capabilities.yaml", ".paircoder/capabilities.yaml", "replace"),
    }
    
    for source_rel, target_rel, strategy in copy_map:
        source = source_root / source_rel
        target = project_root / target_rel
        
        if not source.exists():
            typer.echo(f"⚠️ Source not found: {source_rel}", err=True)
            continue
        
        if source.is_dir():
            copy_directory(source, target, strategy, force)
        else:
            copy_file(source, target, strategy, force)
    
    typer.echo("✅ Upgrade complete!")


def copy_directory(source: Path, target: Path, strategy: str, force: bool):
    """Copy directory with merge strategy."""
    target.mkdir(parents=True, exist_ok=True)
    
    for item in source.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(source)
            target_file = target / rel_path
            
            if target_file.exists() and not force:
                if strategy == "merge":
                    typer.echo(f"  ⏭️ Skipping existing: {rel_path}")
                    continue
                elif strategy == "replace":
                    typer.echo(f"  🔄 Replacing: {rel_path}")
            
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
            typer.echo(f"  ✅ Copied: {rel_path}")
```

### Acceptance Criteria

- [ ] `bpsai-pair upgrade` copies new skills
- [ ] `bpsai-pair upgrade` copies new agents
- [ ] `bpsai-pair upgrade` copies new commands
- [ ] `bpsai-pair upgrade` updates capabilities.yaml
- [ ] Existing customized files are NOT overwritten (unless --force)
- [ ] Summary shows what was copied/skipped

### Test Commands

```bash
# Create a test project
mkdir /tmp/test-upgrade && cd /tmp/test-upgrade
bpsai-pair init --preset minimal

# Remove some files to simulate old version
rm -rf .claude/skills/paircoder-task-lifecycle

# Run upgrade
bpsai-pair upgrade

# Verify files were copied
ls -la .claude/skills/
ls -la .claude/agents/
ls -la .claude/commands/
```

### Verification

```bash
$ bpsai-pair upgrade
🔄 Upgrading PairCoder to v2.8.4...

Skills:
  ✅ Copied: design-plan-implement/SKILL.md
  ✅ Copied: paircoder-task-lifecycle/SKILL.md
  ⏭️ Skipping existing: tdd-implement/SKILL.md

Agents:
  ✅ Copied: security-auditor.md
  ⏭️ Skipping existing: planner.md

Commands:
  ✅ Copied: pc-plan.md
  ✅ Copied: start-task.md

Config:
  🔄 Updated: capabilities.yaml

✅ Upgrade complete! Run 'bpsai-pair status' to verify.
```

---

## T27.6: Fix Windows Hook Compatibility

**Priority:** P0 | **Effort:** 2h | **Issue:** K15

### Problem

Hooks use `|| true` bash syntax which fails on Windows cmd.exe.

### Symptoms

```cmd
C:\project> bpsai-pair task update T1 --status done
'true' is not recognized as an internal or external command
```

### Investigation Steps

```bash
# Find all uses of || true
grep -rn "|| true\||| exit" tools/cli/bpsai_pair/

# Check hook implementations
cat tools/cli/bpsai_pair/core/hooks.py
```

### Likely Locations

- `tools/cli/bpsai_pair/core/hooks.py`
- `tools/cli/bpsai_pair/security/sandbox.py`
- Any subprocess calls

### Fix Pattern

```python
# Before (bash-specific)
subprocess.run("some_command || true", shell=True)

# After (cross-platform)
import subprocess
import sys

def run_command_safe(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run command, ignoring errors (cross-platform || true equivalent)."""
    try:
        return subprocess.run(cmd, **kwargs, check=False)
    except Exception as e:
        # Log but don't fail
        logger.debug(f"Command failed (ignored): {e}")
        return subprocess.CompletedProcess(cmd, returncode=1)

# ---

# Or for shell commands:
def run_shell_safe(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    """Run shell command, cross-platform."""
    if sys.platform == "win32":
        # Windows: use cmd /c and handle errors in Python
        try:
            return subprocess.run(cmd, shell=True, **kwargs, check=False)
        except Exception:
            return subprocess.CompletedProcess(cmd, returncode=1)
    else:
        # Unix: can use || true
        return subprocess.run(f"{cmd} || true", shell=True, **kwargs)
```

### Acceptance Criteria

- [ ] All hooks work on Windows
- [ ] All hooks work on Mac/Linux
- [ ] No `|| true` in subprocess calls (or properly wrapped)
- [ ] Hook failures don't crash the main command

### Test Commands

```bash
# On Windows (or via WSL testing Windows behavior)
bpsai-pair task update T1 --status in_progress
bpsai-pair task update T1 --status done

# Run tests
pytest tests/core/test_hooks.py -v

# Check for bash-specific syntax
grep -rn "|| true" tools/cli/
```

---

## T27.7: Remove `/status` Slash Command

**Priority:** P0 | **Effort:** 1h | **Issue:** K5, CC2

### Problem

Our `/status` command conflicts with Claude Code's built-in `/status` command.

### Solution

Simply remove our `/status` command. Users can use:
- Claude Code's built-in `/status` for session status
- `bpsai-pair status` CLI for project status

### Files to Modify

```bash
# Find and remove the status command
ls -la .claude/commands/
rm .claude/commands/status.md  # If it exists

# Also check cookiecutter template
ls -la tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/commands/
```

### Acceptance Criteria

- [ ] No `/status` command in `.claude/commands/`
- [ ] No `/status` command in cookiecutter template
- [ ] Documentation updated if it references `/status`

### Verification

```bash
$ ls .claude/commands/
pc-plan.md
start-task.md
prep-release.md
# No status.md

$ claude
> /status  # Should show Claude Code's built-in status, not ours
```

---

## T27.8-T27.11: Sync Cookiecutter to v2.8

**Priority:** P0 | **Effort:** 6h total | **Issues:** A1-A5

### Problem

The cookiecutter template is out of sync with the main project.

### Task Breakdown

| Task | What to Sync | Effort |
|------|--------------|--------|
| T27.8 | capabilities.yaml, config.yaml | 2h |
| T27.9 | All skills (`.claude/skills/`) | 2h |
| T27.10 | All commands (`.claude/commands/`) | 1h |
| T27.11 | All agents (`.claude/agents/`) | 1h |

### Investigation

```bash
# Compare main project vs cookiecutter template
MAIN=".paircoder"
TEMPLATE="tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder"

diff $MAIN/capabilities.yaml $TEMPLATE/capabilities.yaml
diff $MAIN/config.yaml $TEMPLATE/config.yaml

# Compare skills
diff -r .claude/skills/ tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/skills/

# Compare agents
diff -r .claude/agents/ tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/agents/
```

### Process

1. **T27.8: Config files**
   ```bash
   # Copy and templatize config
   cp .paircoder/capabilities.yaml $TEMPLATE/capabilities.yaml
   # Edit to replace project-specific values with {{ cookiecutter.xxx }}
   
   cp .paircoder/config.yaml $TEMPLATE/config.yaml
   # Edit to templatize
   ```

2. **T27.9: Skills**
   ```bash
   # Copy all skills
   cp -r .claude/skills/* $TEMPLATE/../.claude/skills/
   # Review for any project-specific content that needs templatizing
   ```

3. **T27.10: Commands**
   ```bash
   cp -r .claude/commands/* $TEMPLATE/../.claude/commands/
   # Remove /status if present
   ```

4. **T27.11: Agents**
   ```bash
   cp -r .claude/agents/* $TEMPLATE/../.claude/agents/
   ```

### What Needs Templatizing

Some files need `{{ cookiecutter.xxx }}` replacements:

```yaml
# config.yaml - needs templatizing
project:
  name: {{ cookiecutter.project_name }}
  description: {{ cookiecutter.project_description }}

trello:
  board_id: ""  # User fills in
  defaults:
    project: {{ cookiecutter.project_name }}
```

```yaml
# capabilities.yaml - mostly static, but check version
version: "2.8"  # Update to match current
```

### Acceptance Criteria

- [ ] `capabilities.yaml` in template matches v2.8 features
- [ ] `config.yaml` in template has all v2.8 options
- [ ] All 5 skills present in template
- [ ] All 4 agents present in template
- [ ] All commands present (except `/status`)
- [ ] Templatized values use cookiecutter syntax
- [ ] `bpsai-pair init` creates project with all files

### Test Commands

```bash
# Test cookiecutter template
cd /tmp
cookiecutter tools/cli/bpsai_pair/data/cookiecutter-paircoder/
# Answer prompts...

cd my-new-project
ls -la .paircoder/
ls -la .claude/skills/
ls -la .claude/agents/
ls -la .claude/commands/

# Verify CLI works with new project
bpsai-pair status
bpsai-pair validate
```

---

## Sprint 27 Completion Checklist

After all tasks complete:

```bash
# 1. Run full test suite
pytest tests/ -v

# 2. Run smoke tests
pytest tests/smoke/ -v

# 3. Verify key commands work
bpsai-pair --version
bpsai-pair status
bpsai-pair template check
bpsai-pair validate

# 4. Test upgrade flow
cd /tmp && mkdir upgrade-test && cd upgrade-test
bpsai-pair init --preset minimal
bpsai-pair upgrade

# 5. Test Trello with Unicode (if credentials available)
bpsai-pair ttask list

# 6. Update version
# Edit tools/cli/bpsai_pair/__init__.py
__version__ = "2.8.4"

# Edit tools/cli/pyproject.toml
version = "2.8.4"

# 7. Commit and PR
git add -A
git commit -m "Sprint 27: Stabilization fixes for v2.8.4

- T27.1: Fix template check crash
- T27.2: Fix smoke test failure  
- T27.3: Fix Unicode errors in Trello
- T27.4-5: Fix upgrade command
- T27.6: Fix Windows hook compatibility
- T27.7: Remove /status command conflict
- T27.8-11: Sync cookiecutter template to v2.8"

git push origin sprint-27/stabilization
# Create PR
```

---

## Notes for Claude Code

**If handing these tasks to CC:**

1. Start with T27.1-T27.3 (isolated, low risk)
2. Review the PR carefully before merging
3. Then proceed to T27.4-T27.7
4. Save T27.8-T27.11 for last (template sync requires care)

**Watch for CC trying to:**
- "Improve" unrelated code
- Skip tests
- Add features not in the spec
- Change coding style

**If CC goes off-script:** Stop, revert, retry with more specific instructions.

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-12-30 | Claude (claude.ai) | Initial task specs created |
