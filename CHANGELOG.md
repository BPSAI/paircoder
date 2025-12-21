# Changelog

All notable changes to the PairCoder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.6.0] - 2025-12-18 (Release: Sprints 14-17 Consolidated)

### Added

#### Sprint 17: Time, Tokens & Metrics
- **Complexity to Hours Mapping** (TASK-102) — Estimate task duration from complexity
  - `HoursEstimate` with min/expected/max hours by size band (XS-XL)
  - Configurable via `.paircoder/config.yaml` `estimation.complexity_to_hours`
  - `Task.estimated_hours` property for automatic estimation
- **Auto-Timer Start/Stop** (TASK-103) — Timer follows task status
  - Timer auto-starts on `task update --status in_progress`
  - Timer auto-stops on `task update --status done`
  - Full state persistence across sessions
- **Actual vs Estimated Tracking** (TASK-104) — Learn from real task completion data
  - `TaskComparison` dataclass for variance calculations
  - `record_task_completion()` logging to `task-completions.jsonl`
  - Estimation accuracy statistics across all completions
- **Velocity Calculation** (TASK-105) — Track team/individual velocity
  - `VelocityTracker` with weekly and sprint-based metrics
  - `bpsai-pair metrics velocity` command
  - Auto-recording via `record_velocity` hook
- **Sprint Burndown Chart Data** (TASK-106) — Visualization data generation
  - `BurndownGenerator` with ideal vs actual remaining points
  - `bpsai-pair metrics burndown --sprint <id>` command
  - JSON output for integration with visualization tools
- **Estimation Accuracy Report** (TASK-107) — Analyze estimation patterns
  - Accuracy breakdown by task type and complexity band
  - `bpsai-pair metrics accuracy` command
  - Actionable recommendations for estimate calibration
- **Token Estimation Model** (TASK-133) — Predict token usage per task
  - `TokenEstimator` with configurable coefficients
  - Formula: base_context + (complexity × per_point) × type_multiplier + (files × per_file)
  - `Task.estimated_tokens` property
- **Token Estimation Feedback Loop** (TASK-138) — Self-improving estimates
  - `TokenFeedbackTracker` records actual vs estimated tokens
  - Learning algorithm adjusts coefficients based on historical data
  - `bpsai-pair metrics tokens` accuracy report

#### Cookie Cutter Template Updates
- Added `security.md` agent for pre-execution security review
- Added `.claude/hooks/` directory with `security-review.md`
- Added `.paircoder/security/` with allowlist, sandbox, and secret-allowlist configs
- Added `paircoder-task-lifecycle` skill
- Updated `config.yaml` with estimation and token settings
- Added `.claude/commands/` with starter slash commands (`/status`, `/pc-plan`, `/task`)
- **Reorganized documentation structure** (TASK-156):
  - Moved `docs/USER_GUIDE.md` → `.paircoder/docs/USER_GUIDE.md`
  - Added `.paircoder/docs/MCP_SETUP.md` (MCP server configuration)
  - Added `.paircoder/docs/FEATURE_MATRIX.md` (capabilities reference)
  - `docs/` now reserved for project-specific documentation

#### Migration Guide (v2.5 → v2.6)

For existing PairCoder projects, run these commands to update your documentation structure:

```bash
# Create PairCoder docs directory
mkdir -p .paircoder/docs

# Move PairCoder documentation (if exists)
mv docs/USER_GUIDE.md .paircoder/docs/ 2>/dev/null || true

# Create project docs placeholder
echo "# Project Documentation" > docs/.gitkeep

# Download new documentation files
curl -sL https://raw.githubusercontent.com/bps-ai/paircoder/main/tools/cli/bpsai_pair/data/cookiecutter-paircoder/%7B%7Bcookiecutter.project_slug%7D%7D/.paircoder/docs/MCP_SETUP.md > .paircoder/docs/MCP_SETUP.md
curl -sL https://raw.githubusercontent.com/bps-ai/paircoder/main/tools/cli/bpsai_pair/data/cookiecutter-paircoder/%7B%7Bcookiecutter.project_slug%7D%7D/.paircoder/docs/FEATURE_MATRIX.md > .paircoder/docs/FEATURE_MATRIX.md
```

