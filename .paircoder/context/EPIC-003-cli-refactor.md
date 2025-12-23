# EPIC-003: CLI Architecture Refactor

> **Target Version:** v3.0.0
> **Effort:** XL (~80-100 hours across 4-5 sprints)
> **Type:** refactor
> **Priority:** P1 (Tech Debt)

---

## Executive Summary

PairCoder's CLI has grown organically to **33,878 lines across 97 files**. Two files account for 16% of all code:
- `cli.py` (2,892 lines) - God object with command implementations
- `planning/cli_commands.py` (2,602 lines) - Misplaced commands

This refactor separates concerns, establishes clear module boundaries, and reduces file sizes to maintainable levels (<500 lines per file).

---

## Current State Analysis

### Line Count Distribution

```
Top 10 Files by Size:
  2,892  cli.py                        ← GOD OBJECT
  2,602  planning/cli_commands.py      ← MISPLACED COMMANDS
  1,104  trello/sync.py
    963  trello/client.py
    904  orchestration/handoff.py
    870  trello/commands.py
    756  metrics/estimation.py
    753  orchestration/security.py
    701  orchestration/orchestrator.py
    642  orchestration/reviewer.py
```

### Problems Identified

| Issue | Location | Impact |
|-------|----------|--------|
| God object | `cli.py` | 2,892 lines, 15+ command groups inline |
| Misplaced commands | `planning/cli_commands.py` | template, release, sprint commands |
| Duplicate parsers | `flows/parser.py` + `parser_v2.py` | Which is canonical? |
| Orphaned utilities | `utils.py`, `pyutils.py`, `jsonio.py` | 3 files, 41 lines total |
| Root-level sprawl | 12 `.py` files at package root | Should be in modules |
| Missing modules | No `release/`, `sprint/`, `template/` | Logic scattered |

### Module Responsibilities (Current vs. Proposed)

| Module | Current Responsibility | Lines | Proposed |
|--------|----------------------|-------|----------|
| `cli.py` | Everything | 2,892 | Registration only (~200) |
| `planning/cli_commands.py` | plan, task, intent, standup, sprint, release, template | 2,602 | plan + task only (~800) |
| `trello/` | Board + task commands | 4,506 | Keep, minor consolidation |
| `orchestration/` | Multi-agent | 5,410 | Keep, possible split |
| `metrics/` | Token tracking | 2,207 | Keep as-is |
| `security/` | Scanning | 2,948 | Keep as-is |

---

## Target Architecture

### Directory Structure

```
tools/cli/bpsai_pair/
├── __init__.py                 # Package exports only
├── __main__.py                 # Entry point (4 lines)
├── cli.py                      # App registration only (~150 lines)
│
├── commands/                   # NEW: All CLI command implementations
│   ├── __init__.py
│   ├── core.py                 # init, status, validate, feature, pack, ci (~400)
│   ├── flow.py                 # flow list/show/run/validate (~150)
│   ├── preset.py               # preset list/show/preview (~150)
│   ├── config.py               # config validate/update/show (~200)
│   ├── metrics.py              # All metrics commands (~350)
│   ├── timer.py                # timer commands (~150)
│   ├── benchmark.py            # benchmark commands (~200)
│   ├── cache.py                # cache commands (~100)
│   ├── mcp.py                  # mcp commands (~150)
│   ├── orchestrate.py          # orchestrate commands (~300)
│   └── security.py             # security commands (~250)
│
├── core/                       # NEW: Shared infrastructure
│   ├── __init__.py
│   ├── config.py               # Config loading (from root)
│   ├── constants.py            # Constants (from root)
│   ├── hooks.py                # Hook system (from root)
│   ├── ops.py                  # Git/file operations (from root)
│   ├── presets.py              # Preset system (from root)
│   └── utils.py                # Merged utils + pyutils + jsonio
│
├── planning/                   # Focused: Plans & Tasks
│   ├── __init__.py
│   ├── commands.py             # plan + task commands only (~600)
│   ├── models.py               # Plan/Task models
│   ├── parser.py               # Single parser
│   ├── state.py                # State management
│   ├── auto_assign.py
│   ├── intent_detection.py
│   └── standup.py
│
├── sprint/                     # NEW: Sprint lifecycle
│   ├── __init__.py
│   ├── commands.py             # sprint list/complete (~200)
│   └── checklist.py            # Completion checklist
│
├── release/                    # NEW: Release engineering
│   ├── __init__.py
│   ├── commands.py             # release plan/checklist/prep (~300)
│   └── template.py             # template check/list/fix (~200)
│
├── flows/                      # Consolidated
│   ├── __init__.py
│   ├── models.py
│   └── parser.py               # Single parser (merge v1 + v2)
│
├── trello/                     # Keep structure, minor cleanup
├── github/                     # Keep as-is
├── metrics/                    # Keep as-is
├── orchestration/              # Keep as-is
├── security/                   # Keep as-is
├── mcp/                        # Keep as-is
├── integrations/               # Keep as-is
├── context/                    # Keep as-is
├── benchmarks/                 # Keep as-is
├── tasks/                      # Keep as-is
└── data/                       # Keep as-is
```

