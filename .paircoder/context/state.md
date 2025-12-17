# Current State

> Last updated: 2025-12-17

## Active Plan

**Plan:** `plan-2025-12-sprint-14-trello-deep`
**Status:** in_progress
**Current Sprint:** sprint-14 (Trello Deep Integration)

## Current Focus

Sprint 14: Make Trello cards created by PairCoder look exactly like Mike would create manually.

**Key Objectives:**
- Sync custom fields (Project, Stack, Effort, Status)
- Labels with exact BPS colors
- Card description templates following BPS format
- Two-way sync (Trello changes update local tasks)
- Checklists from acceptance criteria
- Due date sync
- Activity log comments

## Task Status

### Sprint 1-12: Archived

See `.paircoder/history/sprints-1-12-archive.md` for historical details.

### Sprint 13: Full Autonomy - COMPLETE

All tasks completed. See Sprint 13 section in archive.

Key deliverables:
- Preset system (8 presets including BPS)
- Progress comments for Trello cards
- Auto-PR creation from branch names
- PR merge task archival
- Daily standup generation
- Hook reliability (always fires on status change)

### Sprint 14: Trello Deep Integration - IN PROGRESS

| Task | Title | Status | Priority | Complexity |
|------|-------|--------|----------|------------|
| TASK-081 | Sync Trello custom fields | done | P0 | 35 |
| TASK-082 | Sync Trello labels with exact BPS colors | done | P0 | 25 |
| TASK-083 | Card description templates (BPS format) | done | P1 | 25 |
| TASK-084 | Effort → Trello Effort field mapping | done | P1 | 20 |
| TASK-085 | Two-way sync (Trello → local) | done | P0 | 45 |
| TASK-086 | Support checklists in cards | done | P1 | 30 |
| TASK-087 | Due date sync | pending | P2 | 20 |
| TASK-088 | Activity log comments | pending | P2 | 25 |

### Backlog (Deprioritized)

Tasks moved to `.paircoder/tasks/backlog/`:
- TASK-063: VS Code extension
- TASK-064: Status bar widget
- TASK-065: Auto-context on save
- TASK-074: Dashboard UI
- TASK-075: Slack notifications
- TASK-076: Multi-project support

## What Was Just Done

### Session: 2025-12-17 - TASK-086 Complete

**Checklist Support (TASK-086)** - DONE

Implemented full checklist support for Trello cards:

**New checklist API methods in `trello/client.py`:**
- `get_card_checklists()` - Get all checklists on a card
- `get_checklist_by_name()` - Find checklist by name (case-insensitive)
- `create_checklist()` - Create new checklist on card
- `add_checklist_item()` - Add item to checklist with checked state
- `update_checklist_item()` - Update item state (check/uncheck) or name
- `delete_checklist()` - Delete a checklist
- `ensure_checklist()` - Create or update checklist with items

**Updated `trello/sync.py`:**
- `TaskData.checked_criteria` - Track which acceptance criteria are checked
- `TaskData.from_task()` - Parse checked/unchecked items from task body
- `TrelloSyncManager._sync_checklist()` - Sync acceptance criteria to card
- `TrelloToLocalSync._sync_checklist_to_task()` - Reverse sync checklist state
- `_create_card()` and `_update_card()` now sync checklists automatically

**Sync behavior:**
- Checklist named "Acceptance Criteria" created from task body
- Checkbox state (`- [x]` vs `- [ ]`) preserved during sync
- Reverse sync updates local task file when Trello items are checked
- Preserves indentation when updating task body

**New tests:** 25 tests for checklist functionality
**Test Coverage:** 531 tests passing (up from 506)

### Previous: 2025-12-17 - TASK-085 Complete

**Two-way Sync (TASK-085)** - DONE

Implemented reverse sync from Trello to local task files:

**New classes in `trello/sync.py`:**
- `LIST_TO_STATUS` - Mapping of Trello list names to task statuses
- `SyncConflict` dataclass - Represents sync conflicts with resolution strategy
- `SyncResult` dataclass - Result of sync operation with changes/errors
- `TrelloToLocalSync` class:
  - `extract_task_id()` - Extract task ID from card name
  - `get_list_status()` - Map list name to status
  - `sync_card_to_task()` - Sync single card back to local task
  - `sync_all_cards()` - Sync all cards from board
  - `get_sync_preview()` - Preview changes without applying
- `create_reverse_sync()` - Factory function

**New CLI command in `trello/commands.py`:**
- `bpsai-pair trello sync --from-trello` - Pull changes from Trello
- `bpsai-pair trello sync --preview` - Preview what would change
- `bpsai-pair trello sync --from-trello --list "Done"` - Filter by list

**Conflict resolution:**
- Trello wins for status changes
- Conflicts detected and reported in output
- No data loss (skips when task not found locally)

**New tests:** 21 tests for reverse sync functionality
**Test Coverage:** 506 tests passing (up from 485)

### Previous: 2025-12-17 - TASK-084 Complete

**Effort Field Mapping (TASK-084)** - DONE

The effort mapping was already implemented in TASK-081. This task added:

**Config file support:**
- `TaskSyncConfig.from_config()` - Load sync settings from config.yaml
- `TaskSyncConfig.to_dict()` - Export config for saving
- CLI command now loads effort_mapping from config.yaml

**Config.yaml structure:**
```yaml
trello:
  sync:
    effort_mapping:
      S: [0, 25]
      M: [26, 50]
      L: [51, 100]
```

