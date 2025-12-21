# Current State

> Last updated: 2025-12-19 (afternoon session)

## Active Plan

**Plan:** `plan-2025-12-backlog-remediation`
**Status:** Active
**Current Sprint:** sprint-17.5

**Previous:** `plan-2025-12-sprint-17-time-tokens-metrics` (complete)

## Current Focus

Backlog Remediation: Bugs, Missing Features & Documentation

**Sprint 17.5 Tasks (Critical Fixes):**
- TASK-150: Cookie cutter template full audit and sync (P0, 60 pts) ✓
- TASK-151: Add missing config sections to all presets (P0, 30 pts) ✓
- TASK-152: Fix Task model missing depends_on field (P1, 20 pts) ✓
- TASK-153: Fix plan list showing 0 tasks (P1, 15 pts) ✓

**Progress:** 4/4 tasks complete (125/125 points) ✅ Sprint 17.5 Phase1 Complete!

**Sprint 17.5 Tasks (Documentation & Structure):**
- TASK-154: Document BPS Trello board conventions ✓
- TASK-155: Add /commands directory to cookie cutter ✓
- TASK-156: Reorganize docs/ vs .paircoder/docs/ ✓
- TASK-157: Document Trello setup in quick start ✓
- TASK-158: Clarify task update vs ttask workflow ✓

**Sprint 17.5 Tasks (Enhancements):**
- TASK-159: Trello board initialization from template ✓
- TASK-160: Sprint completion checklist enforcement ✓
- TASK-161: Config validate and update command
- TASK-162: CLI commands for Trello custom fields
- TASK-163: Preset-specific CI workflows
- TASK-164: Document slash commands feature

**Total:** 15 tasks (445 complexity points)

## Task Status

### Sprint 1-12: Archived

See `.paircoder/history/sprints-1-12-archive.md` for historical details.

### Sprint 13: Full Autonomy - COMPLETE

All tasks completed. See Sprint 13 section in archive.

### Sprint 14: Trello Deep Integration - COMPLETE

All 8 tasks completed:
- TASK-081: Sync Trello custom fields ✓
- TASK-082: Sync Trello labels with exact BPS colors ✓
- TASK-083: Card description templates (BPS format) ✓
- TASK-084: Effort → Trello Effort field mapping ✓
- TASK-085: Two-way sync (Trello → local) ✓
- TASK-086: Support checklists in cards ✓
- TASK-087: Due date sync ✓
- TASK-088: Activity log comments ✓

### Sprint 15: Security & Sandboxing - COMPLETE ✅

All 7 tasks completed (250/250 points).

### Sprint 16: Real Sub-agents - COMPLETE ✅

All 6 tasks completed (225/225 points).

| Task | Title | Status | Priority | Complexity |
|------|-------|--------|----------|------------|
| TASK-096 | Agent invocation framework | **done** | P0 | 45 |
| TASK-097 | Planner agent implementation | **done** | P1 | 35 |
| TASK-098 | Reviewer agent implementation | **done** | P1 | 35 |
| TASK-099 | Security agent implementation | **done** | P0 | 40 |
| TASK-100 | Agent handoff protocol | **done** | P1 | 40 |
| TASK-101 | Agent selection logic | **done** | P0 | 30 |

**Progress:** 6/6 tasks complete (225/225 points)

### Backlog (Deprioritized)

Tasks in `.paircoder/tasks/backlog/`:
- TASK-063: VS Code extension
- TASK-064: Status bar widget
- TASK-065: Auto-context on save
- TASK-074: Dashboard UI
- TASK-075: Slack notifications
- TASK-076: Multi-project support

## What Was Just Done

### Session: 2025-12-21 - TASK-160: Sprint Completion Checklist Enforcement

**TASK-160: Sprint completion checklist enforcement** - DONE

Added CLI commands to enforce sprint completion checklist and generate release preparation tasks.

**New Commands:**

```bash
# Sprint completion with checklist
bpsai-pair sprint complete 17.5 [--force] [--plan PLAN_ID]

# List sprints in a plan
bpsai-pair sprint list [--plan PLAN_ID]

# Generate release preparation tasks
bpsai-pair release plan [--sprint SPRINT] [--version VERSION] [--create]

# Show release checklist
bpsai-pair release checklist
```

**Sprint Complete Checklist Items:**
1. Cookie cutter template synced
2. CHANGELOG.md updated
3. Documentation updated
4. Tests passing
5. Version bumped (if release)

**Release Plan Generated Tasks:**
- REL-001: Sync cookie cutter template with project changes
- REL-002: Update CHANGELOG.md with release notes
- REL-003: Bump version number (version update)
- REL-004: Update documentation for new features
- REL-005: Final release verification

**Files Modified:**
- `tools/cli/bpsai_pair/planning/cli_commands.py` - Added `sprint_app` and `release_app` with commands
- `tools/cli/bpsai_pair/cli.py` - Registered new command groups
- `tools/cli/tests/test_cli.py` - Added 9 tests for new commands

**Bug Fixes:**
- Fixed `state.active_plan` → `state.active_plan_id` attribute error in multiple places

**Tests:** All 9 sprint/release tests passing

---

### Session: 2025-12-21 - TASK-159: Trello Board Initialization from Template

**TASK-159: Trello board initialization from template** - DONE

Added new CLI command to create Trello boards from templates, preserving Butler rules, custom fields, and labels.

**New Command:**
```bash
bpsai-pair trello init-board --name "My New Project" --from-template "BPS AI Project Template"
```

**Features:**
- Find template board by name (case-insensitive)
- Copy board preserving: lists, custom fields, labels, Butler automation rules
- Optional `--keep-cards` flag to copy template cards
- Automatically sets new board as active for the project
- Shows summary of lists, custom fields, and labels copied