### New `cli.py` (~150 lines)

```python
"""PairCoder CLI - Entry point and sub-app registration only."""

import typer
from rich.console import Console

from . import __version__

# Import command modules (each defines its own app)
from .commands import core, flow, preset, config, metrics, timer
from .commands import benchmark, cache, mcp, orchestrate, security
from .planning.commands import plan_app, task_app
from .sprint.commands import sprint_app
from .release.commands import release_app, template_app
from .trello.commands import trello_app
from .trello.task_commands import ttask_app
from .github.commands import github_app

console = Console()

app = typer.Typer(
    add_completion=False,
    help="bpsai-pair: AI pair-coding workflow CLI",
)

# Register sub-apps
app.add_typer(plan_app, name="plan")
app.add_typer(task_app, name="task")
app.add_typer(sprint_app, name="sprint")
app.add_typer(release_app, name="release")
app.add_typer(template_app, name="template")
app.add_typer(flow.app, name="flow")
app.add_typer(preset.app, name="preset")
app.add_typer(config.app, name="config")
app.add_typer(metrics.app, name="metrics")
app.add_typer(timer.app, name="timer")
app.add_typer(benchmark.app, name="benchmark")
app.add_typer(cache.app, name="cache")
app.add_typer(mcp.app, name="mcp")
app.add_typer(orchestrate.app, name="orchestrate")
app.add_typer(security.app, name="security")
app.add_typer(trello_app, name="trello")
app.add_typer(ttask_app, name="ttask")
app.add_typer(github_app, name="github")

# Register core commands directly on app
app.command()(core.init)
app.command()(core.feature)
app.command()(core.pack)
app.command()(core.status)
app.command()(core.validate)
app.command()(core.ci)
app.command("context-sync")(core.context_sync)

# Shortcuts
app.command("scan-secrets")(security.scan_secrets)
app.command("scan-deps")(security.scan_deps)


@app.callback()
def main(version: bool = typer.Option(False, "--version", "-v")):
    if version:
        console.print(f"bpsai-pair version {__version__}")
        raise typer.Exit()


def run():
    app()
```

---

## Migration Strategy

### Phase 1: Extract Commands from `cli.py` (Sprint 22)

**Goal:** Reduce `cli.py` from 2,892 → ~200 lines

| Task | From | To | Lines |
|------|------|-----|-------|
| T22.1 | `cli.py` preset commands | `commands/preset.py` | ~150 |
| T22.2 | `cli.py` config commands | `commands/config.py` | ~200 |
| T22.3 | `cli.py` orchestrate commands | `commands/orchestrate.py` | ~300 |
| T22.4 | `cli.py` metrics commands | `commands/metrics.py` | ~400 |
| T22.5 | `cli.py` timer commands | `commands/timer.py` | ~150 |
| T22.6 | `cli.py` benchmark commands | `commands/benchmark.py` | ~200 |
| T22.7 | `cli.py` cache commands | `commands/cache.py` | ~80 |
| T22.8 | `cli.py` mcp commands | `commands/mcp.py` | ~150 |
| T22.9 | `cli.py` flow commands | `commands/flow.py` | ~200 |
| T22.10 | `cli.py` security commands | `commands/security.py` | ~250 |
| T22.11 | `cli.py` core commands | `commands/core.py` | ~400 |
| T22.12 | Refactor `cli.py` to registration only | `cli.py` | ~150 |

