# Changelog

All notable changes to the PairCoder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
