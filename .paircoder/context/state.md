# Current State

> Last updated: 2025-12-22

## Active Plan

**Plan:** plan-2025-12-sprint-23-cli-refactor-phase2
**Epic:** EPIC-003: CLI Architecture Refactor
**Phase:** Phase 2 of 5 - Extract Commands from planning/cli_commands.py
**Status:** In Progress
**Goal:** Reduce planning/cli_commands.py from ~2,602 → ~600 lines

## Current Sprint Tasks (Sprint 23)

| ID    | Title | Status | Priority | Complexity |
|-------|-------|--------|----------|------------|
| T23.1 | Create sprint/ module structure | done | P0 | 15 |
| T23.2 | Extract sprint commands to sprint/commands.py | done | P1 | 30 |
| T23.3 | Create release/ module structure | done | P0 | 15 |
| T23.4 | Extract release commands to release/commands.py | done | P1 | 45 |
| T23.5 | Extract template commands to release/template.py | done | P1 | 35 |
| T23.6 | Verify standup commands are in separate file | pending | P2 | 10 |
| T23.7 | Verify intent commands are in separate file | pending | P2 | 10 |
| T23.8 | Rename cli_commands.py to commands.py | pending | P1 | 25 |
| T23.9 | Update imports and final cleanup | pending | P0 | 35 |

**Progress:** 5/9 tasks (140/220 complexity points)

## Sprint History

Sprints 1-17.5 archived. See `.paircoder/history/sprint_archive.md`.

| Sprint | Theme | Version | Status |
|--------|-------|---------|--------|
| 1-12 | Foundation → Webhooks | v2.0-2.4 | Archived |
| 13 | Full Autonomy | v2.5 | Complete |
| 14 | Trello Deep Integration | v2.5.1 | Complete |
| 15 | Security & Sandboxing | v2.5.2 | Complete |
| 16 | Real Sub-agents | v2.5.3 | Complete |
| 17 | Time, Tokens & Metrics | v2.5.4 | Complete |
| 17.5 | Backlog Remediation | v2.6.0 | Complete |
| 17.6 | Trello Field Validation Hotfix | v2.6.1 | Complete |
| 18 | Release Engineering | v2.6.1 | Complete |
| 19 | Methodology & Session Management | v2.7.0 | Complete |
| 22 | CLI Refactor Phase 1 | v2.7.0 | Complete |

## What's Next

**Sprint 23: CLI Architecture Refactor (Phase 2)** is planned and ready to start.

**Recommended Task Order:**
1. **T23.1 + T23.3** - Create sprint/ and release/ module structures (parallel)
2. **T23.2** - Extract sprint commands (depends on T23.1)
3. **T23.4 + T23.5** - Extract release and template commands (parallel, depend on T23.3)
4. **T23.6 + T23.7** - Verify standup and intent separation (parallel, quick)
5. **T23.8** - Rename cli_commands.py to commands.py (depends on T23.2, T23.4, T23.5)
6. **T23.9** - Final imports update and cleanup (depends on all above)

**Sprint Goal:**
- Reduce `planning/cli_commands.py` from ~2,602 lines to ~600 lines
- Create `sprint/` module with sprint commands
- Create `release/` module with release and template commands
- Rename to `planning/commands.py` following convention
- No behavior changes - pure refactor

## Backlog (Deprioritized)

See `.paircoder/tasks/backlog/`:
- TASK-063: VS Code extension
- TASK-074: Dashboard UI
- TASK-075: Slack notifications
- TASK-076: Multi-project support

## Session Log

_Add entries here as work is completed._

### 2025-12-22 - T23.5 Complete

- **T23.5: Extract template commands to release/template.py** ✓
  - Extracted `template check` and `template list` commands
  - Created `release/template.py` (202 lines, target < 300)
  - Imports `get_template_path` and `find_paircoder_dir` from `release/commands.py`
  - Updated `cli.py` to import `template_app` from release module
  - `planning/cli_commands.py` reduced to 1942 lines
  - All 1705 tests passing

### 2025-12-22 - T23.4 Complete

- **T23.4: Extract release commands to release/commands.py** ✓
  - Extracted `release plan`, `release checklist`, `release prep` commands
  - Created `release/commands.py` (621 lines, target was < 500 - inherent complexity)
  - Included helper functions: `find_paircoder_dir`, `get_state_manager`, `get_template_path`
  - Updated `cli.py` to import `release_app` from new location
  - Removed ~550 lines from `planning/cli_commands.py`
  - All 1705 tests passing
  - Commands work identically from new location