**Acceptance Criteria:**
- [ ] All commands work identically (no behavior change)
- [ ] All tests pass
- [ ] `cli.py` < 200 lines
- [ ] Each command module < 500 lines

---

### Phase 2: Extract Commands from `planning/cli_commands.py` (Sprint 23)

**Goal:** Reduce `planning/cli_commands.py` from 2,602 → ~600 lines

| Task | From | To | Lines |
|------|------|-----|-------|
| T23.1 | Create `sprint/` module | New | - |
| T23.2 | Move sprint commands | `planning/cli_commands.py` | `sprint/commands.py` | ~200 |
| T23.3 | Create `release/` module | New | - |
| T23.4 | Move release commands | `planning/cli_commands.py` | `release/commands.py` | ~400 |
| T23.5 | Move template commands | `planning/cli_commands.py` | `release/template.py` | ~200 |
| T23.6 | Move standup to separate file | Already done | Verify |
| T23.7 | Move intent to separate file | Already done | Verify |
| T23.8 | Rename `cli_commands.py` → `commands.py` | Rename | - |
| T23.9 | Update imports everywhere | Global | - |

**Acceptance Criteria:**
- [ ] `planning/commands.py` contains only plan + task commands
- [ ] `sprint/commands.py` has sprint list/complete
- [ ] `release/commands.py` has release plan/checklist/prep
- [ ] `release/template.py` has template check/list/fix
- [ ] All tests pass

---

### Phase 3: Consolidate Root Files (Sprint 24)

**Goal:** Move orphaned root files into `core/` module

| Task | From | To |
|------|------|-----|
| T24.1 | Create `core/` module | New |
| T24.2 | Move `config.py` | Root → `core/config.py` |
| T24.3 | Move `constants.py` | Root → `core/constants.py` |
| T24.4 | Move `hooks.py` | Root → `core/hooks.py` |
| T24.5 | Move `ops.py` | Root → `core/ops.py` |
| T24.6 | Move `presets.py` | Root → `core/presets.py` |
| T24.7 | Merge `utils.py` + `pyutils.py` + `jsonio.py` | Root → `core/utils.py` |
| T24.8 | Delete empty `adapters.py` | Root | Delete |
| T24.9 | Update all imports | Global | - |
| T24.10 | Update `__init__.py` exports | Package | - |

**Acceptance Criteria:**
- [ ] Root level has only: `__init__.py`, `__main__.py`, `cli.py`
- [ ] All functionality moved to appropriate modules
- [ ] All tests pass
- [ ] No circular imports

---

### Phase 4: Consolidate Parsers (Sprint 24)

**Goal:** Single canonical parser per domain

| Task | Action |
|------|--------|
| T24.11 | Merge `flows/parser.py` + `flows/parser_v2.py` → `flows/parser.py` |
| T24.12 | Deprecate v1 flow format (keep reader for migration) |
| T24.13 | Update all flow references to use unified parser |

---

### Phase 5: Documentation & Cleanup (Sprint 25)

| Task | Action |
|------|--------|
| T25.1 | Update FEATURE_MATRIX.md with new structure |
| T25.2 | Update developer documentation |
| T25.3 | Add architecture diagram |
| T25.4 | Remove deprecated code paths |
| T25.5 | Final review and cleanup |

---

## File Size Targets

After refactor, maximum file sizes:

| Category | Max Lines | Examples |
|----------|-----------|----------|
| Command modules | 400 | `commands/core.py`, `commands/metrics.py` |
| Business logic | 600 | `trello/sync.py`, `orchestration/orchestrator.py` |
| Models | 400 | `planning/models.py` |
| Parsers | 300 | `flows/parser.py` |
| CLI entry | 200 | `cli.py` |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking imports | High | Medium | Comprehensive import grep before each move |
| Test failures | Medium | Low | Run full test suite after each task |
| Circular imports | Medium | High | Design import graph before starting |
| Missing functionality | Low | High | Diff before/after for each command |

---

## Import Graph (Post-Refactor)

```
cli.py
  └── commands/*        # All command modules
  └── planning/         # plan, task commands
  └── sprint/           # sprint commands
  └── release/          # release, template commands
  └── trello/           # trello, ttask commands
  └── github/           # github commands

commands/*
  └── core/             # Shared infrastructure
  └── domain modules    # planning, trello, etc.

domain modules (planning, trello, etc.)
  └── core/             # Shared infrastructure
  └── models            # Own models only

core/
  └── (no internal dependencies)
```

---

## Sprint Allocation

| Sprint | Focus | Tasks | Hours |
|--------|-------|-------|-------|
| Sprint 22 | Extract from `cli.py` | 12 tasks | 16-20 |
| Sprint 23 | Extract from `planning/` | 9 tasks | 12-16 |
| Sprint 24 | Consolidate root + parsers | 13 tasks | 16-20 |
| Sprint 25 | Documentation + cleanup | 5 tasks | 8-10 |
| **Total** | | **39 tasks** | **52-66 hrs** |

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| `cli.py` lines | 2,892 | ~150 | < 200 |
| `planning/cli_commands.py` lines | 2,602 | ~600 | < 800 |
| Largest file | 2,892 | ~600 | < 700 |
| Files at root | 12 | 3 | ≤ 5 |
| Test coverage | Current | Maintained | ≥ Current |

---

## Definition of Done

- [ ] All tests pass
- [ ] No file exceeds 700 lines
- [ ] `cli.py` is registration only (< 200 lines)
- [ ] Root level has only `__init__.py`, `__main__.py`, `cli.py`
- [ ] All commands function identically to pre-refactor
- [ ] Documentation updated
- [ ] No circular imports
- [ ] Import paths updated in all external references (skills, docs)

---

## Appendix: Command Inventory

### Commands Currently in `cli.py` (to be extracted)

| Group | Commands | Target Module |
|-------|----------|---------------|
| (core) | init, feature, pack, context-sync, status, validate, ci | `commands/core.py` |
| preset | list, show, preview | `commands/preset.py` |
| config | validate, update, show | `commands/config.py` |
| orchestrate | task, analyze, select-agent, handoff, auto-run, auto-session, workflow-status | `commands/orchestrate.py` |
| metrics | summary, task, breakdown, budget, export, velocity, burndown, accuracy, tokens | `commands/metrics.py` |
| timer | start, stop, status, show, summary | `commands/timer.py` |
| benchmark | run, results, compare, list | `commands/benchmark.py` |
| cache | stats, clear, invalidate | `commands/cache.py` |
| mcp | serve, tools, test | `commands/mcp.py` |
| flow | list, show, run, validate | `commands/flow.py` |
| security | scan-secrets, pre-commit, install-hook, scan-deps | `commands/security.py` |

### Commands Currently in `planning/cli_commands.py` (to be reorganized)

| Group | Commands | Target Module |
|-------|----------|---------------|
| plan | new, list, show, tasks, status, sync-trello, add-task | `planning/commands.py` |
| task | list, show, update, next, auto-next, archive, restore, list-archived, cleanup, changelog-preview | `planning/commands.py` |
| intent | detect, should-plan, suggest-flow | `planning/commands.py` |
| standup | generate, post | `planning/standup.py` (already separate) |
| sprint | complete, list | `sprint/commands.py` (NEW) |
| release | plan, checklist, prep | `release/commands.py` (NEW) |
| template | check, list | `release/template.py` (NEW) |

---

## Notes

- This refactor is **behavior-preserving** - no new features, no removed features
- Each phase can be done independently and released
- Test coverage must be maintained throughout
- Consider feature flags if incremental rollout needed