**New directory structure:**
```
.paircoder/docs/      # PairCoder documentation (ships with template)
docs/                 # Your project-specific documentation
```

### Changed
- Version bumped to 2.6 (config.yaml)
- Task storage now flat (all tasks in `.paircoder/tasks/`, no subdirectories)
- `plan sync-trello` auto-loads `board_id` from config
- Enhanced hooks: `record_velocity`, `record_token_usage` added to `on_task_complete`

### Fixed
- Trello list name matching (flexible spacing around slashes)
- Task parser handles both flat and legacy nested structures

---

## [v2.5.4] - 2025-12-18 (Sprint 16: Real Subagents)

### Added
- **Agent Invocation Framework** (TASK-096) — Base framework for invoking specialized agents
  - `AgentInvoker` class loads agent definitions from `.claude/agents/*.md`
  - `AgentDefinition` dataclass parses YAML frontmatter (name, model, permission_mode, tools)
  - `InvocationResult` with output, cost, tokens, and duration tracking
  - Invokes agents via `HeadlessSession` with proper permission modes
  - 48 tests in `test_invoker.py`
- **Planner Agent Implementation** (TASK-097) — Design and planning specialist agent
  - `PlannerAgent` class for architectural planning and design tasks
  - `PlanOutput` with phases, files to modify, complexity estimates
  - `invoke_planner()` convenience function
  - `should_trigger_planner()` for automatic routing
  - Permission mode: plan (read-only) for safe exploration
  - 26 tests in `test_planner_agent.py`
- **Reviewer Agent Implementation** (TASK-098) — Code review specialist agent
  - `ReviewerAgent` class for code quality review
  - `ReviewOutput` with items, severity levels (blocker, warning, suggestion, praise)
  - `ReviewVerdict` enum (approve, request_changes, comment)
  - `invoke_reviewer()` and `should_trigger_reviewer()` functions
  - Git diff analysis with `extract_changed_files()` and `extract_line_changes()`
  - 26 tests in `test_reviewer_agent.py`
- **Security Agent Implementation** (TASK-099) — Pre-execution security gatekeeper
  - `SecurityAgent` class for security review of commands and code
  - `SecurityDecision` with ALLOW/WARN/BLOCK actions and SOC2 control references
  - `SecurityFinding` dataclass for detailed security issues
  - `AgentEnhancedReviewHook` for AI-powered security review integration
  - `invoke_security()` and `should_trigger_security()` functions
  - 37 tests in `test_security_agent.py`
- **Enhanced Agent Handoff Protocol** (TASK-100) — Structured context passing between agents
  - `EnhancedHandoffPackage` with full task context, acceptance criteria, files touched
  - `HandoffChain` for tracking multi-agent workflow history
  - `HandoffSerializer` for disk persistence in `.paircoder/handoffs/`
  - `prepare_handoff()` and `receive_handoff()` functions
  - Chain depth and previous handoff tracking for debugging
  - Token budget estimation for handoffs
  - 22 tests in `test_handoff_protocol.py`
- **Agent Selection Logic** (TASK-101) — Intelligent task-to-agent routing
  - `AgentSelector` class with scoring algorithm
  - `SelectionCriteria` with auto-detection of security/review requirements
  - `AgentMatch` with score, reasons, and permission mode
  - Selection rules: design→planner, review→reviewer, security→security, default→claude-code
  - `bpsai-pair orchestrate select-agent` command for agent recommendations
  - Enhanced `bpsai-pair orchestrate analyze` shows specialized agent suggestions
  - 27 tests in `test_agent_selection.py`

