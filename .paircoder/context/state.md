# Current State

> Last updated: 2025-12-30

## Active Plan

**Plan:** plan-2025-12-sprint-27-stabilization
**Sprint:** 27 - Stabilization
**Status:** Planned
**Goal:** CI green, upgrade command works, no blocking bugs
**Version Target:** v2.8.4

## Current Sprint Tasks (Sprint 27)

| ID | Title | Status | Priority | Complexity | Effort |
|----|-------|--------|----------|------------|--------|
| T27.1 | Fix template check crash | ✓ done | P0 | 30 | S |
| T27.2 | Fix smoke test failure | ✓ done | P0 | 30 | S |
| T27.3 | Fix Unicode errors in Trello | ✓ done | P0 | 30 | S |
| T27.4 | Fix upgrade source file resolution | ✓ done | P0 | 55 | M |
| T27.5 | Fix upgrade to actually copy files | ✓ done | P0 | 45 | M |
| T27.6 | Fix Windows hook compatibility | ✓ done | P0 | 30 | S |
| T27.7 | Remove /status slash command conflict | ✓ done | P0 | 15 | S |
| T27.8 | Sync cookiecutter: config files | ✓ done | P0 | 30 | S |
| T27.9 | Sync cookiecutter: skills | ✓ done | P0 | 30 | S |
| T27.10 | Sync cookiecutter: commands | ✓ done | P0 | 15 | S |
| T27.11 | Sync cookiecutter: agents | ✓ done | P0 | 15 | S |

**Progress:** 11/11 tasks (325/325 complexity points) ✓ SPRINT COMPLETE!

## Previous Sprint (25.6 - Emergent Skill Discovery) ✓ COMPLETE

| ID     | Title | Status | Priority | Complexity | Effort |
|--------|-------|--------|----------|------------|--------|
| T25.17 | /update-skills Slash Command | done | P1 | 35 | M |
| T25.18 | Skill Gap Detection | done | P1 | 50 | L |
| T25.19 | Auto-Skill Creation | done | P1 | 55 | L |
| T25.20 | Skill Quality Scoring | done | P2 | 45 | M |
| T25.21 | Skill Marketplace Foundation | dropped | P2 | 45 | M |
| T25.22 | Flows → Skills Migration RFC | done | P1 | 35 | M |
| T25.23 | Subagent Gap Detection | done | P1 | 45 | M |
| T25.24 | Unified Gap Classifier | done | P1 | 40 | M |
| T25.25 | Flow Commands Deprecation Warnings | done | P2 | 25 | S |
| T25.26 | Codex/ChatGPT Skill Export Formats | done | P2 | 30 | M |

**Result:** 9/9 tasks (360/360 complexity points) ✓ Sprint Complete!

## Task Dependencies & Implementation Sequence

```
COMPLETED:
  T25.17 (/update-skills) ✓
  T25.18 (Skill Gap Detection) ✓
  T25.19 (Auto-Skill Creation) ✓
  T25.20 (Skill Quality Scoring) ✓
  T25.22 (Flows → Skills Migration RFC) ✓
  T25.23 (Subagent Gap Detection) ✓
  T25.24 (Unified Gap Classifier) ✓

ALL TASKS COMPLETE:
  1. T25.25 (Deprecation) ✓
  2. T25.26 (Codex/ChatGPT) ✓

DROPPED:
  T25.21 ─────────────────► Skill marketplace foundation (focusing on personalized skill gen)
```

### Priority Breakdown

**P1 (High) - Core Architecture: ALL COMPLETE ✓**
- ✓ T25.22: RFC documents breaking changes and timeline
- ✓ T25.23: Subagent gap detection extends existing gap system
- ✓ T25.24: Unified classifier determines skill vs subagent

**P2 (Medium) - Enhancements:**
- ✓ T25.20: Skill quality scoring with pre-generation gates
- ~~T25.21: Skill marketplace foundation~~ (dropped)
- T25.25: Deprecation warnings (low risk, after RFC)
- T25.26: Codex/ChatGPT export (independent work)

## Context: Industry Skills Adoption

OpenAI has adopted Agent Skills in Codex CLI and ChatGPT. The `agentskills.io` open standard is now supported by: Claude Code, OpenAI Codex, Cursor, VS Code, GitHub, Amp, Goose, and Letta.