**Files Created/Modified:**
- `tools/cli/bpsai_pair/trello/client.py` - Added `find_board_by_name()`, `copy_board_from_template()`, `get_board_info()` methods
- `tools/cli/bpsai_pair/trello/commands.py` - Added `init-board` CLI command
- `tools/cli/tests/test_trello_client.py` - Added 9 tests for new functionality

**API Implementation:**
Uses Trello API `/boards` POST with `idBoardSource` and `keepFromSource` parameters to preserve board structure.

---

### Session: 2025-12-21 - TASK-158: Clarify task update vs ttask Workflow

**TASK-158: Clarify task update vs ttask workflow** - DONE

Clarified when to use `task update` vs `ttask` commands to eliminate confusion in skills documentation.

**Key Clarification:**
```
Is Trello connected?
├── YES → Use `ttask` commands (they handle everything)
└── NO  → Use `task update` commands
```

**Main Changes:**

1. **Decision tree added** to paircoder-task-lifecycle skill showing when to use each command
2. **Simplified completion process** - `ttask done` now handles everything, no need for two-step process
3. **"Don't Mix Commands" table** added to prevent common mistakes
4. **Updated USER_GUIDE.md** with decision tree in Tasks section

**Files Modified:**
- `.claude/skills/paircoder-task-lifecycle/SKILL.md` - Added decision tree, simplified completion
- `.claude/skills/trello-task-workflow/SKILL.md` - Added "When to Use" section, clarified one-command completion
- Template: `.claude/skills/paircoder-task-lifecycle/SKILL.md`
- Template: `.claude/skills/trello-task-workflow/SKILL.md`
- Template: `.paircoder/docs/USER_GUIDE.md`

**Before:** Confusing two-step process (`ttask done` + `task update`)
**After:** Simple rule - if Trello connected, just use `ttask` commands

---

### Session: 2025-12-21 - TASK-157: Document Trello Setup in Quick Start Guide

**TASK-157: Document Trello setup in quick start guide** - DONE

Added comprehensive Trello setup documentation so new users know how to connect their Trello boards.

**Changes Made:**

1. **README.md** - Added "Trello Setup" section before Trello commands with:
   - Step-by-step API credential setup
   - Environment variable configuration
   - Board connection commands

2. **cli.py** - Updated `bpsai-pair init` output to show:
   - Next steps after initialization
   - Optional Trello connection instructions
   - Link to full documentation

3. **USER_GUIDE.md** (template) - Added full Trello Integration section with:
   - 5-step setup guide with detailed instructions
   - Working with Trello tasks commands
   - Syncing plans to Trello
   - Troubleshooting common issues

**Files Modified:**
- `README.md`
- `tools/cli/bpsai_pair/cli.py`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/docs/USER_GUIDE.md`

---

### Session: 2025-12-21 - TASK-156: Reorganize docs/ vs .paircoder/docs/

**TASK-156: Reorganize docs/ vs .paircoder/docs/ structure** - DONE

Reorganized documentation structure in the cookie cutter template to clearly separate PairCoder documentation from project-specific documentation.

**New Structure:**
```
.paircoder/docs/      # PairCoder documentation (ships with template)
├── USER_GUIDE.md     # How to use PairCoder
├── MCP_SETUP.md      # MCP server configuration
└── FEATURE_MATRIX.md # Capabilities reference

