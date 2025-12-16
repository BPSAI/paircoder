# TASK-039: Prepare v2.2.0 Release

## Metadata
- **ID**: TASK-039
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-9
- **Priority**: P0
- **Complexity**: 25
- **Status**: pending
- **Created**: 2025-12-15
- **Tags**: chore, release
- **changelog_entry**: Released PairCoder v2.2.0

## Description

Final release preparation for v2.2.0. This includes version bump, changelog finalization, documentation review, testing, and tag/publish.

## Prerequisites

Before starting this task, ensure:
- [ ] TASK-033 (Archive) - completed
- [ ] TASK-034 (Docs consolidation) - completed
- [ ] TASK-035 (Remove prompts/) - completed
- [ ] TASK-036 (Fix cookiecutter) - completed
- [ ] TASK-037 (Prompt caching) - completed
- [ ] TASK-038 (Codex optimization) - completed OR deferred

## Release Checklist

### 1. Version Bump

**Files to update:**

```bash
# pyproject.toml
sed -i 's/version = "2.0.0"/version = "2.2.0"/' tools/cli/pyproject.toml

# Verify
grep "version" tools/cli/pyproject.toml
```

**Check for other version references:**

```bash
grep -r "2.0.0" . --include="*.py" --include="*.md" --include="*.yaml" | grep -v ".git"
```

### 2. Changelog Finalization

Ensure CHANGELOG.md (at root) has complete v2.2.0 section:

```markdown
## [v2.2.0] - 2025-12-XX

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

### Infrastructure
- Archived v2-upgrade plan (32 tasks) (TASK-033)
```

### 3. Documentation Review

**Quick review of key docs:**

```bash
# README.md - should have current commands
head -100 README.md

# USER_GUIDE.md - should be at root
test -f USER_GUIDE.md && echo "OK" || echo "MISSING"

# AGENTS.md - should have Codex section (if TASK-038 done)
grep -l "Codex" AGENTS.md && echo "Has Codex section"
```

**Check for broken links:**

```bash
# Find markdown links
grep -r "\[.*\](.*\.md)" . --include="*.md" | grep -v ".git" | head -20
```

### 4. Testing

**Run full test suite:**

```bash
cd tools/cli
pip install -e ".[dev]"
pytest -v

# Expected: All tests pass
```

**Smoke test CLI:**

```bash
# Version
bpsai-pair --version
# Expected: 2.2.0

# Help
bpsai-pair --help

# Init test
cd /tmp && mkdir test-v22 && cd test-v22
bpsai-pair init
ls -la
ls -la .paircoder/
ls -la .claude/
# Expected: v2.2 structure created

# Cache commands (if TASK-037 done)
bpsai-pair cache stats
```

**Template test:**

```bash
# Test cookiecutter directly
cd /tmp && mkdir cookie-test && cd cookie-test
cookiecutter /path/to/tools/cli/bpsai_pair/data/cookiecutter-paircoder/ --no-input
ls -la
```

### 5. Build Package

```bash
cd tools/cli

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Verify
ls dist/
# Expected: bpsai_pair-2.2.0.tar.gz, bpsai_pair-2.2.0-py3-none-any.whl

# Test install from wheel
pip install dist/bpsai_pair-2.2.0-py3-none-any.whl --force-reinstall
bpsai-pair --version
# Expected: 2.2.0
```

### 6. Git Tag

```bash
# Ensure clean state
git status
# Expected: clean working tree

# Create annotated tag
git tag -a v2.2.0 -m "Release v2.2.0: Consolidation & Enhancement

Key changes:
- Consolidated documentation to repository root
- Added prompt caching for context management
- Removed obsolete prompts/ directory
- Fixed cookiecutter template path
- Archived v2-upgrade plan (32 tasks)
- Codex optimization improvements

See CHANGELOG.md for full details."

# Verify tag
git show v2.2.0

# Push tag
git push origin v2.2.0
```

### 7. PyPI Publish

```bash
# Ensure twine is installed
pip install twine

# Upload to PyPI
twine upload dist/*

# Verify on PyPI
# https://pypi.org/project/bpsai-pair/
```

### 8. GitHub Release (Optional)

Create GitHub release:
1. Go to Releases page
2. Create new release from v2.2.0 tag
3. Title: "PairCoder v2.2.0: Consolidation & Enhancement"
4. Copy changelog section as description
5. Attach wheel and tarball

### 9. Post-Release Verification

```bash
# Test pip install from PyPI
pip install bpsai-pair==2.2.0 --force-reinstall
bpsai-pair --version
# Expected: 2.2.0

# Test init produces correct structure
cd /tmp && mkdir post-release-test && cd post-release-test
bpsai-pair init
ls -la .paircoder/
# Expected: v2.2 structure
```

### 10. Update State

Update `.paircoder/context/state.md`:

```markdown
## Active Plan

**Plan:** `plan-2025-01-paircoder-v2.2-features`
**Status:** completed

## What Was Just Done

- Released PairCoder v2.2.0
- All Sprint 8-9 tasks completed
- Published to PyPI

## What's Next

- Plan next development cycle (v2.3 or v3)
- Monitor for issues post-release
- Gather user feedback
```

## Acceptance Criteria

- [ ] Version is 2.2.0 in pyproject.toml
- [ ] CHANGELOG.md has v2.2.0 section at root
- [ ] All tests pass
- [ ] Smoke tests pass
- [ ] Package builds successfully
- [ ] Template produces correct structure
- [ ] Tag v2.2.0 created and pushed
- [ ] Package published to PyPI
- [ ] pip install bpsai-pair==2.2.0 works
- [ ] state.md updated to reflect completion

## Dependencies

- All other Sprint 8-9 tasks

## Files to Modify

- `tools/cli/pyproject.toml` (version bump)
- `CHANGELOG.md` (finalize v2.2.0 section)
- `.paircoder/context/state.md` (mark complete)
- `.paircoder/plans/paircoder-v2.2-features.plan.yaml` (mark complete)

## Notes

- Do NOT skip testing - template errors are embarrassing
- Ensure GitHub Actions CI passes before release
- Have rollback plan (yank from PyPI if critical issue)
- Consider announcing release in relevant channels