**Key distinction (T25.23/T25.24):**
- **Skills**: Portable instructions, model-invoked, cross-platform
- **Subagents**: Context-isolated personas, Claude Code specific, resumable

## Previous Sprint Summary (Sprint 25.5)

**Sprint 25.5 COMPLETE:** Cross-Platform Skills
- T25.12: Skill naming conventions (gerund form)
- T25.13: Third-person voice descriptions
- T25.14: Creating-skills meta-skill
- T25.15: Skill install command
- T25.16: Skill export command (Cursor, Continue, Windsurf)

## Previous Sprint Summary (Sprint 25)

**Sprint 25 COMPLETE:** EPIC-003 + Token Budget System
- EPIC-003 CLI Architecture Refactor complete (Phases 1-5)
- Token Budget System with tiktoken integration
- 112 CLI commands, 1774 tests
- v2.8.0 ready for release

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
| 23 | CLI Refactor Phase 2 | v2.7.0 | Complete |
| 24 | CLI Refactor Phase 3 | v2.7.0 | Complete |
| 25 | EPIC-003 Complete + Token Budget | v2.8.0 | Complete |
| 25.5 | Cross-Platform Skills | v2.9 | Complete |
| 25.6 | Emergent Skill Discovery + Flows Deprecation | v2.9.2 | Complete |
| 27 | Stabilization | v2.8.4 | In Progress |
| 26 | UX Overhaul (EPIC-004) | v2.10.0 | Planned |

## What's Next

**Sprint 27: Stabilization** (11 tasks, 325 pts) - IN PROGRESS

Phase 1 - Bug Fixes (Isolated, Low Risk):
- T27.1: Fix template check crash
- T27.2: Fix smoke test failure
- T27.3: Fix Unicode errors in Trello

Phase 2 - Upgrade Command:
- T27.4: Fix upgrade source file resolution
- T27.5: Fix upgrade to actually copy files

Phase 3 - Compatibility:
- T27.6: Fix Windows hook compatibility
- T27.7: Remove /status slash command conflict

Phase 4 - Template Sync:
- T27.8: Sync cookiecutter: config files
- T27.9: Sync cookiecutter: skills
- T27.10: Sync cookiecutter: commands
- T27.11: Sync cookiecutter: agents

**Sprint 26: UX Overhaul (EPIC-004)** (10 tasks, 230 pts)
Make PairCoder usable by non-technical "vibe-coders". Tasks: T26.1-T26.10 - Interactive welcome wizard, Trello setup wizard with pre-checks, post-setup guidance, Claude prompts, /get-started slash command, board creation from template, contextual doc links, documentation updates, user retest session.

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

### 2025-12-30 - T27.11 Complete (Sync cookiecutter: agents) - SPRINT 27 COMPLETE!

- **T27.11: Sync cookiecutter: agents** ✓
  - Compared all 4 agents between main project and template:
    - planner.md ✓
    - reviewer.md ✓
    - security-auditor.md ✓
    - security.md ✓
  - All files already identical (no changes needed)
  - Verified agent content is generic:
    - References to `.paircoder/` paths are framework references (expected)
    - References to `bpsai-pair` are CLI command patterns (expected)
    - No PairCoder project-specific content
  - All 2049 tests pass

**🎉 Sprint 27 Complete!**
- 11/11 tasks done (325/325 complexity points)
- All stabilization goals achieved:
  - CI green ✓
  - Upgrade command works ✓
  - No blocking bugs ✓
  - Cookiecutter template fully synced ✓

### 2025-12-30 - T27.10 Complete (Sync cookiecutter: commands)

- **T27.10: Sync cookiecutter: commands** ✓
  - Compared all commands between main project and template
  - Added missing `prep-release.md` command to template (generalized version)
  - Updated `start-task.md` wording to match main project ("NEVER" vs "DO NOT")
  - Verified no `/status` command in template (removed in T27.7)
  - Template now has all 4 commands: pc-plan, prep-release, start-task, update-skills
  - Scrubbed `prep-release.md` of PairCoder-specific content:
    - Removed `tools/cli/` paths and `bpsai_pair` references
    - Removed cookiecutter template sync phase (PairCoder-only)
    - Made version detection generic (checks common locations)
    - Removed FEATURE_MATRIX references
    - Made build/publish commands generic (Python/Node.js examples)
  - Updated `test_template.py`:
    - Removed deprecated `TestFlowFiles` class (flows are deprecated in v2.8+)
    - Removed `flows` directory check from `test_paircoder_structure`
    - Updated version check to allow v2.8.x patch versions
  - All 2049 tests pass

