# Current State

> Last updated: 2026-01-05

## Active Plan

**Plan:** plan-2026-01-sprint-28-docs
**Sprint:** 28 - Documentation & Release
**Status:** In Progress
**Target Release:** v2.9.0

## Current Sprint (Sprint 28 - v2.9.0 Documentation)

| ID | Title | Priority | Complexity | Status |
|----|-------|----------|------------|--------|
| T28.12 | Update Version Strings Across Docs | P1 | 15 | ✓ done |
| T28.13 | Add CHANGELOG v2.9.0 Entry | P1 | 25 | ✓ done |
| T28.14 | Document Audit and State Commands | P1 | 30 | ✓ done |
| T28.15 | Update CLI Reference with Flag Changes | P1 | 20 | ○ pending |
| T28.16 | Update Config Documentation | P1 | 15 | ○ pending |
| T28.17 | Final Verification and Release Prep | P0 | 20 | ○ pending |

**Total:** 6 tasks, 125 complexity points

## Completed Sprint (Sprint 27 - Stabilization)

| ID | Title | Status |
|----|-------|--------|
| T27.1 | Fix template check crash | ✓ done |
| T27.2 | Fix smoke test failure | ✓ done |
| T27.3 | Fix Unicode errors in Trello | ✓ done |
| T27.4 | Fix upgrade source file resolution | ✓ done |
| T27.5 | Fix upgrade to actually copy files | ✓ done |
| T27.6 | Fix Windows hook compatibility | ✓ done |
| T27.7 | Remove /status slash command conflict | ✓ done |
| T27.8 | Sync cookiecutter: config files | ✓ done |
| T27.9 | Sync cookiecutter: skills | ✓ done |
| T27.10 | Sync cookiecutter: commands | ✓ done |
| T27.11 | Sync cookiecutter: agents | ✓ done |

**Result:** 11/11 tasks (325/325 complexity points) ✓ Sprint Complete!

## Sprint History

Sprints 1-27 archived. See `.paircoder/history/sprint_archive.md`.

| Sprint | Theme | Version | Status |
|--------|-------|---------|--------|
| 1-17.5 | Foundation → Backlog Remediation | v2.0-2.6.0 | Archived |
| 17.6 | Trello Field Validation Hotfix | v2.6.1 | Complete |
| 18 | Release Engineering | v2.6.1 | Complete |
| 19 | Methodology & Session Management | v2.7.0 | Complete |
| 22-24 | CLI Refactor (EPIC-003) | v2.7.0 | Complete |
| 25 | EPIC-003 Complete + Token Budget | v2.8.0 | Complete |
| 25.5 | Cross-Platform Skills | v2.8.1 | Complete |
| 25.6 | Emergent Skill Discovery | v2.8.3 | Complete |
| 27 | Stabilization | v2.8.4 | Complete |
| 26 | UX Overhaul (EPIC-004) | v2.10.0 | Planned |
| 28 | v2.9.0 Documentation & Release | v2.9.0 | In Progress |

## What's Next

Ready to start: T28.15 - Update CLI Reference with Flag Changes


## Backlog (Deprioritized)

See `.paircoder/tasks/backlog/`:
- HF-001: Context sync hotfix
- RFE-001: Remote API Orchestration

## Future: EPIC-005 (Flows Removal)

After Sprint 25.6 deprecation warnings, full removal planned for v2.11.0:
- Flow commands removed entirely
- `flows_dir` config option removed
- `capabilities.yaml` flow_triggers removed
- Migration utility for legacy projects

## Session Log

_Add entries here as work is completed._

### 2026-01-05 - T28.14: Document Audit and State Commands

Documented the new `audit` and `state` command groups:
- Added Audit Commands section to all-cli-commands.md (3 commands: bypasses/summary/clear)
- Added State Commands section to all-cli-commands.md (5 commands: show/list/history/reset/advance)
- Updated README.md command count from 120+ to 127+
- Added Audit and State command tables to README.md
- Updated FEATURE_MATRIX.md CLI Commands Summary table
- Added audit and state features to Sprint 28 section

All examples verified by running actual CLI commands.

### 2026-01-05 - T28.13: Add CHANGELOG v2.9.0 Entry

Added comprehensive changelog entry documenting all Sprint 28 changes:
- **Enforcement System**: Task state machine, bypass audit logging, model routing, preconditions
- **New CLI Commands**: `audit bypasses/summary`, `state show/list/history/reset/advance`
- **Breaking Changes**: `--force` → `--overwrite` flag renames across skill/security commands
- **Enforcement Defaults**: AC verification, budget checks, Trello task restrictions
- **Test Updates**: 76 new tests, 2145+ total (up from 2100+)

All acceptance criteria verified.

### 2026-01-05 - T28.12: Update Version Strings

Updated all version references from 2.8.x to 2.9.0:
- `.paircoder/capabilities.yaml`: 2.8.3 -> 2.9.0
- `README.md`: v2.8.4 -> v2.9.0 (title, install example)
- `.paircoder/docs/USER_GUIDE.md`: v2.8.4 -> v2.9.0 (title, install, footer)
- `.claude/skills/.../all-cli-commands.md`: Version 2.8.4 -> 2.9.0

All acceptance criteria verified.

### 2026-01-05 - Sprint 28 Planning

Created plan `plan-2026-01-sprint-28-docs` with 6 tasks (125 complexity points):
- T28.12: Update Version Strings Across Docs
- T28.13: Add CHANGELOG v2.9.0 Entry
- T28.14: Document Audit and State Commands
- T28.15: Update CLI Reference with Flag Changes
- T28.16: Update Config Documentation
- T28.17: Final Verification and Release Prep

Synced to Trello: 6 cards created in "Planned/Ready" list.

### 2026-01-04 - Hotfix: Enforcement Gates (Sprint 28 Prep)

Completed 4 enforcement gate hotfixes on `hotfix/enforcement-gates` branch:

| Task | Title | Commit |
|------|-------|--------|
| T28.1b | Remove --force from ttask done | `5f3f2d9` |
| T28.3 | Require Trello sync before local task update | `0eaf6fc` |
| T28.4 | Auto-update local task from ttask done | `e527ade` |
| T28.5 | Wire budget can_proceed() before task start | `ae61e74` |

**Changes:**
- `ttask done`: Removed `--force` flag, `--no-strict` now logs bypasses
- `task update`: Added `--local-only` + `--reason` for audited bypass
- `ttask done`: Auto-syncs local task file status
- `ttask start`: Budget check before starting (with `--budget-override`)

**Tests:** 47 new tests added across 4 test files, all passing.

**Status:** Branch ready for merge or additional hotfixes.

### 2025-12-31 - Housekeeping: Archive and Compact

- Archived Sprint 17.6-27 details to `.paircoder/history/sprint_archive.md`
- Compacted state.md for Sprint 28 readiness
- Sprint 27 session logs archived (see sprint_archive.md for key deliverables)
