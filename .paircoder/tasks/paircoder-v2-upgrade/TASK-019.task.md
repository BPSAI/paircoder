---
id: TASK-019
plan: plan-2025-01-paircoder-v2-upgrade
title: Bump version and prepare release
type: chore
priority: P2
complexity: 15
status: pending
sprint: sprint-4
tags: [release, version, chore]
---

# Objective

Bump the version number, update CHANGELOG, and prepare for v2.0.0 (or v0.3.0) release.

# Implementation Plan

1. Decide on version number:
   - Option A: `2.0.0` (major version for v2 architecture)
   - Option B: `0.3.0` (continue pre-1.0 versioning)

2. Update version in `pyproject.toml`

3. Update `CHANGELOG.md`:
   - Add v2.0.0 section
   - List all new features
   - List breaking changes
   - List migration notes

4. Update `__version__` in package `__init__.py`

5. Create git tag

6. (Optional) Build and publish to PyPI

# Files to Modify

- `tools/cli/pyproject.toml` - version field
- `tools/cli/bpsai_pair/__init__.py` - __version__
- `CHANGELOG.md` - release notes

# CHANGELOG Content

```markdown
## [2.0.0] - 2025-12-15

### Added
- Planning system with Goals → Tasks → Sprints workflow
- `bpsai-pair plan` commands (new, list, show, tasks, add-task)
- `bpsai-pair task` commands (list, show, update, next)
- Flow parser v2 supporting .flow.md format (YAML frontmatter + Markdown)
- LLM capability manifest (.paircoder/capabilities.yaml)
- Consolidated directory structure under .paircoder/
- Context files: project.md, workflow.md, state.md
- Built-in flows: design-plan-implement, tdd-implement, review, finish-branch

### Changed
- Config file location: .paircoder/config.yaml (was .paircoder.yml)
- Flow files now use .flow.md extension (legacy .flow.yml still supported)
- AGENTS.md and CLAUDE.md now point to .paircoder/ directory

### Migration
- Existing projects: Run `bpsai-pair init` to add v2 structure
- v1 context/ directory can coexist during transition
- See USER_GUIDE.md for full migration instructions
```

# Acceptance Criteria

- [ ] Version bumped in pyproject.toml
- [ ] Version bumped in __init__.py
- [ ] CHANGELOG updated with v2 features
- [ ] Git tag created (after merge to main)
- [ ] Package builds successfully: `python -m build`

# Verification

```bash
# Check version consistency
grep version tools/cli/pyproject.toml
grep __version__ tools/cli/bpsai_pair/__init__.py

# Build package
cd tools/cli
python -m build

# Check built package
ls dist/
```

# Notes

Consider whether to release as 2.0.0 (signals major change) or 0.3.0 (stays pre-1.0). The v2 architecture is a significant change but the project may not be ready for 1.0+ commitment.
