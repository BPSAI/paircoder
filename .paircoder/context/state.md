# Current State

> Last updated: 2025-12-16

## Active Plan

**Plan:** `plan-2025-12-sprint-13-autonomy`
**Status:** in_progress
**Current Sprint:** sprint-13 (Full Autonomy)

## Current Focus

Trello reliability improvements complete:
- BPS preset with 7-list structure created
- Task update command now ALWAYS fires hooks
- Trello card movement verified working

## Task Status

### Sprint 1-12: All Complete ✅

Sprints 1-12 fully completed (62 tasks). See archive for details.

### Sprint 13: Full Autonomy (Current)

**P0 Tasks - All Complete ✅**

| Task | Title | Status | Complexity |
|------|-------|--------|------------|
| TASK-066 | Webhook listener for Trello card moves | ✅ done | 40 |
| TASK-067 | Agent assignment on Ready column | ✅ done | 35 |
| TASK-070 | GitHub PR integration | ✅ done | 50 |
| TASK-072 | Automatic next task assignment | ✅ done | 40 |
| TASK-077 | Add preset system for config initialization | ✅ done | 45 |
| TASK-078 | Create BPS preset with full Trello guidelines | ✅ done | 35 |
| TASK-079 | Auto-enter planning mode on new feature detection | ✅ done | 55 |
| TASK-080 | Orchestrator sequencing for full autonomy | ✅ done | 65 |

**P1 Tasks - Remaining**

| Task | Title | Status | Depends On |
|------|-------|--------|------------|
| TASK-063 | VS Code extension wrapper for MCP | 📋 planned | - |
| TASK-064 | Current task status bar widget | 📋 planned | TASK-063 |
| TASK-065 | Auto-update context on file save | 📋 planned | TASK-063 |
| TASK-068 | Progress comments from agents | ⏳ pending | TASK-067 |
| TASK-069 | Auto-PR link when branch pushed | ⏳ pending | - |
| TASK-071 | PR merge triggers task archive | ⏳ pending | - |

**P2/P3 Tasks - Backlog**

| Task | Title | Status | Complexity |
|------|-------|--------|------------|
| TASK-073 | Daily standup summary generation | ⏳ pending | 35 |
| TASK-074 | Dashboard web UI | ⏳ pending (deprioritized) | 60 |
| TASK-075 | Slack notifications integration | ⏳ pending | 40 |
| TASK-076 | Multi-project support | ⏳ pending | 50 |

## What Was Just Done

### Session: 2025-12-16 - Trello Reliability Improvements

#### 1. Bug Fix: TaskParser Method Name
Fixed `task_parser.get()` → `task_parser.get_task_by_id()` in 10 locations across 4 files:
- `orchestration/autonomous.py` (4 occurrences)
- `planning/auto_assign.py` (2 occurrences)
- `github/pr.py` (2 occurrences)
- `trello/webhook.py` (2 occurrences)

#### 2. TASK-078: BPS Preset Created ✅
Added `bps` preset to `presets.py` with full BPS Trello guidelines:

**7-List Structure:**
- Intake / Backlog
- Planned / Ready
- In Progress
- Review / Testing
- Deployed / Done
- Issues / Tech Debt
- Notes / Ops Log

**8 Label Colors:**
- Frontend (green), Backend (blue), Worker (purple), Deployment (red)
- Bug (orange), Security (yellow), Docs (sky), AI (black)

**Automation Mappings:**
- `on_task_start` → moves to "In Progress"
- `on_task_complete` → moves to "Deployed / Done"
- `on_task_block` → moves to "Issues / Tech Debt"
- `on_task_review` → moves to "Review / Testing"

**Hooks Enabled by Default:**
- `on_task_start`: start_timer, sync_trello, update_state
- `on_task_complete`: stop_timer, record_metrics, sync_trello, check_unblocked
- `on_task_block`: sync_trello

#### 3. Hook Reliability Fix
Updated `planning/cli_commands.py` - `task_update` command:
- Now **always fires hooks** when status changes
- Added `_run_status_hooks()` helper function
- Maps status to event: in_progress→on_task_start, done→on_task_complete, blocked→on_task_block
- Added `--no-hooks` flag to skip hooks if needed
- Shows feedback: "→ Trello: moved to 'In Progress'"

#### 4. Config Path Compatibility
Updated `hooks.py` to check both locations:
- `trello.automation` (new/preferred)
- `trello.card_format.automation` (backwards compatibility)

#### 5. Test Fixes
Updated tests using old `parser.get()` method:
- `tests/test_autonomous_workflow.py`
- `tests/test_webhook.py`

### Verified Working
```bash
$ bpsai-pair task update TASK-078 --status in_progress
🔄 Updated TASK-078 -> in_progress
  → Trello: moved to 'In Progress'

$ bpsai-pair task update TASK-078 --status done
✅ Updated TASK-078 -> done
  → Trello: moved to 'Deployed / Done'
```

### Test Coverage
- **Total tests**: 389 passing
- All tests pass after fixes

## What's Next

### Immediate Priority

1. **PR Automation** (TASK-069, 071)
   - Auto-link PRs when branches are pushed
   - Archive tasks when PRs are merged

2. **Agent Progress Tracking** (TASK-068)
   - Automatic progress comments on Trello cards

### Backlog

- VS Code Extension (TASK-063, 064, 065) - future
- Daily standup summary generation
- Slack notifications

## Blockers

None.

## Files Modified This Session

```
tools/cli/bpsai_pair/
├── presets.py                    # Added BPS preset
├── hooks.py                      # Config path compatibility fix
├── planning/
│   ├── cli_commands.py           # Hook triggering on task update
│   └── auto_assign.py            # Method name fix
├── orchestration/
│   └── autonomous.py             # Method name fix
├── github/
│   └── pr.py                     # Method name fix
└── trello/
    └── webhook.py                # Method name fix

tests/
├── test_autonomous_workflow.py   # Method name fix
└── test_webhook.py               # Method name fix
```

## Workflow Stages (Codified)

| Stage | Trello List | Trigger |
|-------|-------------|---------|
| Intake | Intake / Backlog | New unplanned task |
| Planned | Planned / Ready | `on_task_ready` hook |
| In Progress | In Progress | `on_task_start` hook |
| Review | Review / Testing | `on_task_review` hook |
| Done | Deployed / Done | `on_task_complete` hook |
| Blocked | Issues / Tech Debt | `on_task_block` hook |

## Available Presets

| Preset | Description |
|--------|-------------|
| python-cli | Python CLI application with Click/Typer |
| python-api | Python REST API with Flask/FastAPI |
| react | React/Next.js frontend application |
| fullstack | Full-stack (Python backend + React frontend) |
| library | Python library/package for distribution |
| minimal | Minimal configuration with essential defaults |
| autonomous | Full autonomy with Trello integration |
| **bps** | **BPS AI Software preset with 7-list Trello workflow** |

## CLI Quick Reference

```bash
# Task management with hooks
bpsai-pair task update <id> --status in_progress  # Fires hooks, moves Trello card
bpsai-pair task update <id> --status done         # Fires hooks, moves card to Done
bpsai-pair task update <id> --status done --no-hooks  # Skip hooks

# Presets
bpsai-pair preset list                    # Show all presets
bpsai-pair preset show bps                # Show BPS preset details
bpsai-pair preset preview bps             # Preview generated config
bpsai-pair init myproject --preset bps    # Initialize with BPS preset

# Trello
bpsai-pair trello status                  # Check connection
bpsai-pair plan sync-trello <plan-id>     # Sync plan to Trello board
```