### 2025-12-22 - T23.3 Complete

- **T23.3: Create release/ module structure** ✓
  - Created `tools/cli/bpsai_pair/release/` directory
  - Created `__init__.py` with `release_app` and `template_app` exports
  - Created placeholder `commands.py` and `template.py`
  - Module imports successfully
  - All 1705 tests passing

### 2025-12-22 - T23.2 Complete

- **T23.2: Extract sprint commands to sprint/commands.py** ✓
  - Extracted `sprint list` and `sprint complete` commands
  - Created `sprint/commands.py` (234 lines, target < 300)
  - Updated `cli.py` to import `sprint_app` from new location
  - Removed 192 lines from `planning/cli_commands.py`
  - All 1705 tests passing
  - Commands work identically from new location

### 2025-12-22 - T23.1 Complete

- **T23.1: Create sprint/ module structure** ✓
  - Created `tools/cli/bpsai_pair/sprint/` directory
  - Created `__init__.py` with `sprint_app` export
  - Created `commands.py` with placeholder Typer app
  - Module imports successfully
  - All 1705 tests passing

### 2025-12-22 - Sprint 23 Planning Complete

- **Sprint 23: CLI Architecture Refactor (Phase 2)** planned
  - Created plan: `plan-2025-12-sprint-23-cli-refactor-phase2`
  - Generated 9 task files (T23.1 through T23.9)
  - Total complexity: 220 points
  - Synced to Trello PairCoder board (Planned/Ready list)
  - 9 cards created on Trello

- **Phase 2 Focus:**
  - Extract sprint commands from `planning/cli_commands.py` → `sprint/commands.py`
  - Extract release commands → `release/commands.py`
  - Extract template commands → `release/template.py`
  - Verify standup/intent already separated
  - Rename `cli_commands.py` → `commands.py`
  - Update imports across codebase

### 2025-12-22 - T22.12 Complete (Sprint 22 Finished!)

- **T22.12: Refactor cli.py to registration only** ✓
  - Extracted session/compaction commands to `commands/session.py` (301 lines)
    - `session check`, `session status`
    - `compaction snapshot save/list`, `compaction check/recover/cleanup`
  - Updated `commands/__init__.py` to export `session_app`, `compaction_app`
  - Refactored `cli.py` to registration-only architecture:
    - **Final line count: 194 lines** (target: < 200)
    - Reduced from original 2,892 lines to 194 lines (93% reduction!)
    - Contains only: imports, app creation, sub-app registration, shortcut commands, version callback
  - All 1705 tests passing
  - All CLI commands work identically (no behavior change)

**Sprint 22 Summary:**
- Created `commands/` package with 12 modules (including session.py)
- Extracted all command implementations from cli.py
- Total line count of command modules: ~3,500 lines
- cli.py reduced by 93%: 2,892 → 194 lines
- Zero behavior changes, pure refactor

### 2025-12-22 - T22.11 Complete

- **T22.11: Extract core commands to commands/core.py** ✓
  - Created `commands/core.py` (782 lines) with 7 commands:
    - `init`, `feature`, `pack`, `context-sync`, `status`, `validate`, `ci`
  - Includes helper functions:
    - `repo_root()`, `_select_ci_workflow()`, `ensure_v2_config()`
    - `print_json()`, `console` initialization
  - Created `register_core_commands(app)` function for registration
  - Updated `commands/__init__.py` to export `register_core_commands`
  - Updated `cli.py`:
    - Removed ~700 lines of core command code
    - Added import for `register_core_commands`
    - Cleaned up unused imports (init_bundled_cli, Config, presets, etc.)
    - Removed unused environment variables (MAIN_BRANCH, CONTEXT_DIR, FLOWS_DIR)
    - Removed unused `_flows_root()` function
  - cli.py now at 441 lines (down from 1172)
  - Updated test imports in `test_cli.py` and `test_config_v2.py`
  - All 1705 tests passing
  - **Note:** core.py is 782 lines (exceeds 500 line target) due to inherent complexity of init, status, and validate commands

### 2025-12-22 - T22.10 Complete