### 2025-12-30 - T27.9 Complete (Sync cookiecutter: skills)

- **T27.9: Sync cookiecutter: skills** ✓
  - Compared all 7 shared skills between main project and template
  - Skills already matched: creating-skills, designing-and-implementing, finishing-branches, implementing-with-tdd, managing-task-lifecycle, reviewing-code
  - Updated `planning-with-trello/SKILL.md`:
    - Removed obsolete "Project Conventions" section that referenced non-existent `reference.md`
    - Template now matches main project version
  - Verified `testing-fixes` skill correctly NOT in template:
    - This is an auto-generated, project-specific skill
    - Template should only include generic, reusable skills
  - All 7 template skills now match v2.8 versions exactly
  - All 2050 tests pass

### 2025-12-30 - T27.8 Complete (Sync cookiecutter: config files)

- **T27.8: Sync cookiecutter: config files** ✓
  - Updated `capabilities.yaml` template from v2.2 to v2.8:
    - Removed `flows` directory reference (deprecated)
    - Changed `flow_triggers` to `Skill_triggers`
    - Changed `suggested_flow` to `suggested_skill`
    - Updated skill names to use gerund format
  - Updated `config.yaml` template to v2.8:
    - Changed `flows:` section to `skills:` section
    - Removed `flows_dir` and added `skills_dir: .claude/skills`
    - Added full model providers config (anthropic, openai, google)
    - Added complete Trello custom fields configuration
    - Added `on_task_ready` and `on_task_review` hooks
    - Added `record_task_completion` hook
  - Updated tests to match new v2.8 format:
    - `test_capabilities_has_required_sections` - checks for `Skill_triggers`
    - `test_config_has_all_sections` - checks for `skills:` instead of `flows:`
  - All 2050 tests pass

### 2025-12-30 - T27.7 Complete (Remove /status slash command conflict)

- **T27.7: Remove /status slash command conflict** ✓
  - Issue: PairCoder's `/status` command conflicted with Claude Code's built-in `/status`
  - No `status.md` file existed in `.claude/commands/` (already removed or never created)
  - Updated 7 documentation files to remove `/status` references:
    - `CLAUDE.md` - Updated slash commands table
    - `tools/cli/.../CLAUDE.md` (cookiecutter) - Updated slash commands table
    - `docs/CLAUDE_CODE_INTEGRATION.md` - Updated command tables
    - `.paircoder/docs/USER_GUIDE.md` - Updated slash commands section and examples
    - `tools/cli/.../USER_GUIDE.md` (cookiecutter) - Updated slash commands
    - `tools/cli/.../FEATURE_MATRIX.md` (cookiecutter) - Updated commands list
    - `CHANGELOG.md` - Updated v2.6.0 entry
  - Users should now use `bpsai-pair status` CLI command for project status
  - All 2050 tests pass

### 2025-12-30 - T27.6 Complete (Fix Windows hook compatibility)

- **T27.6: Fix Windows hook compatibility** ✓
  - Issue: Claude Code hooks on Windows fail with bash-specific syntax like `|| true`
  - Solution: Use `--quiet` flag for cross-platform error suppression
  - Changes made:
    - Fixed `session.py` exception handling to catch `ProjectRootNotFoundError`
    - Both `session check` and `compaction snapshot save` now properly exit 0 with `--quiet`
  - All hook commands now have `--quiet`/`-q` flag:
    - `bpsai-pair session check --quiet`
    - `bpsai-pair compaction snapshot save --quiet`
    - `bpsai-pair context-sync --auto` (or `--quiet`)
    - `bpsai-pair history-log --quiet`
  - Created 15 new cross-platform tests in `test_session.py`:
    - `TestQuietModeForHooks`: --quiet mode behavior
    - `TestContextSyncAutoMode`: --auto mode behavior
    - `TestHistoryLogQuietMode`: history-log --quiet
    - `TestCrossPlatformHookCompatibility`: integration tests
  - All 2050 tests pass

### 2025-12-30 - T27.5 Complete (Fix upgrade to actually copy files)

