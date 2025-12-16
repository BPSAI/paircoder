# Changelog

All notable changes to the PairCoder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