docs/                 # Project-specific documentation (user-created)
└── .gitkeep          # Placeholder for architecture.md, api.md, etc.
```

**Files Created:**
- `.paircoder/docs/MCP_SETUP.md` - MCP server configuration guide
- `.paircoder/docs/FEATURE_MATRIX.md` - PairCoder capabilities reference
- `docs/.gitkeep` - Placeholder with instructions

**Files Moved:**
- `docs/USER_GUIDE.md` → `.paircoder/docs/USER_GUIDE.md`

**Files Modified:**
- `CLAUDE.md` - Added Documentation section, updated directory structure
- `.paircoder/capabilities.yaml` - Added docs and project_docs directories
- `CHANGELOG.md` - Added migration guide for existing projects

---

### Session: 2025-12-21 - TASK-155: Add /commands Directory to Cookie Cutter Template

**TASK-155: Add /commands directory to cookie cutter template** - DONE

Added slash commands capability to the cookie cutter template so new projects get this feature out of the box.

**Files Created:**
- `.claude/commands/status.md` - Shows project status, current sprint, active tasks
- `.claude/commands/plan.md` - Shows current plan details and progress
- `.claude/commands/task.md` - Shows current or specific task details

**Files Modified:**
- `CLAUDE.md` - Added "Slash Commands" section documenting `/status`, `/plan`, `/task`
- `CLAUDE.md` - Updated directory structure to include `commands/` directory

**Template Location:**
`tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/commands/`

---

### Session: 2025-12-21 - TASK-154: Document BPS Trello Board Conventions

**TASK-154: Document BPS Trello board conventions** - DONE

Created documentation for BPS-specific Trello board conventions to prevent AI agents from:
- Moving dashboard/Info list cards
- Leaving custom fields empty
- Not checking acceptance criteria on completion
- Not adding PR URLs to cards

**Files Created:**
- `.paircoder/context/bps-board-conventions.md` - Comprehensive reference document for board conventions
- `.claude/skills/trello-task-workflow/reference.md` - Skill-specific reference for task workflow
- `.claude/skills/trello-aware-planning/reference.md` - Skill-specific reference for planning

**Files Modified:**
- `.claude/skills/trello-task-workflow/SKILL.md` - Added pointer to reference.md
- `.claude/skills/trello-aware-planning/SKILL.md` - Added pointer to reference.md

**Design Decision:**
Kept skill files generic with project-specific conventions in separate `reference.md` files. This allows skills to be reusable while still having project-specific customizations.

---

### Session: 2025-12-19 (afternoon) - TASK-153: Fix Plan List Task Count

**TASK-153: Fix plan list showing 0 tasks** - DONE

Fixed the `plan list` command to show accurate task counts instead of always showing 0.

**Root Cause:**
The command used `len(plan.tasks)` which counted task summaries embedded in the plan file, not actual task files with matching `plan_id`.

**Fix:**
Changed `cli_commands.py` to use `TaskParser.get_tasks_for_plan(plan.id)` which counts actual task files that have the matching `plan_id` in their frontmatter.

**Changes:**
- `tools/cli/bpsai_pair/planning/cli_commands.py` - Added `TaskParser` instance and used `get_tasks_for_plan()` to count actual tasks

**Verification:**
```
$ bpsai-pair plan list
                                   Plans (2)
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ ID                    ┃ Title                 ┃ Type    ┃ Status     ┃ Tasks ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│ plan-2025-12-backlog… │ Backlog Remediation   │ feature │ 📋 planned │    15 │
│ plan-2025-12-sprint-… │ Time, Tokens & ...    │ feature │ 📋 planned │     8 │
└───────────────────────┴───────────────────────┴─────────┴────────────┴───────┘
```

**Tests:** All 1282 tests pass (excluding pre-existing trello_sync failure)

---

### Session: 2025-12-19 (afternoon) - TASK-152: Fix depends_on Field

**TASK-152: Fix Task model missing depends_on field** - DONE

Fixed the `'Task' object has no attribute 'depends_on'` error that occurred during task completion.

**Root Cause:**
The `check_unblocked` hook tried to access `task.depends_on` but the Task model didn't have this field.

**Changes:**

1. **`planning/models.py`** - Task dataclass:
   - Added `depends_on: list[str] = field(default_factory=list)` field
   - Updated `to_dict()` to include `depends_on` in serialization
   - Updated `from_dict()` to parse `depends_on` with default empty list

2. **`hooks.py`** - `_check_unblocked` method:
   - Changed from `task.depends_on` to `getattr(task, 'depends_on', None) or []`
   - Provides backwards compatibility with old task objects

**Tests:**
- All 34 hooks tests pass
- Manual verification: Task model correctly handles depends_on field
- Manual verification: Task update completes without error

**Files modified:**
- `tools/cli/bpsai_pair/planning/models.py`
- `tools/cli/bpsai_pair/hooks.py`

---

### Session: 2025-12-19 (afternoon) - TASK-151: Add Missing Config Sections

**TASK-151: Add missing config sections to all presets** - DONE

Updated `presets.py` so all presets generate complete configs with all required sections:

**Changes to Preset dataclass:**
- Added `estimation_config`, `metrics_config`, `security_config` fields

**Changes to `to_config_dict()`:**
- Bumped version from 2.4 to 2.6
- Added default `routing` section (with complexity-based model routing)
- Added default `trello` section (with empty board_id, sync settings, list_mappings)
- Added default `estimation` section (complexity_to_hours, token_estimates)
- Added default `metrics` section (enabled: true, store_path)
- Added default `hooks` section (Sprint 17 hooks: record_velocity, record_token_usage)
- Added default `security` section (allowlist_path, secrets_allowlist_path, sandbox)

**Updated `bps` preset:**
- Added `record_token_usage` and `update_state` hooks to match current standards

**Tests added (9 new):**
- `test_to_config_dict_has_all_sections`
- `test_to_config_dict_trello_defaults`
- `test_to_config_dict_estimation_defaults`
- `test_to_config_dict_hooks_defaults`
- `test_to_config_dict_security_defaults`
- `test_to_config_dict_metrics_defaults`
- `test_all_presets_generate_complete_config`
- `test_bps_preset_has_custom_trello_config`
- `test_bps_preset_has_custom_hooks`

**Files modified:**
- `tools/cli/bpsai_pair/presets.py`
- `tools/cli/tests/test_presets.py`

**Test Results:** 36 preset tests, all passing

---

### Session: 2025-12-19 (afternoon) - TASK-150: Cookie Cutter Template Audit

**TASK-150: Cookie cutter template full audit and sync** - DONE

Full audit of all cookie cutter template files against current paircoder source, with fixes applied:

**Template Files Updated:**

1. **`.paircoder/context/state.md`** - Updated to current format:
   - Added `**Current Sprint:**` field
   - Added `### Active Sprint` and `### Backlog` sections
   - Added session entry format with date
   - Added quick commands including `ttask done` workflow

2. **`.paircoder/context/project.md`** - Made more useful:
   - Added full repository structure diagram
   - Renamed sections (Overview → What Is This Project?)
   - Added `.claude/` directory to structure
   - Added How to Work Here section
   - Added Testing/Building sections

3. **`.paircoder/context/workflow.md`** - Updated to current format:
   - Added table format for branch strategy
   - Added NON-NEGOTIABLE requirement for state.md updates
   - Added Definition of Done checklist
   - Added Trello commands to CLI reference
   - Added JavaScript/TypeScript to code style section

4. **`.paircoder/capabilities.yaml`** - Updated to v2.2:
   - Updated version from 2.0 to 2.2
   - Added `list_flows` and `pack_context` capabilities
   - Added programmatic invocation details
   - Added CRITICAL notes section with state.md and ttask done reminders
   - Added `user_finishing_work` flow trigger

5. **`.github/workflows/ci.yml`** - Fixed quoting issues:
   - Changed `== true` to `== 'true'` in all conditionals
   - Quoted `node-version`, `cache`, and `python-version` values

6. **`.github/workflows/project_tree.yml`** - Fixed output path:
   - Changed from `context/project_tree.md` to `.paircoder/context/project_tree.md`
   - Added `mkdir -p .paircoder/context` to ensure directory exists
   - Fixed egg-info prune pattern

7. **`CODEOWNERS`** - Improved with clear comments:
   - Added header explaining format and usage
   - Added `/.paircoder/**` and `/.claude/**` ownership rules
   - Added `/src/**`, `/tests/**`, `/docs/**` rules
   - Added `*.md` catch-all for markdown files

**New Files Created:**

- `docs/RELEASE_CHECKLIST.md` - Release checklist with template sync check section
- `tools/cli/tests/test_template.py` - 20 tests for template validation