- **T27.5: Fix upgrade to actually copy files** ✓
  - Issue: upgrade command didn't handle commands (only skills, agents, docs)
  - Changes made to `upgrade.py`:
    - Added `commands_to_add` and `commands_to_update` to `UpgradePlan` dataclass
    - Added `get_bundled_commands()` function to discover bundled commands
    - Updated `plan_upgrade()` to check for missing/outdated commands
    - Updated `execute_upgrade()` to copy commands to project
    - Added `--commands` flag to CLI for selective upgrades
    - Updated summary display to show commands added/updated
  - Created 6 new tests in `test_upgrade.py`:
    - `TestGetBundledCommands`: command discovery from template
    - `TestPlanUpgrade`: command detection in upgrade plans
    - `TestExecuteUpgrade`: command copying verification
  - All 2035 tests pass

### 2025-12-30 - T27.4 Complete (Fix upgrade source file resolution)

- **T27.4: Fix upgrade source file resolution** ✓
  - Root cause: `get_template_dir()` incorrectly used `importlib.resources`
    - Used `with resources.files() as data_dir` (not needed, returns Traversable)
    - Used `Path(data_dir)` which doesn't work for `MultiplexedPath` objects
  - Fix: Use `data_dir.joinpath(*path_parts)` which returns a proper Path
  - Added `bpsai_pair/data/__init__.py` so `importlib.resources.files()` can access the data package
  - Created 13 new tests in `test_upgrade.py`:
    - `TestGetTemplateDir`: template resolution in dev/installed modes
    - `TestGetBundledSkills`: skill discovery from template
    - `TestGetBundledAgents`: agent discovery from template
    - `TestPlanUpgrade`: upgrade plan generation
    - `TestImportlibResourcesIntegration`: package data access
  - All 2029 tests pass

### 2025-12-30 - T27.3 Complete (Fix Unicode errors in Trello)

- **T27.3: Fix Unicode errors in Trello** ✓
  - Added `encoding="utf-8"` to all file operations in Trello module:
    - `auth.py`: token file read/write
    - `task_commands.py`: config read, bypass log write
    - `commands.py`: config read/write
    - `fields.py`: cache file read/write
    - `webhook_commands.py`: config read
    - `mcp/tools/trello.py`: task file read/write
  - Added `ensure_ascii=False` to JSON dumps for proper Unicode output
  - Added `allow_unicode=True` to YAML dumps
  - Added 2 new Unicode tests in `TestTrelloAuthUnicode`:
    - `test_store_and_load_unicode_token`: Tests emojis, Japanese, accented chars
    - `test_load_unicode_token_file`: Tests reading pre-existing Unicode files
  - All 312 Trello tests pass, full suite (2014 tests) passes

### 2025-12-30 - T27.2 Complete (Fix smoke test failure)

- **T27.2: Fix smoke test failure** ✓
  - Root cause: `test_template.py` expected `project_tree.yml` workflow in cookiecutter template
  - `project_tree.yml` is v1 legacy workflow that was never migrated to v2
  - Removed assertion for `project_tree.yml` from `test_github_workflows_exist`
  - Removed entire `test_project_tree_yml_correct_path` test (tests non-existent file)
  - All 19 template tests pass
  - Full test suite passes (2014 tests)

### 2025-12-30 - T27.1 Complete (Fix template check crash)

- **T27.1: Fix template check crash** ✓
  - Root cause: `find_paircoder_dir()` raises `ProjectRootNotFoundError` when not in a project, but `template_check` and `template_list` didn't catch it
  - Fix: Added try/except for `ProjectRootNotFoundError` in both functions
  - Shows helpful error: "❌ Not in a PairCoder project" with init instructions
  - Exit code 1 on error (graceful failure instead of traceback)
  - Added 3 new tests in `TestTemplateCheckNotInProject` class
  - All 16 template tests pass

### 2025-12-30 - Sprint 27 Plan Created

- **Sprint 27: Stabilization** plan created
  - Plan ID: `plan-2025-12-sprint-27-stabilization`
  - Type: chore
  - Goal: CI green, upgrade command works, no blocking bugs
  - Version target: v2.8.4
  - 11 tasks, 325 complexity points
  - All tasks P0 priority (stabilization focus)
  - Synced to Trello: 11 cards created in "Planned/Ready" list

### 2025-12-23 - T25.26 Complete (Codex/ChatGPT Skill Export Formats)

