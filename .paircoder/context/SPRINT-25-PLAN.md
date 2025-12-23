# Sprint 25: Complete EPIC-003 + Token Budget

> **Version:** v2.8.0
> **Duration:** 3-5 days
> **Theme:** "Finish the refactor, add proactive token management"

---

## Sprint Goal

1. Complete EPIC-003 (Phase 4: Parser Consolidation + Phase 5: Documentation)
2. Fix project root detection bug
3. Implement token budget system to prevent context compaction

---

## Status Check

**EPIC-003 Progress:**
| Phase | Sprint | Tasks | Status |
|-------|--------|-------|--------|
| Phase 1: Extract from cli.py | Sprint 22 | T22.1-T22.12 | ✅ Complete |
| Phase 2: Extract from planning/ | Sprint 23 | T23.1-T23.9 | ✅ Complete |
| Phase 3: Consolidate Root Files | Sprint 24 | T24.1-T24.10 | ✅ Complete |
| Phase 4: Consolidate Parsers | Sprint 24* | T24.11-T24.13 | ⏳ Pending |
| Phase 5: Documentation & Cleanup | Sprint 25 | T25.1-T25.5 | ⏳ Pending |

*Phase 4 was planned for Sprint 24 but not completed.

---

## Task List

### Part A: EPIC-003 Phase 4 - Parser Consolidation (3 tasks)

*Original EPIC-003 task IDs preserved for traceability*

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T24.11 | Merge flows/parser.py + flows/parser_v2.py | refactor | M | 35 |
| T24.12 | Deprecate v1 flow format (keep reader for migration) | refactor | S | 15 |
| T24.13 | Update all flow references to unified parser | refactor | S | 20 |

**T24.11 Details:**
- Analyze both `flows/parser.py` and `flows/parser_v2.py`
- Identify differences and which version is canonical
- Create unified `flows/parser.py` combining best of both
- Delete `parser_v2.py` after merge
- Ensure backward compatibility with existing .flow.md files

**T24.12 Details:**
- Add deprecation warnings for v1 flow format if different from v2
- Keep v1 reader code for migration purposes
- Document v1 → v2 migration path if needed

**T24.13 Details:**
- Find all code importing from flow parsers
- Update to use unified parser API
- Run all flow-related tests

**Acceptance Criteria:**
- [ ] Single `flows/parser.py` file (no parser_v2.py)
- [ ] All existing flow files still parse correctly
- [ ] Deprecation path documented if formats differ
- [ ] All tests pass

---

### Part B: EPIC-003 Phase 5 - Documentation & Cleanup (5 tasks)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T25.1 | Update FEATURE_MATRIX.md with new structure | docs | S | 15 |
| T25.2 | Update developer documentation | docs | M | 25 |
| T25.3 | Add architecture diagram | docs | S | 15 |
| T25.4 | Remove deprecated code paths | refactor | S | 20 |
| T25.5 | Final review and cleanup | chore | M | 25 |

**T25.1 Details:**
- Update module/file structure in FEATURE_MATRIX.md
- Reflect new `core/`, `commands/`, `sprint/`, `release/` structure
- Update line counts if changed significantly

**T25.2 Details:**
- Update CONTRIBUTING.md with new module structure
- Update any docs referencing old import paths
- Ensure code examples use correct imports

**T25.3 Details:**
Create ASCII or Mermaid diagram showing:
```
cli.py (registration only)
  ├── commands/     → Core CLI commands
  ├── planning/     → plan, task commands
  ├── sprint/       → sprint commands
  ├── release/      → release, template commands
  ├── trello/       → Trello integration
  └── core/         → Shared infrastructure (config, hooks, ops, utils)
```

**T25.4 Details:**
- Remove any backward-compat shims from refactor
- Clean up TODO/FIXME comments added during refactor
- Remove dead code paths

**T25.5 Details:**
- Run final verification of all refactor changes
- Ensure no circular imports
- Check file sizes meet targets (< 500 lines for commands)
- Mark EPIC-003 as COMPLETE

**Acceptance Criteria:**
- [ ] FEATURE_MATRIX.md reflects current architecture
- [ ] Developer docs updated with correct import paths
- [ ] Architecture diagram exists
- [ ] No deprecated imports or dead code remaining
- [ ] EPIC-003 marked complete

---

### Part C: Bug Fix - Project Root Detection (1 task)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T25.6 | Fix project root detection in all commands | bugfix | S | 20 |

**Problem:**
Commands use `Path.cwd()` instead of finding actual project root. This causes `.paircoder/` directories to be created in wrong locations when running from subdirectories.

**Evidence:** Stray `.paircoder/` found at `tools/cli/.paircoder/`

**Solution:**
Add helper to `core/ops.py`:
```python
def find_project_root(start_path: Path = None) -> Path:
    """Find project root by walking up to find .paircoder/ or .git/"""
    cwd = start_path or Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".paircoder").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return cwd
```

**Files to update:**
- `commands/upgrade.py` (line ~318)
- `trello/commands.py` (trello connect)
- Any other command using `Path.cwd()` for project paths

**Immediate cleanup:**
```bash
rm -rf tools/cli/.paircoder
```

**Acceptance Criteria:**
- [ ] `find_project_root()` exists in core/ops.py
- [ ] `upgrade` command uses `find_project_root()`
- [ ] `trello connect` uses `find_project_root()`
- [ ] Test: running command from subdirectory finds correct root
- [ ] No stray `.paircoder/` directories

---

### Part D: Token Budget System (5 tasks)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T25.7 | Add tiktoken dependency | chore | XS | 5 |
| T25.8 | Create tokens.py estimation module | feature | L | 50 |
| T25.9 | Add budget CLI commands | feature | M | 35 |
| T25.10 | Integrate budget into session status | feature | S | 20 |
| T25.11 | Add pre-task budget hook | feature | S | 20 |