**Test Results:** 20 new tests, all passing

**Files Modified:**
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/context/state.md`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/context/project.md`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/context/workflow.md`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/capabilities.yaml`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.github/workflows/ci.yml`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.github/workflows/project_tree.yml`
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CODEOWNERS`

---

### Session: 2025-12-19 (morning) - Backlog Remediation Planning

**Created:** `plan-2025-12-backlog-remediation`

Analyzed and prioritized backlog from React SDK deployment session (docs/PAIRCODER-BACKLOG.md).

**Plan created with 15 tasks across 3 sprints:**

**Sprint 18 - Critical Fixes (125 pts):**
- TASK-150: Cookie cutter template full audit and sync (P0, 60)
- TASK-151: Add missing config sections to all presets (P0, 30)
- TASK-152: Fix Task model missing depends_on field (P1, 20)
- TASK-153: Fix plan list showing 0 tasks (P1, 15)

**Sprint 19 - Documentation & Structure (120 pts):**
- TASK-154: Document BPS Trello board conventions (P1, 25)
- TASK-155: Add /commands directory to cookie cutter (P2, 15)
- TASK-156: Reorganize docs/ vs .paircoder/docs/ (P2, 40)
- TASK-157: Document Trello setup in quick start (P2, 20)
- TASK-158: Clarify task update vs ttask workflow (P2, 20)

**Sprint 20 - Enhancements (210 pts):**
- TASK-159: Trello board initialization from template (P2, 45)
- TASK-160: Sprint completion checklist enforcement (P2, 35)
- TASK-161: Config validate and update command (P3, 40)
- TASK-162: CLI commands for Trello custom fields (P2, 40)
- TASK-163: Preset-specific CI workflows (P3, 35)
- TASK-164: Document slash commands feature (P3, 15)

**Trello Sync:** 15 cards created in Intake/Backlog list

**Files created:**
- `.paircoder/plans/plan-2025-12-backlog-remediation.plan.yaml`
- `.paircoder/tasks/backlog-remediation/TASK-150.task.md` through TASK-164.task.md

---

### Session: 2025-12-18 (evening) - TASK-138: Token Estimation Feedback Loop

**TASK-138: Token Estimation Feedback Loop** - DONE

Implemented self-improving token estimation based on actual usage data:

**Enhanced:** `tools/cli/bpsai_pair/metrics/estimation.py`
- `TokenComparison` dataclass - compares estimated vs actual tokens with ratio
- `TokenFeedbackTracker` class - records usage, calculates stats, learns coefficients

**Feedback loop flow:**
1. Record estimated vs actual tokens on task completion
2. Calculate accuracy statistics by task type
3. Recommend coefficient adjustments based on data
4. Apply learning with conservative adjustment (10% rate, bounds 0.3x-3.0x)

**New CLI command:** `bpsai-pair metrics tokens`
- Shows token estimation accuracy report
- Displays actual/estimated ratio by task type
- Provides coefficient adjustment recommendations
- `--json` flag for programmatic access

**Example output:**
```
Token Estimation Accuracy Report
==================================

Tasks Analyzed: 15
Avg Ratio (actual/estimated): 1.18x
Bias: Underestimating by ~18%

By Task Type:
- Feature: 1.25x (underestimate) (6 tasks)
- Bugfix: 0.95x (5 tasks)
- Refactor: 1.45x (underestimate) (4 tasks)

Recommendations:
- Increase feature multiplier by ~25%
- Increase refactor multiplier by ~45%
```

**New hook:** `record_token_usage` in hooks.py
- Records TokenComparison to token-comparisons.jsonl
- Triggered on task completion with actual_tokens in context

**Learning algorithm:**
```
new_multiplier = old_multiplier * (1 + 0.1 * (avg_ratio - 1))
clamped to [0.3, 3.0]
```

**Updated files:**
- `metrics/estimation.py` - added TokenComparison, TokenFeedbackTracker
- `metrics/__init__.py` - exports new classes
- `cli.py` - added `metrics tokens` command
- `hooks.py` - added `record_token_usage` hook

**Tests:** 15 new tests (76 total in test_estimation.py)

---

### Session: 2025-12-18 (evening) - TASK-133: Token Estimation Model

**TASK-133: Token Estimation Model** - DONE

Implemented token estimation model that predicts token usage based on task characteristics:

**Enhanced:** `tools/cli/bpsai_pair/metrics/estimation.py`
- `TokenEstimate` dataclass - token usage breakdown (base, complexity, files, total)
- `TokenEstimationConfig` dataclass - configurable coefficients
- `TokenEstimator` class - estimates tokens from complexity, type, file count

**Formula:**
```
tokens = base_context +
         (complexity * per_complexity_point) * type_multiplier +
         (file_count * per_file_touched)