- **T25.26: Codex/ChatGPT Skill Export Formats** ✓
  - Extended `ExportFormat` enum with CODEX, CHATGPT, and ALL options
  - Implemented `_format_for_codex()` - preserves content (same Agent Skills spec)
  - Implemented `_format_for_chatgpt()` - strips frontmatter, title-case heading, export footer
  - Implemented `export_to_all_formats()` - exports to all platforms at once
  - Updated `check_portability()` with format-specific warnings (MCP tools for Codex)
  - Updated CLI help text with new formats in examples
  - 11 new tests for Codex/ChatGPT/ALL formats (33 total exporter tests pass)
  - Updated CHANGELOG.md

### 2025-12-23 - T25.25 Complete (Flow Commands Deprecation Warnings)

- **T25.25: Flow Commands Deprecation Warnings** ✓
  - Created `bpsai_pair/core/deprecation.py` - Deprecation utilities:
    - `deprecated_command` decorator for marking CLI commands as deprecated
    - `suppress_deprecation_warnings()` for CI/CD pipelines
    - `show_migration_hint_once()` with daily rate limiting
    - `warn_deprecated_config()` for config option deprecation
  - Updated `bpsai_pair/commands/flow.py`:
    - Added deprecation decorator to all 4 flow commands (list, show, run, validate)
    - Added `--no-deprecation-warnings` flag to suppress warnings
    - Added migration hint that shows once per day
    - Updated all docstrings with [DEPRECATED] suffix
    - Updated app help text to indicate deprecation
  - 20 new tests in `tests/test_flow_deprecation.py`:
    - All deprecation warning tests pass
    - All existing flow CLI tests still pass
  - Updated CHANGELOG.md with deprecation documentation

### 2025-12-23 - T25.20 Complete (Skill Quality Scoring with Pre-Generation Gates)

- **T25.20: Skill Quality Scoring** ✓
  - Created `bpsai_pair/skills/gates.py` - Pre-generation quality gates:
    - `GateStatus` enum: PASS, WARN, BLOCK
    - `GateResult` and `QualityGateResult` dataclasses
    - `GapQualityGate` class with 4 gates:
      - Redundancy: Checks overlap with existing skills
      - Novelty: Blocks generic commands (pytest, git add, etc.)
      - Complexity: Requires 3+ distinct commands
      - Time Value: Estimates time savings value
    - `GENERIC_COMMANDS` blocklist (30+ commands)
    - `evaluate_gap_quality()` and `format_gate_result()` functions
  - Created `bpsai_pair/skills/scorer.py` - Post-creation quality scoring:
    - `DimensionScore` and `SkillScore` dataclasses
    - `SkillScorer` class with 5 dimensions:
      - Token efficiency (25%): Lines/info density
      - Trigger clarity (20%): "When to use" clarity
      - Completeness (20%): Workflow coverage
      - Usage frequency (20%): Historical invocation counts
      - Portability (15%): Cross-platform compatibility
    - Letter grades (A-F) based on 0-100 scores
    - `score_skills()`, `format_skill_score()`, `format_score_table()`
  - Added CLI commands:
    - `bpsai-pair gaps check <gap-id>` - Check gap against quality gates
    - `bpsai-pair skill score [name]` - Score skill quality
  - Integrated gates into `gaps detect`:
    - `--with-gates/--no-gates` option (default: with gates)
    - Shows gate status (✓ PASS, ✗ BLOCKED, ⚠ WARNING) for each gap
    - Blocking reasons displayed for failed gates
    - Gate summary in output
  - 30 new tests for gates, 34 new tests for scorer
  - All 223 skill-related tests pass

**This completes the "testing-fixes" problem!** Patterns like running pytest repeatedly will now be blocked by the novelty gate because they contain only generic commands.

### 2025-12-23 - P1 Tasks Complete (T25.22, T25.23, T25.24)

- **T25.22: Flows → Skills Migration RFC** ✓
  - Created `docs/rfcs/RFC-005-flows-to-skills.md`:
    - Current state analysis of flows infrastructure
    - Migration mapping table (flows → skills concepts)
    - Breaking changes enumeration with mitigation strategies
    - Deprecation timeline: v2.10.x warnings → v2.11.x removal
    - Conversion utility specification (`bpsai-pair migrate`)
  - Created `docs/MIGRATION.md` with flows→skills migration guide
  - RFC ready for review