- **T22.10: Extract security commands to commands/security.py** ✓
  - Created `commands/security.py` (270 lines) with 4 commands:
    - `security scan-secrets`, `security pre-commit`, `security install-hook`, `security scan-deps`
  - Included helper function: `_get_secret_scanner()`
  - Kept shortcut commands in cli.py: `bpsai-pair scan-secrets`, `bpsai-pair scan-deps`
  - Updated `commands/__init__.py` to export security_app
  - Removed ~240 lines of security code from cli.py
  - cli.py now at 1172 lines (down from ~2892!)
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.9 Complete

- **T22.9: Extract flow commands to commands/flow.py** ✓
  - Created `commands/flow.py` (296 lines) with 4 commands:
    - `flow list`, `flow show`, `flow run`, `flow validate`
  - Included helper functions: `_flows_root()`, `_find_flow_v2()`
  - Updated `commands/__init__.py` to export flow_app
  - Removed ~230 lines of flow code from cli.py (scattered)
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.8 Complete

- **T22.8: Extract mcp commands to commands/mcp.py** ✓
  - Created `commands/mcp.py` (127 lines) with 3 commands:
    - `mcp serve`, `mcp tools`, `mcp test`
  - Updated `commands/__init__.py` to export mcp_app
  - Removed ~90 lines of mcp code from cli.py
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.7 Complete

- **T22.7: Extract cache commands to commands/cache.py** ✓
  - Created `commands/cache.py` (103 lines) with 3 commands:
    - `cache stats`, `cache clear`, `cache invalidate`
  - Updated `commands/__init__.py` to export cache_app
  - Removed ~53 lines of cache code from cli.py
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.6 Complete

- **T22.6: Extract benchmark commands to commands/benchmark.py** ✓
  - Created `commands/benchmark.py` (193 lines) with 4 commands:
    - `benchmark run`, `benchmark results`, `benchmark compare`, `benchmark list`
  - Included helper function: `_get_benchmark_paths()`
  - Updated `commands/__init__.py` to export benchmark_app
  - Removed ~137 lines of benchmark code from cli.py
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.5 Complete

- **T22.5: Extract timer commands to commands/timer.py** ✓
  - Created `commands/timer.py` (199 lines) with 5 commands:
    - `timer start`, `timer stop`, `timer status`, `timer show`, `timer summary`
  - Included helper function: `_get_time_manager()`
  - Updated `commands/__init__.py` to export timer_app
  - Removed ~145 lines of timer code from cli.py
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.4 Complete

- **T22.4: Extract metrics commands to commands/metrics.py** ✓
  - Created `commands/metrics.py` (547 lines) with 10 commands:
    - `summary`, `task`, `breakdown`, `budget`, `export`
    - `velocity`, `burndown`, `accuracy`, `tokens`
  - Included helper functions for metrics, velocity, burndown, accuracy, tokens
  - Removed ~480 lines of metrics code from cli.py
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.3 Complete

- **T22.3: Extract orchestrate commands to commands/orchestrate.py** ✓
  - Created `commands/orchestrate.py` (381 lines) with 7 commands:
    - `orchestrate task`, `analyze`, `select-agent`, `handoff`
    - `auto-run`, `auto-session`, `workflow-status`
  - Included helper functions: `repo_root()`, `_load_task_metadata()`
  - Updated `commands/__init__.py` to export orchestrate_app
  - Removed ~320 lines of orchestrate code from cli.py
  - All 47 related tests passing

### 2025-12-22 - T22.2 Complete

- **T22.2: Extract config commands to commands/config.py** ✓
  - Created `commands/config.py` (195 lines) with:
    - `config validate` command
    - `config update` command
    - `config show` command
  - Updated `commands/__init__.py` to export config_app
  - Updated `cli.py` imports to use new module
  - Removed ~170 lines of config code from cli.py
  - All 14 config-related tests passing
  - All 45 test_cli.py tests passing

### 2025-12-22 - T22.1 Complete

- **T22.1: Extract preset commands to commands/preset.py** ✓
  - Created `tools/cli/bpsai_pair/commands/` directory
  - Created `commands/__init__.py` with preset_app export
  - Created `commands/preset.py` (149 lines) with:
    - `preset list` command
    - `preset show` command
    - `preset preview` command
  - Updated `cli.py` imports to use new module
  - Removed 120 lines of preset code from cli.py
  - All 40 preset-related tests passing
  - All 45 test_cli.py tests passing