```

**Default coefficients:**
- base_context: 15,000 tokens (skills, state, project context)
- per_complexity_point: 500 tokens
- by_task_type: feature(1.2x), bugfix(0.8x), docs(0.6x), refactor(1.5x)
- per_file_touched: 2,000 tokens

**Task model integration:**
- `Task.estimated_tokens` property - returns TokenEstimate
- `Task.estimated_tokens_str` property - returns formatted string like "~45K tokens"

**CLI output:**
- `bpsai-pair task show <id>` now displays `Est. Tokens: ~42K tokens`

**Updated files:**
- `metrics/estimation.py` - added TokenEstimate, TokenEstimationConfig, TokenEstimator
- `metrics/__init__.py` - exports token estimation classes
- `planning/models.py` - added estimated_tokens properties to Task
- `planning/cli_commands.py` - task show displays token estimate
- `.paircoder/config.yaml` - added token_estimates configuration section

**Tests:** 19 new tests in `test_estimation.py`

---

### Session: 2025-12-18 (evening) - TASK-107: Estimation Accuracy Report

**TASK-107: Estimation Accuracy Report** - DONE

Implemented estimation accuracy reporting that analyzes historical estimates vs actuals:

**New file:** `tools/cli/bpsai_pair/metrics/accuracy.py`
- `AccuracyStats` dataclass - overall accuracy statistics (accuracy %, bias direction)
- `TaskTypeAccuracy` dataclass - accuracy breakdown by task type (feature, bugfix, refactor)
- `ComplexityBandAccuracy` dataclass - accuracy breakdown by complexity band (XS-XL)
- `AccuracyAnalyzer` class - analyzes historical task completion data

**Features:**
- `load_completions()` - loads task completion records from task-completions.jsonl
- `get_accuracy_stats()` - calculates overall accuracy and bias direction
- `get_accuracy_by_task_type()` - groups accuracy by feature/bugfix/refactor
- `get_accuracy_by_complexity_band()` - groups accuracy by XS/S/M/L/XL bands
- `get_recommendation()` - generates actionable recommendation based on bias
- `generate_report()` - full report with all breakdowns

**CLI command:**
- `bpsai-pair metrics accuracy` - show estimation accuracy report
- `--json` flag for JSON output

**Example output:**
```
Estimation Accuracy Report
==========================

Overall Accuracy: 82%
Bias: Optimistic by 18%

By Task Type:
- Feature: 75% accurate (25% underestimate)
- Bugfix: 90% accurate (10% overestimate)
- Refactor: 65% accurate (35% underestimate)

By Complexity:
- XS (0-15): 95% accurate
- S (16-30): 85% accurate
- M (31-50): 78% accurate
- L (51-75): 70% accurate
- XL (76-100): 60% accurate

