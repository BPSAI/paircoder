# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-15

### Added

#### Planning System
- `bpsai-pair plan new` - Create plans with goals and tasks
- `bpsai-pair plan list` - List all plans
- `bpsai-pair plan show` - Show plan details
- `bpsai-pair plan tasks` - List tasks for a plan
- `bpsai-pair plan add-task` - Add tasks to a plan

#### Task Management
- `bpsai-pair task list` - List all tasks
- `bpsai-pair task show` - Show task details
- `bpsai-pair task update` - Update task status (pending, in_progress, done, blocked)
- `bpsai-pair task next` - Get next task to work on

#### Flows (Workflows)
- `bpsai-pair flow list` - List available workflows
- `bpsai-pair flow show` - Show flow details
- `bpsai-pair flow run` - Run a workflow
- `bpsai-pair flow validate` - Validate flow definitions
- New `.flow.md` format (YAML frontmatter + Markdown body)
- Built-in flows: tdd-implement, design-plan-implement, review, finish-branch

#### LLM Integration
- `.paircoder/capabilities.yaml` - Capability manifest for AI agents
- Role-based operations (Navigator, Driver, Reviewer)
- Flow triggers for automatic workflow suggestions
- Enhanced `AGENTS.md` and `CLAUDE.md` root pointer files

#### Project Structure
- New `.paircoder/` directory for all configuration
- `.paircoder/config.yaml` - Centralized configuration
- `.paircoder/context/project.md` - Project overview
- `.paircoder/context/workflow.md` - Development workflow
- `.paircoder/context/state.md` - Current state tracking
- `.paircoder/flows/` - Workflow definitions
- `.paircoder/plans/` - Plan files
- `.paircoder/tasks/` - Task files organized by plan

### Changed

- Flow parser now supports both `.flow.yml` and `.flow.md` formats
- Updated cookiecutter template with v2 structure
- Improved JSON output (no Rich console interference)
- Enhanced USER_GUIDE.md with v2 documentation
- Updated README.md with new command reference

### Fixed

- JSON output formatting issues with Rich console
- Flow list now shows all flow formats

### Migration from v1

- The old `context/` directory is still supported
- Run `bpsai-pair init` to add `.paircoder/` structure
- Update `AGENTS.md` and `CLAUDE.md` to point to `.paircoder/`

## [0.2.5] - 2025-01-01

### Added
- Initial flow support with `.flow.yml` format
- Basic flow list/show/run/validate commands

## [0.2.0] - 2024-12-01

### Added
- Windows support (fully Python-backed, no Bash required)
- `bpsai-pair ci` command for local CI checks
- `bpsai-pair pack --list` for preview
- `bpsai-pair pack --json` for JSON output

## [0.1.0] - 2024-11-01

### Added
- Initial release
- `bpsai-pair init` command
- `bpsai-pair feature` command
- `bpsai-pair pack` command
- `bpsai-pair context-sync` command
- `bpsai-pair status` command
- `bpsai-pair validate` command
- Cookiecutter template for new projects