### Changed
- Test count increased from 541 to 1247 (706 new tests across all modules)
- Orchestration module now exports all agent-related classes and functions
- CLI enhanced with specialized agent selection commands

---

## [v2.5.3] - 2025-12-17 (Sprint 15 Final)

### Added
- **Secret Detection** (TASK-094) — Pre-commit secret scanning with pattern matching
  - `SecretScanner` class with patterns for AWS keys, GitHub tokens, Slack tokens, private keys
  - `scan_file()`, `scan_diff()`, `scan_staged()` methods
  - Allowlist support for false positive suppression
  - Integration with pre-commit hooks
  - 15 tests in `test_security_secrets.py`
- **Dependency Vulnerability Scan** (TASK-095) — CVE scanning for project dependencies
  - `DependencyScanner` for Python (pip-audit) and npm (npm audit) dependencies
  - `Vulnerability` dataclass with package, version, CVE ID, severity, fixed version
  - `ScanReport` with critical/high severity detection
  - `bpsai-pair scan-deps` command with `--fail-on` severity threshold
  - 18 tests in `test_security_dependencies.py`

### Changed
- Sprint 15 security features complete (TASK-089 through TASK-095)
- Test count increased from 541 to 574 (33 new security tests)

---

## [v2.5.2] - 2025-12-17 (Sprint 15: Security & Sandboxing)

### Added
- **Security Agent Definition** (TASK-089) — Pre-execution security gatekeeper with SOC2 compliance focus
  - `.claude/agents/security.md` with block/warn/allow decision framework
  - Security checklist for code, commands, and git operations
  - SOC2 control references (CC6.1, CC6.6, CC7.1, etc.)
- **Command Allowlist System** (TASK-090) — Safe vs unsafe command classification
  - `AllowlistManager` with ALLOW, REVIEW, BLOCK decisions
  - Default classifications: always allowed (git status, pytest), require review (git push), always blocked (rm -rf /)
  - Configurable via `.paircoder/security/allowlist.yaml`
  - 39 tests in `test_security_allowlist.py`
- **Pre-execution Security Review** (TASK-091) — Security hooks for command and code review
  - `SecurityReviewHook` class for pre-execution command review
  - `CodeChangeReviewer` for scanning staged code changes
  - Secret detection patterns: API keys, AWS credentials, GitHub/Slack tokens, JWTs, private keys
  - Injection vulnerability detection: SQL injection, command injection, path traversal
  - 35 tests in `test_security_review.py`
- **Docker Sandbox Runner** (TASK-092) — Isolated container execution for untrusted commands
  - `SandboxRunner` with configurable containers (image, memory, CPU limits)
  - Network isolation (default: none) for security
  - File change tracking via `container.diff()`
  - Non-root `sandbox` user for defense in depth
  - 35 tests in `test_security_sandbox.py`
- **Git Checkpoint/Rollback** (TASK-093) — Automatic safety nets for code changes
  - `GitCheckpoint` class with full checkpoint management
  - `create_checkpoint()`, `rollback_to()`, `rollback_to_last()`, `list_checkpoints()`
  - `preview_rollback()` for safe review before rollback
  - Retention policy with `cleanup_old_checkpoints()`
  - 20 tests in `test_security_checkpoint.py`

### Changed
- Test count increased from 412 to 541+ (129 new security tests)
- Documentation updated with Sprint 15 security features

---

## [v2.5.1] - 2025-12-17 (Sprint 14: Trello Deep Integration)

### Added
- **Trello Custom Fields Sync** (TASK-081) — Sync PairCoder fields to Trello custom fields
  - Project, Stack, Status, Effort, Deployment Tag mapping
  - Automatic field creation on board if missing