Recommendation: Add 18% buffer to estimates to improve accuracy.
```

**Updated files:**
- `metrics/__init__.py` - exports AccuracyAnalyzer, AccuracyStats, TaskTypeAccuracy, ComplexityBandAccuracy
- `cli.py` - added `metrics accuracy` command

**Tests:** 16 tests in `test_accuracy.py`

---

### Session: 2025-12-18 (evening) - TASK-106: Sprint Burndown Chart Data

**TASK-106: Sprint Burndown Chart Data** - DONE

Implemented burndown chart data generation for sprint planning visualization:

**New file:** `tools/cli/bpsai_pair/metrics/burndown.py`
- `SprintConfig` dataclass - sprint configuration (id, dates, total points)
- `BurndownDataPoint` dataclass - single day's data (date, remaining, ideal, completed)
- `BurndownData` dataclass - complete burndown with config and data points
- `BurndownGenerator` class - generates burndown data from velocity completions

**Features:**
- `generate()` - generate burndown data for a sprint config
- `_calculate_ideal_remaining()` - linear ideal burndown calculation
- `_get_completions_for_date()` - get completions for a specific date
- `create_config_from_tasks()` - create config from task list
- `to_json()` - JSON output for visualization tools

**CLI command:**
- `bpsai-pair metrics burndown --sprint <id>` - generate burndown data
- Options: `--start`, `--end` (date range), `--json` (JSON output)
- Shows daily remaining vs ideal progress with status indicators

**Updated files:**
- `metrics/__init__.py` - exports BurndownGenerator, BurndownData, BurndownDataPoint, SprintConfig
- `cli.py` - added `metrics burndown` command

**Tests:** 20 tests in `test_burndown.py`

---

### Session: 2025-12-18 (evening) - TASK-105: Velocity Calculation

**TASK-105: Velocity Calculation** - DONE

Implemented velocity tracking for project planning:

**New file:** `tools/cli/bpsai_pair/metrics/velocity.py`
- `TaskCompletionRecord` dataclass - records task completion with complexity/sprint
- `VelocityStats` dataclass - comprehensive velocity statistics
- `VelocityTracker` class - tracks and calculates velocity metrics

**Features:**
- `record_completion()` - record task completion with complexity points
- `get_points_this_week()` - points completed in current week (Monday-based)
- `get_points_for_sprint()` - points completed in a specific sprint
- `get_weekly_velocity_average()` - rolling N-week average
- `get_sprint_velocity_average()` - average velocity per sprint
- `get_velocity_stats()` - comprehensive stats object
- `get_weekly_breakdown()` - week-by-week breakdown
- `get_sprint_breakdown()` - sprint-by-sprint breakdown

**CLI command:**
- `bpsai-pair metrics velocity` - show velocity metrics
- Options: `--weeks` (default 4), `--sprints` (default 3), `--json`

**Hook integration:**
- Added `record_velocity` hook to record completions automatically
- Configured in presets and config templates

**Updated files:**
- `metrics/__init__.py` - exports VelocityTracker, VelocityStats, TaskCompletionRecord
- `cli.py` - added `metrics velocity` command
- `hooks.py` - added `record_velocity` hook handler
- `presets.py` - added record_velocity to on_task_complete hooks
- `.paircoder/config.yaml` - added record_velocity hook
- Cookiecutter template config updated

**Tests:** 20 tests in `test_velocity.py`

---

### Session: 2025-12-18 (afternoon) - Trello Workflow Fixes

**Fixed Trello Workflow Issues:**

Investigated and fixed two workflow compliance issues:

1. **Cards not moved to "Planned/Ready" after sprint planning**
   - Root cause: `plan sync-trello` creates cards in "Intake/Backlog" by default
   - Fix: Added `--target-list` option to `plan sync-trello` command
   - Updated skill/flow documentation to be explicit about moving cards

2. **Acceptance Criteria not checked off on task completion**
   - Root cause: Two-step completion process (`ttask done` then `task update`) wasn't being followed
   - Fix: Made skill documentation more prominent with CRITICAL warnings

**Files Updated:**
- `tools/cli/bpsai_pair/planning/cli_commands.py` - added `--target-list` option
- `.claude/skills/paircoder-task-lifecycle/SKILL.md` - added prominent warnings
- `.claude/skills/trello-aware-planning/SKILL.md` - documented `--target-list` option
- `.paircoder/flows/trello-aware-planning.flow.md` - fixed list naming consistency

**New Command Usage:**
```bash
# Sync directly to Planned/Ready for sprint planning
bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"
```

---

### Session: 2025-12-18 (morning) - TASK-103 & TASK-104

**TASK-104: Actual vs Estimated Tracking** - DONE

Implemented task completion tracking and estimation accuracy:

**Enhanced:** `tools/cli/bpsai_pair/metrics/estimation.py`
- `TaskComparison` dataclass - variance calculations (hours, percent)
- `record_task_completion()` - log estimated vs actual hours
- `load_task_completions()` - retrieve completion history
- `get_estimation_accuracy()` - statistics across all completions

**Enhanced:** `tools/cli/bpsai_pair/metrics/collector.py`
- Added task completion storage in `task-completions.jsonl`

**Enhanced:** `tools/cli/bpsai_pair/planning/cli_commands.py`
- `task show` displays estimated vs actual hours with variance

**Enhanced:** `tools/cli/bpsai_pair/hooks.py`
- Records task completion on task_complete event

**Tests:** 258+ new tests in `test_estimation.py`

---

**TASK-103: Auto-Timer That Actually Works** - DONE

Enhanced timer persistence and automatic start/stop:

**Enhanced:** `tools/cli/bpsai_pair/integrations/time_tracking.py`
- Full active timer state persistence (task ID, timer ID, description, start time)
- Session restoration for active timers

**Enhanced:** `tools/cli/bpsai_pair/hooks.py`
- Timer auto-starts on `task update --status in_progress`
- Timer auto-stops on `task update --status done`
- Validates task ID consistency between start/stop

**CLI Output:**
- Shows formatted timer duration on stop
- Shows accumulated total time for task

**Tests:** 194 new tests in `test_hooks.py`, 101 new tests in `test_time_tracking.py`

---

### Session: 2025-12-18 (early morning) - Sprint 17 Setup & TASK-102

**Sprint 17 Plan Created and Synced to Trello:**
- Created `sprint-17-time-tokens-metrics.plan.yaml`
- Created 8 task files (TASK-102, 103, 104, 105, 106, 107, 133, 138)
- Synced all 8 cards to PairCoder Trello board

**TASK-102: Complexity to Hours Mapping** - DONE

Implemented complexity-to-hours estimation for better project planning:

**New file:** `tools/cli/bpsai_pair/metrics/estimation.py`
- `HoursEstimate` dataclass - min, expected, max hours with size band
- `EstimationConfig` - configurable complexity-to-hours mapping
- `EstimationService` - main service for estimating hours from complexity
- `estimate_hours()` convenience function

**Features:**
- Default mapping: XS (0-15), S (16-30), M (31-50), L (51-75), XL (76-100)
- Each band has (min, expected, max) hours: XS(0.5,1,2), S(1,2,4), M(2,4,8), L(4,8,16), XL(8,16,32)
- Configurable via `.paircoder/config.yaml` `estimation` section
- Added `estimated_hours` and `estimated_hours_str` properties to Task model

**Updated files:**
- `metrics/__init__.py` - exports new classes
- `.paircoder/config.yaml` - added `estimation.complexity_to_hours` config
- `planning/models.py` - added `estimated_hours` property to Task

**Tests:** 28 tests in `test_estimation.py`

---

### Session: 2025-12-17 - TASK-098: Reviewer Agent Implementation

**TASK-098: Reviewer Agent Implementation** - DONE

Created the ReviewerAgent for code review tasks:

**New file:** `tools/cli/bpsai_pair/orchestration/reviewer.py`
- `ReviewSeverity` enum - INFO, WARNING, BLOCKER severity levels
- `ReviewVerdict` enum - APPROVE, APPROVE_WITH_COMMENTS, REQUEST_CHANGES
- `ReviewItem` dataclass - individual review finding with file, line, message
- `ReviewOutput` dataclass - structured output with verdict, items, counts
- `ReviewOutput.from_raw_text()` - parses markdown output into structured data
- `ReviewerAgent` class - invokes reviewer via AgentInvoker framework
- `should_trigger_reviewer()` - trigger conditions for routing
- `extract_changed_files()` - extract files from git diff
- `extract_line_changes()` - extract line additions/deletions from diff
- `invoke_reviewer()` - convenience function for one-shot reviews

**Features:**
- Loads `.claude/agents/reviewer.md` via AgentInvoker
- Always operates in read-only `plan` permission mode
- Builds context from git diff + changed file contents
- Returns structured `ReviewOutput` with verdict and items by severity
- Auto-detects git diff and changed files

**Updated files:**
- `orchestration/__init__.py` - exports reviewer classes
- `orchestration/orchestrator.py` - added `_execute_with_reviewer()` method
- `mcp/tools/orchestration.py` - added `paircoder_orchestrate_review` MCP tool

**Tests:** 30 tests in `test_reviewer_agent.py`

---

### Session: 2025-12-17 - TASK-097: Planner Agent Implementation

**TASK-097: Planner Agent Implementation** - DONE

Created the PlannerAgent for design and planning tasks:

**New file:** `tools/cli/bpsai_pair/orchestration/planner.py`
- `PlanPhase` dataclass - represents a phase in the implementation plan
- `PlanOutput` dataclass - structured plan with summary, phases, files, complexity, risks
- `PlanOutput.from_raw_text()` - parses markdown output into structured data
- `PlannerAgent` class - invokes planner via AgentInvoker framework
- `should_trigger_planner()` - trigger conditions for routing
- `invoke_planner()` - convenience function for one-shot planning

**Features:**
- Loads `.claude/agents/planner.md` via AgentInvoker
- Always operates in read-only `plan` permission mode
- Builds context from task description + project context + relevant files
- Returns structured `PlanOutput` with phases, files, complexity
- Parses markdown output into structured plan data

**Updated files:**
- `orchestration/__init__.py` - exports planner classes
- `orchestration/orchestrator.py` - added `_execute_with_planner()` method
- `mcp/tools/orchestration.py` - added `paircoder_orchestrate_plan` MCP tool

**Tests:** 23 tests in `test_planner_agent.py`

---

### Session: 2025-12-17 - TASK-096: Agent Invocation Framework

**TASK-096: Agent Invocation Framework** - DONE

Created the agent invocation framework for Sprint 16:

**New file:** `tools/cli/bpsai_pair/orchestration/invoker.py`
- `AgentDefinition` dataclass - parses YAML frontmatter from .claude/agents/*.md
- `InvocationResult` dataclass - structured result with output, tokens, cost
- `AgentInvoker` class - loads agent definitions and invokes via HeadlessSession
- `invoke_agent()` convenience function for one-shot invocations

**Features:**
- Loads agent definitions from `.claude/agents/{name}.md`
- Parses YAML frontmatter (name, description, model, permissionMode, tools)
- Extracts system prompt from markdown body
- Invokes agents via `HeadlessSession` with correct permission mode
- Caches loaded agents for performance
- Supports handoff context between agents

**Updated:** `tools/cli/bpsai_pair/orchestration/__init__.py`
- Exports `AgentDefinition`, `AgentInvoker`, `InvocationResult`, `invoke_agent`

**Tests:** 24 tests in `test_invoker.py`

---

### Session: 2025-12-17 - Sprint 16 Plan Creation

Created Sprint 16: Real Sub-agents plan and synced to Trello:
- Created plan file: `sprint-16-real-subagents.plan.yaml`
- Created task files: TASK-096 to TASK-101
- Created sprint-16 list on Trello board
- Synced 6 cards to Trello

---

### Session: 2025-12-17 - TASK-095: Dependency Vulnerability Scan

**TASK-095: Dependency Vulnerability Scan** - DONE

Implemented dependency vulnerability scanning:

**New file:** `tools/cli/bpsai_pair/security/dependencies.py`
- `DependencyScanner` class for scanning Python and npm dependencies
- `Vulnerability` dataclass for detected CVEs
- `ScanReport` dataclass with severity analysis
- `Severity` enum with comparison operators

**Features:**
- Python scanning via pip-audit (requirements.txt, pyproject.toml)
- npm scanning via npm audit (package.json)
- Result caching for performance (configurable TTL)
- Severity filtering (--fail-on option)
- Verbose and JSON output formats

**CLI commands:**
- `bpsai-pair scan-deps [path]` - Scan dependencies
- `bpsai-pair scan-deps --fail-on high` - Fail on high+ severity
- `bpsai-pair scan-deps --verbose` - Show detailed CVE info
- `bpsai-pair scan-deps --json` - JSON output for CI

**Tests:** 37 tests in `test_security_dependencies.py`

**Sprint 15 Complete!** All 7 security tasks done (250/250 points).

---

### Session: 2025-12-17 - TASK-094: Secret Detection

**TASK-094: Secret Detection** - DONE

Implemented pre-commit secret scanning:

**New file:** `tools/cli/bpsai_pair/security/secrets.py`
- `SecretScanner` class with comprehensive pattern matching
- `SecretMatch` dataclass for detected secrets with redaction
- `SecretType` enum for categorizing secrets
- `AllowlistConfig` for false positive suppression

**Secret patterns supported:**
- AWS credentials (access keys, secret keys)
- GitHub tokens (PAT, OAuth, fine-grained)
- Slack tokens and webhooks
- Private keys (RSA, SSH, EC, DSA, PGP)
- JWT tokens
- Database connection strings
- Stripe keys (live and test)
- SendGrid keys
- Google API keys
- Generic patterns (api_key, password, secret, token)

**Scanning modes:**
- `scan_file()` - Scan individual files
- `scan_diff()` - Scan git diff output
- `scan_staged()` - Scan staged git changes
- `scan_commit_range()` - Scan commits since reference
- `scan_directory()` - Recursive directory scanning

**CLI commands:**
- `bpsai-pair scan-secrets [path]` - Scan files/directories
- `bpsai-pair scan-secrets --staged` - Scan staged changes
- `bpsai-pair scan-secrets --diff HEAD~1` - Scan since commit
- `bpsai-pair security pre-commit` - Pre-commit hook mode
- `bpsai-pair security install-hook` - Install git hook

**Configuration:**
- `.paircoder/security/secret-allowlist.yaml` - Allowlist config
- Supports pattern-based allowlisting
- File path exclusions
- Ignore patterns for false positives

**Tests:** 52 tests in `test_security_secrets.py`

---

### Session: 2025-12-17 - Documentation Audit & Changelog Update

**Documentation Audit Complete:**
- Audited README.md, CONTRIBUTING.md, USER_GUIDE.md, FEATURE_MATRIX.md, docs/SECURITY.md
- Fixed outdated reference to `scripts/ci_local.sh` → `bpsai-pair ci` in CONTRIBUTING.md
- Updated test counts from 412 to 541+ across all documentation
- Added Sprint 14 and Sprint 15 features to FEATURE_MATRIX.md
- Updated docs/SECURITY.md to mark completed Sprint 15 tasks
- Updated ROADMAP-SPRINTS-14-20.md with current status

**CHANGELOG.md Updated:**
- v2.5.1: Sprint 14 (Trello Deep Integration) - 8 tasks
- v2.5.2: Sprint 15 (Security & Sandboxing) - 5 tasks done
- v2.5.3: Unreleased (remaining Sprint 15 tasks)

---

### Session: 2025-12-17 - Sprint 15 Progress (5 tasks complete)

**TASK-093: Git Checkpoint/Rollback** - DONE

Implemented automatic git checkpointing and rollback:

**New file:** `tools/cli/bpsai_pair/security/checkpoint.py`
- `GitCheckpoint` class with full checkpoint management
- `create_checkpoint(message)` - Creates tagged checkpoint at HEAD
- `rollback_to(checkpoint)` - Rolls back with optional stash
- `rollback_to_last()` - Rolls back to most recent checkpoint
- `list_checkpoints()` - Lists all checkpoints with metadata
- `preview_rollback()` - Shows what would be reverted
- `cleanup_old_checkpoints()` - Retention policy enforcement
- `is_dirty()` - Check for uncommitted changes

**Error handling:**
- `CheckpointError`, `NotAGitRepoError`, `CheckpointNotFoundError`, `NoCheckpointsError`

**CLI formatting:**
- `format_checkpoint_list()` - For `bpsai-pair rollback` display
- `format_rollback_preview()` - For `--preview` mode

**Tests:** 20 tests in `test_security_checkpoint.py`

---

**TASK-092: Docker Sandbox Runner** - DONE

Execute commands in isolated Docker containers:

**New file:** `tools/cli/bpsai_pair/security/sandbox.py`
- `SandboxConfig` - Configuration (image, memory, CPU, network)
- `SandboxRunner` - Execute commands in containers
- `SandboxResult` - Results with file change tracking
- `FileChange` - Track created/modified/deleted files
- `MountConfig` - Volume mount configuration

**Features:**
- Network isolation (default: none)
- Resource limits (memory, CPU)
- Environment variable passthrough
- Automatic container cleanup
- File change detection via `container.diff()`

**New file:** `tools/cli/bpsai_pair/security/Dockerfile`
- Python 3.12-slim base with dev tools
- Non-root `sandbox` user for security

**New file:** `.paircoder/security/sandbox.yaml`
- Configuration template with all options

**Tests:** 35 tests in `test_security_sandbox.py`

---

**TASK-091: Pre-execution Security Review** - DONE

Security review before command execution:

**New file:** `tools/cli/bpsai_pair/security/review.py`
- `ReviewResult` - Result dataclass with allow/block/warn
- `SecurityReviewHook` - Pre-execution command review
- `CodeChangeReviewer` - Scan code for vulnerabilities

**Secret detection patterns:**
- API keys, passwords, AWS credentials
- Private keys, GitHub/Slack tokens, JWTs
- Database connection strings

**Injection vulnerability patterns:**
- SQL injection (f-strings in queries)
- Command injection (os.system, subprocess shell=True)
- Path traversal

**New file:** `.claude/hooks/security-review.md`
- Documentation for hook integration

**Tests:** 35 tests in `test_security_review.py`

---

**TASK-090: Command Allowlist System** - DONE

Safe vs unsafe command classification:

**New file:** `tools/cli/bpsai_pair/security/allowlist.py`
- `AllowlistManager` - Command classification
- `CommandDecision` - ALLOW, REVIEW, BLOCK
- `CheckResult` - Full result with reason and matched rule

**Default classifications:**
- Always allowed: git status, pytest, ls, cat, bpsai-pair
- Require review: git push, pip install, docker
- Always blocked: rm -rf /, curl | bash, sudo rm

**Pattern matching:**
- Regex patterns for complex commands
- Wildcard support in allowlist
- Configurable via `.paircoder/security/allowlist.yaml`

**Tests:** 39 tests in `test_security_allowlist.py`

---

**TASK-089: Security Agent Definition** - DONE

Created `.claude/agents/security.md`:
- Pre-execution security gatekeeper role
- Block vs warn conditions defined
- Security checklist for code/commands/git
- SOC2 control references (CC6.1, CC6.6, CC7.1, etc.)
- Output formats for BLOCKED/WARNING/ALLOWED

Also created:
- `.claude/hooks/security-review.md` - Hook integration docs
- `docs/SECURITY.md` - Security features documentation

## What's Next

**Sprint 18 - COMPLETE ✅**

All 4 critical fixes completed (125/125 points):
- [x] TASK-150: Cookie cutter template full audit and sync
- [x] TASK-151: Add missing config sections to all presets
- [x] TASK-152: Fix Task model missing depends_on field
- [x] TASK-153: Fix plan list showing 0 tasks

**Sprint 19 - Documentation & Structure (Next Up):**
1. TASK-154: Document BPS Trello board conventions (P1, 25 pts)
2. TASK-155: Add /commands directory to cookie cutter (P2, 15 pts)
3. TASK-156: Reorganize docs/ vs .paircoder/docs/ (P2, 40 pts)
4. TASK-157: Document Trello setup in quick start (P2, 20 pts)
5. TASK-158: Clarify task update vs ttask workflow (P2, 20 pts)

**Sprint 17 (Previous) - COMPLETE:**
- [x] Complexity → hours mapping working
- [x] Auto-timer starts/stops with task status
- [x] Actual vs estimated tracking recorded
- [x] Velocity calculation available
- [x] Burndown chart data generated
- [x] Estimation accuracy report available
- [x] Token estimation model implemented
- [x] Token feedback loop working

## Sprint 16 Success Criteria

- [x] Agent invocation framework created
- [x] Planner agent routes design/planning tasks
- [x] Reviewer agent routes code review tasks
- [x] Security agent routes security-related tasks
- [x] Agent handoff passes context between agents
- [x] Agent selection uses scoring algorithm
- [x] CLI `orchestrate select-agent` command available

## Test Coverage

- **Total tests**: 1300
- **Orchestration module tests**:
  - test_invoker.py: 48 tests
  - test_planner_agent.py: 26 tests
  - test_reviewer_agent.py: 26 tests
  - test_security_agent.py: 37 tests
  - test_handoff_protocol.py: 22 tests
  - test_agent_selection.py: 27 tests
- **Security module tests**:
  - test_security_allowlist.py: 39 tests
  - test_security_review.py: 35 tests
  - test_security_sandbox.py: 35 tests
  - test_security_checkpoint.py: 20 tests
  - test_security_secrets.py: 52 tests
  - test_security_dependencies.py: 37 tests
- **Test command**: `pytest -v`

## Blockers

None currently.