### 2025-12-22 - Sprint 22 Planning Complete

- **Sprint 22: CLI Architecture Refactor (Phase 1)** planned
  - Created plan: `plan-2025-12-sprint-22-cli-refactor-phase1`
  - Generated 12 task files (T22.1 through T22.12)
  - Total complexity: 330 points
  - Synced to Trello PairCoder board (Planned/Ready list)
  - 12 cards created on Trello

- **EPIC-003 Analysis:**
  - Total effort: XL (~80-100 hours across 4-5 sprints)
  - Phase 1: Extract from cli.py (Sprint 22) - 12 tasks
  - Phase 2: Extract from planning/cli_commands.py (Sprint 23) - 9 tasks
  - Phase 3: Consolidate root files (Sprint 24) - 10 tasks
  - Phase 4: Consolidate parsers (Sprint 24-25) - 3 tasks
  - Phase 5: Documentation & cleanup (Sprint 25) - 5 tasks

### 2025-12-22 - v2.7.0 Released

- **Release v2.7.0** ✓
  - Ran e2e documentation checks (release prep)
  - Fixed skill validator CLI registration (missing import/registration in cli.py)
  - Fixed velocity tests (week boundary edge cases on Mondays)
  - Fixed map_and_validate test (4-tuple return value)
  - All 1705 tests passing
  - Bumped version to 2.7.0 in pyproject.toml
  - Updated CHANGELOG.md with Sprint 19 features
  - Built and validated package
  - Committed and tagged v2.7.0
  - Published to PyPI: https://pypi.org/project/bpsai-pair/2.7.0/

### 2025-12-22 - T19.10 Complete (Hotfix)

- **T19.10: Add `bpsai-pair migrate` command** ✓
  - Created `tools/cli/bpsai_pair/migrate.py` with:
    - `LegacyVersion` enum (V1_LEGACY, V2_EARLY, V2_PARTIAL, V2_CURRENT, UNKNOWN)
    - `detect_version()` - detects PairCoder structure version
    - `plan_migration()` - creates migration plan based on detected version
    - `create_backup()` - timestamped backup of .paircoder/ and .claude/
    - `execute_migration()` - executes migration plan
    - `migrate_app` Typer CLI app with commands
  - CLI commands:
    - `bpsai-pair migrate` - Run migration (with confirmation)
    - `bpsai-pair migrate --dry-run` - Show plan without changes
    - `bpsai-pair migrate --no-backup` - Skip backup creation
    - `bpsai-pair migrate --force` - Skip confirmation prompt
    - `bpsai-pair migrate status` - Show current version status
  - Migration capabilities:
    - v1.x → v2.5: Full structure migration, file moves, config creation
    - v2.0-2.3 → v2.5: Add missing dirs, config sections (trello, hooks, etc.)
  - Created `tests/test_migrate.py` with 29 tests covering all functionality
  - All 29 tests passing
  - Registered in CLI as `bpsai-pair migrate`

### 2025-12-22 - T19.6 Complete (Sprint 19 Done!)

- **T19.6: Merge trello-task-workflow into paircoder-task-lifecycle** ✓
  - Consolidated skills: deleted `.claude/skills/trello-task-workflow/`, kept `paircoder-task-lifecycle`
  - Moved BPS conventions reference to `paircoder-task-lifecycle/reference/bps-trello-conventions.md`
  - Renamed flow file: `trello-task-workflow.flow.md` → `paircoder-task-lifecycle.flow.md`
  - Updated references in:
    - `.paircoder/docs/FEATURE_MATRIX.md` (skill count 6→5, skill name)
    - `README.md` (skill list)
    - `CLAUDE.md` in cookiecutter template
    - `capabilities.yaml` in cookiecutter template
    - `test_template.py` (expected skills/flows)
  - Deleted nested leftover directory in cookiecutter template
  - Skill validates with `bpsai-pair skill validate paircoder-task-lifecycle`
  - All 20 template tests passing

### 2025-12-22 - T19.7 Complete

