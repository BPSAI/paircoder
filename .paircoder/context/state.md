# Current State

> Last updated: 2025-12-15

## Active Plan

**Plan:** `plan-2025-01-paircoder-v2-upgrade`
**Status:** in_progress
**Current Sprint:** sprint-4 (Template & Documentation)

## Current Focus

Sprints 1-3 complete! Planning module fully integrated into CLI.
Ready to begin Sprint 4: Template updates and documentation.

## Task Status

### Sprint 1: Foundation & Claude Code Integration ✅

| Task | Title | Status |
|------|-------|--------|
| TASK-001 | Create v2 directory structure | ✅ done |
| TASK-002 | Create LLM capability manifest | ✅ done |
| TASK-003 | Update ADR 0002 | ✅ done |
| TASK-004 | Create project.md | ✅ done |
| TASK-005 | Create workflow.md | ✅ done |
| TASK-006 | Create state.md | ✅ done |

### Sprint 2: Planning System Implementation ✅

| Task | Title | Status | Notes |
|------|-------|--------|-------|
| TASK-007 | Implement plan YAML parser | ✅ done | `planning/parser.py` |
| TASK-008 | Implement task YAML+MD parser | ✅ done | `planning/parser.py` |
| TASK-009 | Add 'bpsai-pair plan' CLI commands | ✅ done | Converted to Typer |
| TASK-010 | Add 'bpsai-pair task' CLI commands | ✅ done | Converted to Typer |
| TASK-015 | Update flow parser for .flow.md | ✅ done | Pulled forward |

### Sprint 3: CLI Extensions & Flows ✅

| Task | Title | Status | Notes |
|------|-------|--------|-------|
| TASK-011 | Create design-plan-implement.flow.md | ✅ done | Created in Sprint 1 |
| TASK-012 | Create tdd-implement.flow.md | ✅ done | Created in Sprint 1 |
| TASK-013 | Create review.flow.md | ✅ done | Created in Sprint 1 |
| TASK-014 | Create finish-branch.flow.md | ✅ done | Created in Sprint 1 |
| — | Integrate planning module into CLI | ✅ done | Claude Code completed |

### Sprint 4: Template & Documentation ⏳

| Task | Title | Status | Priority |
|------|-------|--------|----------|
| TASK-016 | Update cookiecutter template for v2 | ✅ done | P1 |
| TASK-017 | Update USER_GUIDE.md | ⏳ pending | P2 |
| TASK-018 | Update README.md | ⏳ pending | P2 |
| TASK-019 | Bump version and prepare release | ⏳ pending | P2 |

## What Was Just Done

### TASK-016: Cookiecutter Template Update

Updated the cookiecutter template to use v2 `.paircoder/` structure:

1. **Created `.paircoder/config.yaml`** - v2 configuration with models, routing, flows
2. **Created `.paircoder/capabilities.yaml`** - LLM capability manifest
3. **Created `.paircoder/context/`** - project.md, workflow.md, state.md
4. **Created `.paircoder/flows/`** - tdd-implement.flow.md starter flow
5. **Updated AGENTS.md & CLAUDE.md** - Point to new `.paircoder/` structure

### Key Files Added to Template

```
.paircoder/
├── config.yaml
├── capabilities.yaml
├── context/
│   ├── project.md
│   ├── workflow.md
│   └── state.md
├── flows/
│   └── tdd-implement.flow.md
├── plans/.gitkeep
└── tasks/.gitkeep
```

## What's Next

1. **TASK-017**: Update USER_GUIDE.md
   - Document planning system
   - Document new CLI commands
   - Add LLM integration section

2. **TASK-018**: Update README.md
   - Highlight v2 features
   - Update command overview

3. **TASK-019**: Version bump and release
   - Decide on 2.0.0 vs 0.3.0
   - Update CHANGELOG
   - Create release

## Blockers

None — ready to proceed with Sprint 4.

## CLI Commands Now Available

```bash
# Planning
bpsai-pair plan new <slug> --type feature --title "Title"
bpsai-pair plan list
bpsai-pair plan show <plan-id>
bpsai-pair plan tasks <plan-id>
bpsai-pair plan add-task <plan-id> --id TASK-XXX --title "Title"

# Tasks  
bpsai-pair task list
bpsai-pair task show <task-id>
bpsai-pair task update <task-id> --status done
bpsai-pair task next

# Flows (v2)
bpsai-pair flow list        # Shows .flow.md files
bpsai-pair flow show <name>
bpsai-pair flow run <name>
```