- **BPS Label Colors** (TASK-082) — Exact color matching for Trello labels
  - Frontend (green #61bd4f), Backend (blue #0079bf), Worker (purple #c377e0)
  - Deployment (red #eb5a46), Bug (orange #ff9f1a), Security (yellow #f2d600)
  - Documentation (sky #00c2e0), AI/ML (black #344563)
- **Card Description Templates** (TASK-083) — BPS-formatted card descriptions
  - Consistent structure for task cards
  - Template expansion with task metadata
- **Effort Field Mapping** (TASK-084) — Complexity to Trello Effort conversion
  - complexity 0-20 → XS, 21-40 → S, 41-60 → M, 61-80 → L, 81-100 → XL
- **Two-way Sync** (TASK-085) — Trello card movements update local task status
  - Webhook-driven or poll-based sync options
  - Card in "In Progress" → task status: in_progress
- **Checklist Support** (TASK-086) — Create checklists from acceptance criteria
  - Task acceptance criteria automatically create checklist items
  - Check/uncheck synced bidirectionally
- **Due Date Sync** (TASK-087) — Sync plan due dates to Trello cards
  - Sprint end dates propagate to card due dates
- **Activity Log Comments** (TASK-088) — Automated progress tracking via comments
  - Task status changes logged as card comments
  - Agent progress updates visible in Trello activity
- **Check/Uncheck Checklist Items** — New commands with partial text matching
  - `bpsai-pair trello check TASK-001 "implement"` — checks items containing "implement"
  - `bpsai-pair trello uncheck TASK-001 "test"` — unchecks items containing "test"

### Changed
- Trello integration now creates cards indistinguishable from manually-created BPS cards
- Enhanced credential persistence across sessions

---

## [v2.5.0] - 2025-12-16

### Added
- **Preset System** - 8 built-in presets for quick project initialization
  - `bpsai-pair preset list` - List available presets
  - `bpsai-pair preset show <name>` - Show preset details
  - `bpsai-pair preset preview <name>` - Preview generated config
  - `bpsai-pair init --preset <name>` - Initialize with preset
  - Presets: python-cli, python-api, react, fullstack, library, minimal, autonomous, **bps**
- **BPS Preset** - Full BPS AI Software workflow with 7-list Trello structure
  - Lists: Intake/Backlog, Planned/Ready, In Progress, Review/Testing, Deployed/Done, Issues/Tech Debt, Notes/Ops Log
  - 8 label colors for stack types (Backend, Frontend, Database, etc.)
  - Automation mappings for task events
  - Hooks enabled by default
- **GitHub PR Integration** - Automated pull request workflows
  - `bpsai-pair github auto-pr` - Auto-create PR from branch name (detects TASK-xxx)
  - `bpsai-pair github archive-merged <pr>` - Archive task when PR merges
  - `bpsai-pair github archive-merged --all` - Scan and archive all merged PRs
  - `bpsai-pair github link <task>` - Link task to existing PR
- **Trello Progress Comments** - Report progress directly on Trello cards
  - `bpsai-pair trello progress TASK-001 "message"` - Post progress update
  - `bpsai-pair trello progress TASK-001 --started` - Report task started
  - `bpsai-pair trello progress TASK-001 --blocked "reason"` - Report blocked
  - `bpsai-pair trello progress TASK-001 --completed "summary"` - Report completion
  - `bpsai-pair trello progress TASK-001 --review` - Request review
- **Daily Standup Summary** - Generate team status updates
  - `bpsai-pair standup generate` - Generate markdown summary
  - `bpsai-pair standup generate --format slack` - Slack-formatted output
  - `bpsai-pair standup generate --since 48` - Custom lookback period
  - `bpsai-pair standup post` - Post summary to Trello Notes list
- **Intent Detection** - Detect work intent from natural language
  - `bpsai-pair intent detect <text>` - Detect intent type
  - `bpsai-pair intent should-plan <text>` - Check if planning needed
  - `bpsai-pair intent suggest-flow <text>` - Suggest appropriate flow
- **Autonomous Workflow Framework** - State machine for hands-off task execution
  - `bpsai-pair orchestrate auto-session` - Run autonomous session
  - `bpsai-pair orchestrate workflow-status` - Show workflow state
  - Event logging and task selection logic
- **Trello Webhook Server** - Listen for card movements
  - `bpsai-pair trello webhook serve` - Start webhook server
  - `bpsai-pair trello webhook status` - Check webhook status
  - Agent assignment when cards move to Ready column
- **23 new tests** for progress reporter, standup, and GitHub integration (412 total tests)

### Fixed
- **Hook Reliability** - Hooks now ALWAYS fire on task status changes
  - `task update --status in_progress` fires `on_task_start` hooks
  - `task update --status done` fires `on_task_complete` hooks
  - `task update --status blocked` fires `on_task_block` hooks
- **Config Path Compatibility** - Hooks check both `trello.automation` and `trello.card_format.automation`
- **TaskParser API** - Fixed `task_parser.get()` → `task_parser.get_task_by_id()` across all modules

### Changed
- Version bumped to 2.5.0 across all files
- README updated with 80+ commands and new feature sections
- Total command count now 80+ (up from 60+)

## [v2.4.0] - 2025-12-16

### Added
- **MCP Server Integration** - Claude and MCP-compatible agents can now call PairCoder tools directly
  - `bpsai-pair mcp serve` - Start MCP server (stdio transport)
  - `bpsai-pair mcp tools` - List all 13 available tools
  - `bpsai-pair mcp test <tool>` - Test tools locally without MCP client
  - Tools: task management (4), planning (2), context (1), orchestration (2), metrics (2), Trello (2)
- **Auto-Hooks System** - Automatic actions triggered on task state changes
  - Configurable hooks in `.paircoder/config.yaml`
  - Built-in hooks: start_timer, stop_timer, record_metrics, sync_trello, update_state, check_unblocked
  - Events: on_task_start, on_task_complete, on_task_block
- **Plan-to-Trello Sync** - `bpsai-pair plan sync-trello <plan-id>` creates Trello cards from plan tasks
- **Enhanced Plan Status** - `bpsai-pair plan status` shows comprehensive progress with sprint breakdown
- **Skills "Recording Your Work"** - All 6 skills now include CLI/MCP commands for tracking work
- **29 new tests** for MCP server, tools, and hooks (245 total tests)

### Fixed
- Task list discovery now properly finds all tasks in `.paircoder/tasks/` directories
- Plan status correctly counts tasks by filtering on plan_id field in frontmatter
- Added missing `get_tasks_for_plan()` method to TaskParser

### Changed
- All skills updated with explicit "Recording Your Work" sections
- Config schema extended with comprehensive hooks configuration
- Version bumped across all files (pyproject.toml, __init__.py, config.yaml)

## [v2.3.0] - 2025-12-15

### Added
- **Trello Integration** - Full Trello board and card management
  - `bpsai-pair trello connect` - Store API credentials securely
  - `bpsai-pair trello status` - Check connection status
  - `bpsai-pair trello boards` - List available boards
  - `bpsai-pair trello use-board` - Set active board for project
  - `bpsai-pair trello lists` - Show lists on active board
  - `bpsai-pair trello config` - View/modify Trello settings
- **Trello Task Commands** - Work with Trello cards as tasks
  - `bpsai-pair ttask list` - List tasks from board
  - `bpsai-pair ttask show` - View task details
  - `bpsai-pair ttask start` - Claim and start task
  - `bpsai-pair ttask done` - Complete task with summary
  - `bpsai-pair ttask block` - Mark task as blocked
  - `bpsai-pair ttask comment` - Add progress comment
  - `bpsai-pair ttask move` - Move task to different list
- **Trello Skills** - New skills for Trello-based workflows
  - `trello-task-workflow` - Work on tasks from Trello board
  - `trello-aware-planning` - Create plans synced to Trello
- **21 new tests** for Trello integration (216 total tests)

### Changed
- Config schema updated with Trello list mapping and custom field settings
- CLAUDE.md and capabilities.yaml updated with Trello integration

## [v2.2.0] - 2025-12-15

### Added
- Prompt caching for efficient context management (TASK-037)
- `bpsai-pair cache` commands (stats, clear, invalidate)
- Codex-optimized context packing with `--lite` flag (TASK-038)

### Changed
- Consolidated documentation to repository root (TASK-034)
- Updated cookiecutter template for v2.2 structure (TASK-036)
- Improved Codex CLI guidance in AGENTS.md (TASK-038)

### Removed
- Obsolete `prompts/` directory (TASK-035)
- Duplicate documentation from tools/cli/ (TASK-034)

### Fixed
- Nested cookiecutter template path (TASK-036)
- Task title parsing in lifecycle module

### Infrastructure
- Archived v2-upgrade plan (32 tasks) (TASK-033)

## [v2.1.0] - 2025-12-15

### Added
- Headless Mode Integration for Orchestration (TASK-025)
- Agent Handoff Protocol (TASK-026)
- Codex CLI Adapter (TASK-027)
- Orchestrator Service (TASK-028)
- Task Lifecycle Management (TASK-029)
- Token Tracking and Cost Estimation (TASK-030)
- Time Tracking Integration (TASK-031)
- Benchmarking Framework (TASK-032)

## [1.0.0] - 2025-09-05

### Closed Beta
- **Released in closed beta to gather feedback and plans for v2 upgrade.** 

## [0.2.5] - 2025-09-01

### Changed
- **Template docs** — Clarified "Gotchas" guidance in `directory_note.md` for clearer setup instructions
- **Agent instructions** — Reformatted `agents.md` working rules for improved readability in new projects

### Developer Notes
- Documentation-only adjustments in the bundled template; no functional changes

## [0.2.4] - 2025-09-01

### Added
- **Windows & Cross-Platform quickstart** — Clear, copy-pasteable PowerShell setup (venv, ExecutionPolicy, activation) added to README and USER_GUIDE
- **CLI fallback note** — Explicit `python -m bpsai_pair.cli --help` guidance when PATH entry point isn’t available

### Changed
- **Package README** — Expanded Quick Start with Windows-specific instructions directly below install steps
- **README/USER_GUIDE parity** — Aligned wording and examples so all three docs (repo README, package README, USER_GUIDE) present consistent Windows initialization
- **Local wheel path** — Corrected example to `.\dist\bpsai_pair-*.whl` in Windows snippets

### Fixed
- **Minor typos** — Corrected activation comments (`activate.bat`) and ensured fenced code blocks render cleanly across docs

### Developer Notes
- This is a **documentation-only** release; no API or behavior changes
- Build/publish flow: bump to `0.2.4`, tag (`v0.2.4`), `python -m build`, `twine upload`
- If a stray tag (e.g., `2.0.0`) reappears, remove any GitHub Release/workflow that recreates it and restrict release jobs to **tag events** only


## [0.2.3] - 2025-08-22

### Added
- **Comprehensive user documentation** - Added USER_GUIDE.md to both package distribution and bundled template
- **Documentation accessibility** - Users now receive full documentation both with the package and in initialized projects

### Changed
- **Documentation structure** - Copied paircoder-docs.md working file from repo root to accessible locations for end users & renamed USER_GUIDE.md
- **MANIFEST.in** - Updated to include USER_GUIDE.md in package distribution

### Developer Notes
- Documentation now ships with the package and gets installed in user projects
- Sets foundation for future Sphinx/MkDocs HTML documentation
- Next release (0.3.0) will include proper HTML documentation build

## [0.2.2] - 2025-08-22

### Fixed
- **Windows Unicode encoding** - Added UTF-8 environment variables for Windows CI compatibility
- **Path exclusion patterns** - Improved `.agentpackignore` pattern matching for directories
- **CI smoke tests** - All platforms now passing with proper git configuration

### Changed
- Enhanced `should_exclude` method in `ops.py` for better pattern matching

## [0.2.1] - 2025-08-22

### Added
- **AGENTS.md and CLAUDE.md root pointers** in bundled template - AI agents now have clear entry points that direct them to `/context/` for instructions
- **Comprehensive context documentation** - Real project values replace all placeholders in development.md and agents.md
- **Directory notes** - Added `context/directory_notes/tools-cli.md` to clarify package structure
- **Git configuration in CI** - Smoke tests now properly configure git identity for commit operations

### Changed
- **Template consolidation** - Removed redundant `tools/cookiecutter-paircoder/` directory; template now lives exclusively in `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`
- **Repository structure alignment** - Clear separation between package development (`tools/cli/`) and reference implementation (root)
- **Documentation updates** - All references to project structure now point to `/context/project_tree.md` as single source of truth
- **CLI README** - Removed incorrect path references and clarified bundled template usage

### Fixed
- **Corrupted workflow** - Fixed `project_tree.yml` workflow with proper cron syntax and complete tree generation logic
- **CI smoke tests** - Added git user configuration to prevent commit failures in GitHub Actions
- **Template completeness** - Ensured bundled template includes all necessary files for fully functional PairCoder projects
- **Navigation clarity** - Eliminated conflicting agent instructions; single clear path from root → `/context/`

### Removed
- **Redundant template directory** - Deleted `tools/cookiecutter-paircoder/` to eliminate confusion and maintenance burden
- **Outdated shell scripts** - Fully replaced with Python implementations for cross-platform compatibility

### Developer Notes
- This release focuses on **structural clarity** and **template consolidation**
- The repository now properly demonstrates PairCoder principles while developing the tool itself
- All placeholder values (`<PROJECT NAME>`, `<PRIMARY GOAL>`, etc.) have been replaced with actual project values
- The dual nature of the repo (package + reference implementation) is now clearly documented

### Migration Guide
For users upgrading from 0.2.0:
- No breaking changes to CLI commands
- If you've customized templates, ensure you're using the bundled version at `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`
- Run `bpsai-pair-init` in new projects to get the improved template with AGENTS.md/CLAUDE.md files

---

## [0.2.0] - 2025-08-21

### Added
- **Cross-platform CLI** - Core actions implemented in pure Python (no Bash required)
- **Portable CI smoke matrix** - Testing across Ubuntu, macOS, Windows with Python 3.10–3.12
- **Branch type support** - `feature --type` now supports `feature|fix|refactor`
- **JSON output mode** - Basic JSON output for some commands (experimental)
- **Pack preview options** - Added `--dry-run`, `--list`, and `--json` flags to pack command
- **Status command** - New `bpsai-pair status` shows current context and recent changes
- **Validate command** - Check repo structure and context consistency
- **Local CI command** - Run local checks with `bpsai-pair ci`

### Changed
- **Improved documentation** - Root `AGENTS.md`, branch types documentation, troubleshooting guide
- **Better error messages** - Friendlier CLI output with Rich formatting
- **Template hygiene** - Cleaner agent boundaries and instructions

### Fixed
- **Windows compatibility** - All commands now work on Windows without WSL
- **Path handling** - Cross-platform path operations throughout

---

## [0.1.3] - 2025-08-10

### Added
- **Initial public release** - Core package/CLI functionality
- **Hardened CLI UX** - Default bundled init, --next alias, friendlier errors
- **Pack previews** - Early version of dry-run/list functionality
- **Agents guide** - Expanded documentation for AI agents
- **Roadmap updates** - Clear versioning and feature planning

### Changed
- Repository treated as living reference implementation
- Documentation alignment across all files

---

## [0.1.0] - 2025-08-07

### Added
- **Initial development release**
- Basic CLI commands: `init`, `feature`, `pack`, `context-sync`
- Cookiecutter template for project scaffolding
- Context loop concept and implementation
- Basic CI workflows
- Pre-commit configuration