- **T19.7: Document Built-in Claude Code Commands** ✓
  - Created `docs/CLAUDE_CODE_INTEGRATION.md` with:
    - Built-in Claude Code commands we leverage (/compact, /context, /plan)
    - Commands to avoid conflicting with
    - How PairCoder commands complement built-ins
    - Context management best practices
    - Session management workflow
    - Planning integration guidance
    - Skills and tools comparison
    - Command quick reference
    - Best practices section
    - Troubleshooting tips
  - Updated `.paircoder/docs/USER_GUIDE.md`:
    - Added "Claude Code Integration" section (#24)
    - Added reference to full integration guide
    - Added key points summary
    - Added quick reference table

### 2025-12-22 - T19.5 Complete

- **T19.5: Skill Validator CLI** ✓
  - Created `tools/cli/bpsai_pair/skills/` module with:
    - `validator.py`: `SkillValidator` class with validation rules
    - `cli_commands.py`: `skill validate` and `skill list` CLI commands
  - Validation checks:
    - Frontmatter has only `name` and `description` fields (error if extra)
    - Description under 1024 characters (error if exceeded)
    - 3rd-person voice (warning on 2nd person like "you")
    - File under 500 lines (error if exceeded)
    - Name matches directory name (error if mismatch)
    - Gerund naming preferred (warning on non-gerund like "code-review")
  - CLI commands:
    - `bpsai-pair skill validate` - Validates all skills in .claude/skills/
    - `bpsai-pair skill validate <name>` - Validates specific skill
    - `bpsai-pair skill validate --fix` - Auto-corrects simple issues
    - `bpsai-pair skill validate --json` - JSON output
    - `bpsai-pair skill list` - Lists all skills
  - Created `tests/test_skill_validator.py` with 16 tests covering all rules
  - All 16 tests passing
  - Validates 7 existing skills: 7 pass, 1 warning (code-review naming)

### 2025-12-22 - T19.9 Complete

- **T19.9: Detect Manual Task File Edits** ✓
  - Created `tools/cli/bpsai_pair/planning/cli_update_cache.py` module with:
    - `CLIUpdateCache` class for tracking CLI status updates per task
    - `detect_manual_edit()` function to detect file edits outside CLI
    - `get_cli_update_cache()` helper function
  - Updated `tools/cli/bpsai_pair/planning/cli_commands.py`:
    - `task update` now records to CLI cache on successful updates
    - Added `--resync` flag to re-trigger hooks for current status
    - `task list` now checks for manual edits and shows warnings
    - Added `_check_for_manual_edits()` helper function
  - Created `tests/test_manual_edit_detection.py` with 13 tests:
    - CLIUpdateCache CRUD operations
    - Manual edit detection logic
    - Resync flag functionality
    - CLI integration tests
  - All 13 tests passing
  - Detection shows: task ID, file status vs CLI status, resync command

### 2025-12-22 - T19.8 Complete

- **T19.8: ttask done Should Verify/Auto-Check Acceptance Criteria** ✓
  - Updated `tools/cli/bpsai_pair/trello/task_commands.py`:
    - Added `_get_unchecked_ac_items()` helper function
    - Refactored `task_done` command with new AC verification behavior:
      - Default: verifies AC items are checked, blocks with list of unchecked items
      - `--check-all` flag: auto-checks all AC items then completes
      - `--force` flag: skips verification, logs warning
      - `--skip-checklist` flag: legacy behavior preserved
    - Completion comment now includes AC status
  - Created `tests/test_ttask_done_ac_verification.py` with 13 tests:
    - Warns with unchecked AC items (default behavior)
    - --check-all checks items and completes
    - --force skips verification
    - No checklists/No AC checklist succeeds
    - All AC checked succeeds
    - Case-insensitive AC checklist matching
    - Completion comment mentions AC status
    - Backwards compatibility with --skip-checklist
    - Helper function unit tests
  - All 13 tests passing
  - Full Trello test suite passing (243/244, 1 pre-existing failure unrelated)

### 2025-12-22 - T19.4 Complete

- **T19.4: Token-Aware Batch Planning** ✓
  - Created `tools/cli/bpsai_pair/planning/token_estimator.py` module with:
    - `PlanTokenEstimator` class for plan-level estimation
    - `TaskTokenEstimate`, `BatchSuggestion`, `PlanTokenEstimate` dataclasses
    - Batching algorithm that suggests task groupings to stay under threshold
    - Formatted output with breakdown by component
  - Added CLI command `bpsai-pair plan estimate <plan-id>`:
    - Shows breakdown: base context, tasks, files touched
    - Warns when plan exceeds threshold (default 50k tokens)
    - Suggests batching strategy with specific task groupings
    - Supports `--threshold` flag for custom limit
    - Supports `--json` flag for JSON output
    - Supports `--no-tasks` to hide per-task breakdown
  - Added `_populate_files_touched` helper to parse "Files to Modify" from tasks
  - Created `tests/test_plan_estimate.py` with 14 tests covering:
    - Command existence and help
    - Output breakdown verification
    - Config values usage
    - Task type multiplier effects
    - File token calculation
    - Threshold warnings and batching suggestions
    - JSON output format
    - Plan not found error handling
    - PlanTokenEstimator class unit tests
  - All 14 tests passing

### 2025-12-22 - T19.3 Complete

- **T19.3: Compaction Detection and Recovery** ✓
  - Created `tools/cli/bpsai_pair/compaction.py` module with:
    - `CompactionManager` class for snapshot management
    - `CompactionSnapshot` and `CompactionMarker` data classes
    - Snapshot creation with state.md context extraction
    - Recent files tracking from changes.log
    - Compaction event logging to history
  - Added CLI commands:
    - `bpsai-pair compaction snapshot save` - Creates pre-compaction snapshot
    - `bpsai-pair compaction snapshot list` - Lists available snapshots
    - `bpsai-pair compaction check` - Detects unrecovered compaction
    - `bpsai-pair compaction recover` - Restores context after compaction
    - `bpsai-pair compaction cleanup` - Removes old snapshots
  - Added `PreCompact` hook to `.claude/settings.json`
    - Runs before `/compact` or auto-compaction
    - Saves snapshot with trigger type ($CLAUDE_COMPACT_TRIGGER)
  - Integrated compaction check into `session check` command
    - Auto-recovers context if compaction detected
    - Runs via UserPromptSubmit hook on each message
  - Updated cookiecutter template with PreCompact hook
  - Created `tests/test_compaction.py` with 14 tests covering:
    - Snapshot creation and listing
    - Compaction detection with/without markers
    - Context recovery and marker updates
    - History logging
    - CLI command help and functionality
  - All 14 tests passing

### 2025-12-22 - T19.2 Complete

- **T19.2: Session Restart Enforcement** ✓
  - Created `tools/cli/bpsai_pair/session.py` module with:
    - `SessionManager` class for session tracking
    - `SessionState` and `SessionContext` data classes
    - Session detection based on 30 min timeout (configurable)
    - Context parsing from state.md
  - Added CLI commands:
    - `bpsai-pair session check` - Detects new session and displays context
    - `bpsai-pair session status` - Shows current session info
  - Added `UserPromptSubmit` hook to `.claude/settings.json`
    - Runs on every user message
    - Shows context summary on new session (>30 min gap)
    - Silent on continuing session
  - Updated cookiecutter template with UserPromptSubmit hook
  - Created `tests/test_session.py` with 12 tests covering:
    - New session detection (no cache, timeout)
    - Continuing session detection
    - Timestamp updates
    - Context output format
    - Session history logging
    - Custom timeout configuration
    - Force flag functionality
  - All 12 tests passing

### 2025-12-22 - T19.1 Complete

- **T19.1: Mandatory state.md Update Hook** ✓
  - Added pre-completion check to `task update --status done` command
  - Block completion if state.md wasn't updated since task started
  - Uses timer start time from `time-tracking-cache.json` as reference
  - Falls back to task file modification time if no timer
  - Added `--skip-state-check` flag for emergency bypass (logs warning)
  - Helpful error message tells user what to update in state.md
  - Created `tests/test_state_check.py` with 7 tests covering:
    - Blocking when state.md not updated
    - Allowing when state.md was updated
    - Bypass flag functionality
    - Only applies to `done` status
    - Handling tasks without active timer
    - Error message includes instructions and task ID
  - All 7 tests passing

### 2025-12-22 - Sprint 19 Planning Complete

- **Sprint 19 Setup**
  - Created plan: `plan-2025-12-sprint-19-methodology`
  - Generated 9 task files (T19.1 through T19.9)
  - Total complexity: 340 points
  - Synced to Trello PairCoder board (Planned/Ready list)
  - Fixed bug in `trello/sync.py` - `map_and_validate` returns 4 values, was unpacking 3

- **E2E Test Coverage Added** (post-incident)
  - Created `tools/cli/tests/test_plan_sync_trello_e2e.py` (10 tests)
  - Tests exercise full path through `validate_and_map_custom_fields`
  - Verified tests catch the tuple unpacking bug when fix is reverted
  - Root cause: existing unit tests mocked `field_validator`, never exercising real `map_and_validate`

- **Field Mapping Issues Fixed** (post-incident)
  - Status mapping: `pending` → `Planning` (was "To do")
  - Project field: Now uses `config.default_project` (was `task.plan_title`)
  - Stack inference: Split `infer_label()` from `infer_stack()`, added `LABEL_TO_STACK_MAPPING`
    - "Documentation" → "Collection", "Frontend" → "React", etc.
  - Added `default_project` and `default_stack` to `TaskSyncConfig`
  - Updated 149 tests to match new BPS board conventions

**Tasks by Priority:**
- P0 (Critical): T19.1, T19.2 - Methodology enforcement
- P1 (High): T19.3, T19.4, T19.8, T19.9 - Session management, workflow
- P2 (Medium): T19.5, T19.7 - Tooling, docs
- P3 (Low): T19.6 - Skill consolidation

### 2025-12-22 - T18.4 Complete (Sprint 18 Finished!)

- **T18.4: Release Engineering Documentation** ✓
  - Created `docs/RELEASING.md` with step-by-step release guide
    - Version location (single source: pyproject.toml)
    - CHANGELOG format and conventions
    - How to use `bpsai-pair release prep`
    - Cookie cutter sync process with `template check`
    - CI/CD pipeline overview
    - Git tagging and GitHub release creation
    - Troubleshooting section
  - Updated `CONTRIBUTING.md` with release section
    - Who can release
    - Release cadence
    - Pre-release checklist
  - Updated `.github/PULL_REQUEST_TEMPLATE.md` with release checklist
    - Version bump verification
    - CHANGELOG check
    - release prep validation
    - Template sync check
    - Package exports verification
  - References T18.1, T18.2, T18.3 tooling throughout

### 2025-12-22 - T18.3 Complete

- **T18.3: Cookie Cutter Drift Detection CLI** ✓
  - Added `bpsai-pair template check` command
  - Compares source files with cookiecutter template
  - Shows drift with line diff counts
  - Supports `--fail-on-drift` for CI enforcement
  - Supports `--fix` to auto-sync template from source
  - Added `bpsai-pair template list` command to list template files
  - Created `.github/workflows/template-check.yml` for CI
  - Integrated template drift check into `release prep` command
  - Created `tests/test_template_check.py` with 13 tests
  - All 32 related tests passing

### 2025-12-22 - T18.2 Complete

- **T18.2: Create Release Prep Command** ✓
  - Added `bpsai-pair release prep` command to planning/cli_commands.py
  - Checks: version consistency, CHANGELOG entry, git status, tests, doc freshness
  - Supports `--since` flag for baseline comparison
  - Supports `--create-tasks` flag to generate tasks for issues
  - Uses status icons (✅ ❌ ⚠️) for clear output
  - Created `tests/test_release_prep.py` with 14 tests
  - Added release config section to `.paircoder/config.yaml`
  - Cookie cutter integration placeholder for T18.3

### 2025-12-22 - T18.1 Complete

- **T18.1: Fix Version String Single Source of Truth** ✓
  - Confirmed `__init__.py` already uses `importlib.metadata.version("bpsai-pair")`
  - Created `tests/test_version.py` with 5 tests:
    - Version matches pyproject.toml
    - No hardcoded version in __init__.py
    - Uses importlib.metadata correctly
    - CLI --version shows correct version
    - Version follows semver format
  - All acceptance criteria verified and passing

### 2025-12-22 - v2.6.1 Release

- Bumped version to 2.6.1 in pyproject.toml
- Updated CHANGELOG.md with Trello field validation improvements
- Added sprint 17.6 (hotfix) to history
- Created and pushed git tag v2.6.1

### 2025-12-21 - Sprint 18 Planning

- Created plan: `plan-2025-12-sprint-18-release-engineering`
- Generated 4 task files (T18.1 through T18.4)
- Synced to Trello PairCoder board (Planned/Ready list)
- Total complexity: 120 points

### 2025-12-21 - Context Cleanup

- Archived Sprints 13-17.5 to sprint_archive.md
- Trimmed state.md from ~1450 to ~100 lines
- Deleted obsolete files
- Reorganized context directory
- Ready for Sprint 18