**T25.7 Details:**
```toml
# pyproject.toml
tiktoken = "^0.5.0"
```

**T25.8 Details:**
Create `tools/cli/bpsai_pair/tokens.py`:

```python
"""Token counting and budget estimation."""
import tiktoken

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    
def count_file_tokens(path: Path) -> int:
    """Count tokens in a file."""
    
def estimate_task_tokens(task_id: str, files: list[Path], complexity: int) -> dict:
    """Estimate total tokens for a task.
    
    Returns:
        {
            "base_context": 15000,
            "task_file": 500,
            "source_files": 8000,
            "estimated_output": 3000,
            "total": 26500,
            "budget_percent": 26.5
        }
    """

def get_budget_status(estimated: int, model: str = "claude-sonnet-4-5") -> dict:
    """Get budget status with thresholds.
    
    Returns:
        {
            "used": 26500,
            "limit": 100000,
            "remaining": 73500,
            "percent": 26.5,
            "status": "ok",  # ok | warning | critical
            "message": "Budget healthy"
        }
    """

MODEL_LIMITS = {
    "claude-sonnet-4-5": 100000,
    "claude-opus-4-5": 100000,
    "claude-haiku-4-5": 100000,
}

THRESHOLDS = {
    "info": 50,      # 50% - informational
    "warning": 75,   # 75% - consider breaking up
    "critical": 90,  # 90% - compaction likely
}
```

**T25.9 Details:**
Create `tools/cli/bpsai_pair/commands/budget.py`:

```bash
# Estimate tokens for a task
bpsai-pair budget estimate T25.8
# Output:
#   Task: T25.8 - Create tokens.py estimation module
#   Files: 3 (tokens.py, test_tokens.py, commands/budget.py)
#   
#   Token Breakdown:
#     Base context:    15,000
#     Task file:          450
#     Source files:     3,200
#     Est. output:      5,000
#     ─────────────────────────
#     Total:           23,650 (24% of budget)
#   
#   Status: ✅ OK

# Estimate for specific files
bpsai-pair budget estimate -f src/main.py -f src/utils.py

# Show current session budget status
bpsai-pair budget status

# Pre-flight check (exits 1 if over threshold)
bpsai-pair budget check T25.8 --threshold 75
```

**T25.10 Details:**
Update `session status` output:
```
Session: abc123
Active: 25 min since last activity

Token Budget:
  ████████████░░░░░░░░ 45% (45,000 / 100,000)
  Status: OK
```

**T25.11 Details:**
Add to `on_task_start` hook in config.yaml:
```yaml
hooks:
  on_task_start:
    - check_token_budget    # NEW - warns if task large
    - start_timer
    - sync_trello
    - update_state
```

Warning output:
```
⚠️ TOKEN BUDGET WARNING
Task T25.8 estimated at 75,000 tokens (75% of budget)
Consider breaking into smaller subtasks.
Continue anyway? [y/N]: 
```

**Acceptance Criteria:**
- [ ] tiktoken installed
- [ ] `count_tokens()` works with tiktoken
- [ ] `estimate_task_tokens()` provides breakdown
- [ ] `bpsai-pair budget estimate <task>` works
- [ ] `bpsai-pair budget status` shows session usage
- [ ] `bpsai-pair budget check` exits 1 if over threshold
- [ ] Pre-task hook warns about large tasks
- [ ] Thresholds: 50% info, 75% warn, 90% critical

---

## Sprint Summary

| Part | Description | Tasks | Complexity |
|------|-------------|-------|------------|
| A | EPIC-003 Phase 4: Parsers | 3 | 70 |
| B | EPIC-003 Phase 5: Docs | 5 | 100 |
| C | Bug Fix: Project Root | 1 | 20 |
| D | Token Budget System | 5 | 130 |
| **Total** | | **14** | **320** |

---

## Task Dependencies

```
Part A (Parsers):
T24.11 → T24.12 → T24.13

Part B (Docs) - after Part A:
T25.1 → T25.2 → T25.3 → T25.4 → T25.5

Part C (Bug Fix) - independent:
T25.6

Part D (Token Budget) - independent:
T25.7 → T25.8 → T25.9 → T25.10 → T25.11
```

**Suggested order:**
1. T25.6 (bug fix - quick win, prevents future issues)
2. T24.11-T24.13 (parsers - complete Phase 4)
3. T25.7-T25.11 (token budget - can parallel with docs)
4. T25.1-T25.5 (docs - finalize after code stable)

---

## Definition of Done

- [ ] EPIC-003 fully complete (all 5 phases)
- [ ] Single unified flow parser
- [ ] Architecture diagram exists
- [ ] Documentation reflects current structure
- [ ] Project root detection fixed
- [ ] Token budget system working
- [ ] Pre-task warnings for large tasks
- [ ] All tests pass
- [ ] Version bumped to v2.8.0
- [ ] CHANGELOG.md updated

---

## Files Changed

**New Files:**
- `bpsai_pair/tokens.py`
- `bpsai_pair/commands/budget.py`
- `docs/architecture.md` (or diagram in existing doc)

**Modified Files:**
- `flows/parser.py` (merged)
- `core/ops.py` (add find_project_root)
- `commands/upgrade.py` (use find_project_root)
- `trello/commands.py` (use find_project_root)
- `commands/session.py` (add budget to status)
- `core/hooks.py` (add check_token_budget)
- `FEATURE_MATRIX.md`
- `CONTRIBUTING.md`
- `pyproject.toml` (tiktoken dep)
- `.paircoder/config.yaml` (add hook)

**Deleted Files:**
- `flows/parser_v2.py`
- `tools/cli/.paircoder/` (stray directory)