**New tests:**
- Edge case tests: boundary values (25/26, 50/51), negative values, over 100
- Custom range tests
- Config loading tests: empty config, custom effort mapping, custom fields, full config, to_dict

**Test Coverage:** 485 tests passing (up from 475)

### Previous: 2025-12-17 - TASK-083 Complete

**Card Description Templates (TASK-083)** - DONE

Created `trello/templates.py`:
- `CardDescriptionData` dataclass for template rendering data
- `CardDescriptionTemplate` class with:
  - `extract_sections()` - Parse task body for sections (Objective, Implementation Plan, etc.)
  - `extract_objective()` - Get objective from explicit section or first paragraph
  - `extract_implementation_plan()` - Get plan from section or bullet points
  - `format_acceptance_criteria()` - Render as checkboxes
  - `format_links()` - Render task/PR links section
  - `format_metadata()` - Render footer with complexity/priority/plan
  - `render()` - Full BPS-formatted card description
  - `from_task_data()` - Convenience method for TaskData
- `should_preserve_description()` - Detect manually edited cards
- `DEFAULT_BPS_TEMPLATE` constant with full BPS format

Updated `trello/sync.py`:
- Import new template classes
- Added `card_template` and `preserve_manual_edits` to `TaskSyncConfig`
- Refactored `build_card_description()` to use `CardDescriptionTemplate`
- Added `should_update_description()` to preserve manual edits
- Updated `_update_card()` to check before overwriting descriptions

Created `tests/test_trello_templates.py`:
- 26 tests covering all template functionality
- Tests for BPS format compliance, section extraction, links, metadata

**Test Coverage:** 475 tests passing (up from 449)

### Previous: 2025-12-17 - TASK-082 Complete

**Trello Labels with BPS Colors (TASK-082)** - DONE

Verified and completed the label sync implementation:
- `BPS_LABELS` in `trello/sync.py` defines exact color mappings
- `ensure_bps_labels()` creates missing labels with correct colors before sync
- Labels added based on inferred stack and tag matches
- Multiple labels supported per card

Added 3 new tests for label sync verification.

### Previous: 2025-12-16 - TASK-081 Complete

**Trello Custom Fields Sync (TASK-081)** - DONE

Added to `trello/client.py`:
- `CustomFieldDefinition` dataclass for field metadata
- `EffortMapping` class for complexity → S/M/L mapping
- `get_custom_fields()` - List custom fields on board
- `get_custom_field_by_name()` - Find field by name
- `set_custom_field_value()` - Set text/number/list/checkbox/date fields
- `set_card_custom_fields()` - Bulk set multiple fields
- `set_effort_field()` - Set effort from complexity score
- `create_card_with_custom_fields()` - Create card with fields
- Label management: `get_labels()`, `get_label_by_name()`, `create_label()`, `ensure_label_exists()`, `add_label_to_card()`

Created `trello/sync.py`:
- `TaskData` dataclass with `from_task()` factory
- `TaskSyncConfig` for field mappings and settings
- `TrelloSyncManager` class:
  - `infer_stack()` - Detect stack from task title/tags
  - `build_card_description()` - BPS-formatted descriptions
  - `ensure_bps_labels()` - Create missing labels
  - `sync_task_to_card()` - Create or update card
  - `sync_tasks()` - Batch sync multiple tasks
- `BPS_LABELS` with exact color mappings
- `STACK_KEYWORDS` for inference

Created `tests/test_trello_sync.py`:
- 33 tests for custom fields and sync functionality
- Tests for EffortMapping, TaskData, TrelloSyncManager, TrelloService
- Tests for BPS labels and stack keyword configuration

**Test Coverage:** 445 tests passing (up from 412)

### Previous: Sprint 13 Cleanup

1. Created `.paircoder/history/sprints-1-12-archive.md`
2. Created `.paircoder/tasks/backlog/` directory
3. Moved 6 deprioritized tasks to backlog
4. Updated documentation (README, CHANGELOG, USER_GUIDE, FEATURE_MATRIX)

## Sprint 14 Definition of Done

- [x] `plan sync-trello` creates cards with all custom fields populated
- [x] Labels match exact BPS colors
- [x] Card description follows BPS template
- [x] Moving card in Trello updates local task status
- [x] Checklist items created from acceptance criteria
- [x] All tests passing

## BPS Trello Requirements

### Custom Fields

| Field | Example | Maps From |
|-------|---------|-----------|
| Project | Aurora | plan.title |
| Stack | Flask | task.tags or inferred |
| Status | In Progress | task.status |
| Effort | S / M / L | task.complexity |
| Deployment Tag | v1.2.3 | git tag or manual |

### Label Colors

| Label | Color | Hex |
|-------|-------|-----|
| Frontend | Green | #61bd4f |
| Backend | Blue | #0079bf |
| Worker/Function | Purple | #c377e0 |
| Deployment | Red | #eb5a46 |
| Bug/Issue | Orange | #ff9f1a |
| Security/Admin | Yellow | #f2d600 |
| Documentation | Sky | #00c2e0 |
| AI/ML | Black | #344563 |

## What's Next

1. **TASK-087**: Due date sync
   - Sync due dates between tasks and cards

2. **TASK-088**: Activity log comments
   - Post progress updates as Trello comments

## Blockers

None currently.

## Test Coverage

- **Total tests**: 531 passing
- **Test command**: `pytest -v`