- **T25.23: Subagent Gap Detection** ✓
  - Created `bpsai_pair/skills/subagent_detector.py`:
    - `SubagentGap` dataclass with serialization support
    - `SubagentGapDetector` class detects:
      - Persona patterns ("act as", "you are a")
      - Context isolation patterns ("separately", "in parallel")
      - Resumability patterns ("continue", "resume")
      - Tool restriction patterns (read-only operations)
    - `SubagentGapPersistence` for history storage
    - Confidence scoring based on indicators
  - Added `bpsai-pair subagent gaps` command:
    - `--analyze` for fresh detection
    - `--json` for JSON output
    - `--clear` to clear history
  - Persists to `.paircoder/history/subagent-gaps.jsonl`
  - 17 new tests, all passing

- **T25.24: Unified Gap Classifier** ✓
  - Created `bpsai_pair/skills/classifier.py`:
    - `GapType` enum: SKILL, SUBAGENT, AMBIGUOUS
    - `ClassifiedGap` dataclass with scores and recommendations
    - `GapClassifier` implements decision tree:
      - Portability/simplicity → SKILL
      - Isolation/persona/resumability → SUBAGENT
      - Close scores → AMBIGUOUS
    - Human-readable reasoning generation
  - Added `bpsai-pair gaps` command group:
    - `gaps detect` - unified detection and classification
    - `gaps list [--type skill|subagent|ambiguous]` - filtered listing
    - `gaps show <id>` - detailed view with score bars
  - Deduplication of overlapping skill/subagent gaps
  - 19 new tests, all passing

**All P1 tasks for Sprint 25.6 are now complete!**
- Progress: 6/10 tasks (260/405 complexity points)
- Remaining: P2 tasks only

### 2025-12-23 - Sprint 25.6 Extended with Skills/Subagent Strategy

- **Sprint 25.6 Scope Extended**
  - Added 5 new tasks (T25.22-T25.26) for flows deprecation and subagent discovery
  - Total complexity increased from 230 to 405 points
  - Sprint now addresses industry convergence on Agent Skills standard
  - Research: OpenAI adopted skills in Codex CLI and ChatGPT
  - Research: agentskills.io now supported by 10+ AI coding tools
  
- **New Tasks Added:**
  - T25.22: Flows → Skills Migration RFC (P1, 35 pts)
  - T25.23: Subagent Gap Detection (P1, 45 pts)
  - T25.24: Unified Gap Classifier (P1, 40 pts)
  - T25.25: Flow Commands Deprecation Warnings (P2, 25 pts)
  - T25.26: Codex/ChatGPT Skill Export Formats (P2, 30 pts)

- **Key Architecture Decision:**
  - Skills = portable, cross-platform, model-invoked workflows
  - Subagents = context-isolated personas, Claude Code specific
  - Gap detector will classify patterns into appropriate category

### 2025-12-23 - T25.19 Complete (Auto-Skill Creation)

- **T25.19: Auto-Skill Creation** ✓
  - Created `bpsai_pair/skills/generator.py` module with:
    - `GeneratedSkill` dataclass for skill drafts
    - `SkillGenerator` class for generating from gaps
    - `save_generated_skill()` for saving to disk
    - `generate_skill_from_gap_id()` high-level function
  - Added `bpsai-pair skill generate` CLI command:
    - Lists available gaps if no ID provided
    - `--preview` flag to preview without saving
    - `--auto-approve` flag to save without confirmation
    - `--force` flag to overwrite existing skill
  - Generated skills include:
    - Valid YAML frontmatter (name, description)
    - Third-person voice descriptions
    - Observed commands as workflow steps
    - Placeholders for customization
    - Auto-generation notice
  - All generated skills pass validation
  - 19 new tests, all 123 skill-related tests pass

### 2025-12-23 - T25.18 Complete (Skill Gap Detection)

- **T25.18: Skill Gap Detection** ✓
  - Created `bpsai_pair/skills/gap_detector.py` module with:
    - `SkillGap` dataclass with serialization support
    - `SkillGapDetector` class for session analysis
    - `GapPersistence` class for saving/loading gaps to history
    - `detect_gaps_from_history()` high-level function
    - `format_gap_notification()` for user notifications
  - Added `bpsai-pair skill gaps` CLI command:
    - Lists detected gaps from history
    - `--analyze` flag to run fresh detection
    - `--json` flag for JSON output
    - `--clear` flag to clear gap history
  - Gap detection features:
    - Detects repeated command sequences (3+ occurrences)
    - Calculates confidence scores based on frequency
    - Reduces confidence for overlaps with existing skills
    - Generates gerund-form skill names
    - Estimates time savings
  - Persists gaps to `.paircoder/history/skill-gaps.jsonl`
  - 22 new tests, all 104 skill-related tests pass

