# Current State

> Last updated: 2025-12-18 (evening session)

## Active Plan

**Plan:** `plan-2025-12-sprint-17-time-tokens-metrics`
**Status:** In Progress
**Current Sprint:** sprint-17

**Previous:** `plan-2025-12-sprint-16-real-subagents` (complete)

## Current Focus

Sprint 17: Time, Tokens & Metrics - Know how much things cost.

**Sprint 17 Tasks:**
- TASK-102: Complexity to hours mapping ✓
- TASK-103: Auto-timer that actually works ✓
- TASK-104: Actual vs estimated tracking ✓
- TASK-105: Velocity calculation ✓
- TASK-106: Sprint burndown chart data ✓
- TASK-107: Estimation accuracy report ✓
- TASK-133: Token estimation model (pending)
- TASK-138: Token estimation feedback loop (pending)

**Progress:** 6/8 tasks complete (165/230 points)

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

**Sprint 17 Remaining Tasks:**
- TASK-133: Token estimation model
- TASK-138: Token estimation feedback loop

**Sprint 17 Success Criteria:**
- [x] Complexity → hours mapping working
- [x] Auto-timer starts/stops with task status
- [x] Actual vs estimated tracking recorded
- [x] Velocity calculation available
- [x] Burndown chart data generated
- [x] Estimation accuracy report available
- [ ] Token estimation model implemented
- [ ] Token feedback loop working

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