### 2025-12-23 - T25.17 Complete (/update-skills Slash Command)

- **T25.17: /update-skills Slash Command** ✓
  - Created `.claude/commands/update-skills.md` slash command
  - Created `bpsai_pair/skills/suggestion.py` module with:
    - `HistoryParser` - parses session history files
    - `PatternDetector` - detects repeated command sequences
    - `SkillSuggester` - generates skill suggestions with confidence scores
    - `SkillDraftCreator` - creates skill drafts from suggestions
    - `suggest_skills()` - high-level function for pattern analysis
  - Added `bpsai-pair skill suggest` CLI command:
    - Shows suggestions with confidence scores (0-100%)
    - Detects overlap with existing skills
    - `--create N` flag to create draft for suggestion N
    - `--json` flag for JSON output
    - `--min` flag to set minimum pattern occurrences
  - Integrates with existing skill validator for draft validation
  - Added slash command to cookiecutter template
  - 19 new tests, all passing
  - All 82 skill-related tests pass

### 2025-12-23 - T25.16 Complete (Cross-Platform Skill Structure) - SPRINT 25.5 COMPLETE!

- **T25.16: Cross-Platform Skill Structure** ✓
  - Created `bpsai_pair/skills/exporter.py` module with:
    - `ExportFormat` enum (CURSOR, CONTINUE, WINDSURF)
    - `export_skill()` - export single skill to target format
    - `export_all_skills()` - export all skills
    - `check_portability()` - detect platform-specific features
  - Added `bpsai-pair skill export` CLI command:
    - `skill export <n> --format cursor` - Cursor AI (.cursor/rules/)
    - `skill export <n> --format continue` - Continue.dev (.continue/context/)
    - `skill export <n> --format windsurf` - Windsurf (.windsurfrules)
    - `--all` flag to export all skills
    - `--dry-run` flag to preview without creating
  - Export formats:
    - Cursor: Individual .md files with metadata comments
    - Continue: Individual .md files with context headers
    - Windsurf: Appends to single file with section markers
  - Portability warnings for:
    - Skills with scripts/ directory
    - Skills referencing bpsai-pair commands
    - Skills referencing Claude Code features
  - Created `docs/CROSS_PLATFORM_SKILLS.md` documentation
  - 22 new tests, all 63 skill-related tests pass

**Sprint 25.5: Cross-Platform Skills - COMPLETE!**
- T25.12: Skill naming conventions (gerund form)
- T25.13: Third-person voice descriptions
- T25.14: Creating-skills meta-skill
- T25.15: Skill install command
- T25.16: Skill export command

### 2025-12-23 - T25.15 Complete (Skill Installer Command)

- **T25.15: Skill Installer Command** ✓
  - Created `bpsai_pair/skills/installer.py` module with:
    - `parse_source()` - detect URL vs local path
    - `parse_github_url()` - extract owner/repo/branch/path from GitHub URLs
    - `install_from_path()` - install from local directory
    - `install_from_url()` - download and install from GitHub
    - `check_conflicts()` - detect naming conflicts
    - `get_target_dir()` - get project or personal target
  - Added `bpsai-pair skill install` CLI command:
    - `skill install <path>` - install from local path
    - `skill install <url>` - install from GitHub URL
    - `--name` flag to rename skill during install
    - `--force` flag to overwrite existing skill
    - `--project` / `--personal` flags for target selection
  - Validates skills before installation using existing validator
  - GitHub URL parsing handles tree/blob formats and branches with slashes
  - 25 new tests covering all installation scenarios
  - All 41 skill-related tests pass

### 2025-12-23 - T25.14 Complete (Create skill-creation Skill)

- **T25.14: Create skill-creation Skill** ✓
  - Created `.claude/skills/creating-skills/SKILL.md` (153 lines)
  - Follows Agent Skills specification exactly
  - Includes:
    - Gerund naming convention guidance
    - Third-person voice examples
    - SKILL.md template with frontmatter
    - Validation checklist
    - Common mistakes to avoid
  - Skill triggers on: "create a skill", "new skill", "write a skill"
  - Added to cookiecutter template for new projects
  - Validated with `bpsai-pair skill validate`

### Earlier Session Logs

_See `.paircoder/history/session_archive.md` for entries prior to 2025-12-23._
