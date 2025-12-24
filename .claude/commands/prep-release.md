---
description: Enter Release Engineer role to prepare a release with documentation verification and security checks
allowed-tools: Bash(bpsai-pair:*), Bash(git:*), Bash(pytest:*), Bash(pip:*), Bash(grep:*), Bash(diff:*), Bash(rm:*), Bash(cd:*), Bash(ls:*)
argument-hint: <version>
---

# Release Engineer Role - Release Preparation Workflow

You are now in **Release Engineer role**. Your job is to prepare a bulletproof release.

The version is: `$ARGUMENTS` (e.g., `v2.8.1` or `2.8.1`)

## Phase 1: Pre-Release Validation

### 1.1 Verify All Sprint Tasks Complete

```bash
# Check for incomplete tasks
bpsai-pair task list --status in_progress
bpsai-pair task list --status blocked

# Check current state
bpsai-pair status
```

**BLOCKER**: If any tasks are in_progress or blocked, they must be completed or moved to next sprint before release.

### 1.2 Run Full Test Suite

```bash
# All tests must pass
pytest tests/ -v --tb=short

# Check coverage meets target (80%)
pytest tests/ --cov=bpsai_pair --cov-report=term-missing --cov-fail-under=80
```

**BLOCKER**: Release cannot proceed if tests fail.

### 1.3 Security Scans

```bash
# Scan for accidentally committed secrets
bpsai-pair security scan-secrets

# Scan dependencies for known vulnerabilities
bpsai-pair security scan-deps
```

**BLOCKER**: Release cannot proceed if secrets are detected.
**WARNING**: Dependency vulnerabilities should be reviewed but may not block.

## Phase 2: Version Bump

```bash
# Determine current version
grep -E "^version|__version__" tools/cli/pyproject.toml tools/cli/bpsai_pair/__init__.py

# Update version in both files
# pyproject.toml: version = "X.Y.Z"
# __init__.py: __version__ = "X.Y.Z"
```

Edit both files to set the new version (without 'v' prefix in the files).

## Phase 3: Documentation Verification

### 3.1 Required Documentation Check

For PairCoder, verify these files are updated:

```bash
# Check CHANGELOG has entry for this version
grep -A 20 "## \[$ARGUMENTS\]" CHANGELOG.md || grep -A 20 "## $ARGUMENTS" CHANGELOG.md

# Check README mentions current features
head -100 README.md

# Check FEATURE_MATRIX is current
cat .paircoder/docs/FEATURE_MATRIX.md | head -50
```

### 3.2 Documentation Freshness

Check when key docs were last modified:

```bash
# Check modification dates
git log -1 --format="%ci" -- README.md
git log -1 --format="%ci" -- CHANGELOG.md
git log -1 --format="%ci" -- .paircoder/docs/FEATURE_MATRIX.md
git log -1 --format="%ci" -- docs/user-guide.md 2>/dev/null || echo "No user guide"
```

**WARNING** if any required doc is older than 7 days - may need update.

### 3.3 CHANGELOG Entry

If CHANGELOG doesn't have an entry for this version, create one:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Fix 1

### Removed
- (if applicable)
```

Use `bpsai-pair task changelog-preview --since <last-version>` to help generate content.

## Phase 4: Cookiecutter Template Sync (PairCoder Only)

For PairCoder releases, verify the cookiecutter template matches:

```bash
# Check template exists
ls -la tools/cli/bpsai_pair/data/cookiecutter-paircoder/

# Compare key files
diff .paircoder/config.yaml tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/config.yaml || echo "Config differs"

diff CLAUDE.md tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CLAUDE.md || echo "CLAUDE.md differs"
```

**WARNING** if files differ significantly - template may need update.

Key files that should stay in sync:
- `config.yaml` structure (not values)
- `CLAUDE.md` instructions
- `capabilities.yaml` format
- Flow file formats

## Phase 5: Build Verification

```bash
# Clean any old builds
rm -rf tools/cli/dist/ tools/cli/build/ tools/cli/*.egg-info

# Build the package
cd tools/cli && pip install build && python -m build

# Verify it installs cleanly
pip install dist/*.whl --force-reinstall

# Verify version is correct
bpsai-pair --version
```

## Phase 6: Create Release Checklist

```bash
# Create Trello card for release tracking (optional)
bpsai-pair release checklist $ARGUMENTS --create-trello 2>/dev/null || echo "Manual checklist"
```

Or manually track:

- [ ] All sprint tasks complete
- [ ] Tests passing (100%)
- [ ] Coverage ≥ 80%
- [ ] No secrets in codebase
- [ ] Version bumped in pyproject.toml
- [ ] Version bumped in __init__.py
- [ ] CHANGELOG updated
- [ ] README current
- [ ] FEATURE_MATRIX updated
- [ ] Cookiecutter template synced (if applicable)
- [ ] Package builds successfully
- [ ] Package installs cleanly

## Phase 7: Git Operations

```bash
# Stage all changes
git add -A

# Commit with release message
git commit -m "Release $ARGUMENTS"

# Create annotated tag
git tag -a "$ARGUMENTS" -m "Release $ARGUMENTS"

# Show what will be pushed
git log --oneline -5
git tag -l | tail -5
```

**DO NOT push yet** - let user review and confirm.

## Phase 8: Report Summary

Provide release summary to user:

```
📦 **Release Prepared**: $ARGUMENTS

**Pre-Release Checks**:
- ✅ All tasks complete
- ✅ Tests: XXX passed
- ✅ Coverage: XX%
- ✅ Security: Clean

**Documentation**:
- ✅ CHANGELOG: Updated
- ✅ README: Current
- ✅ FEATURE_MATRIX: Updated
- ⚠️ User guide: Last updated X days ago (review recommended)

**Cookiecutter**: 
- ✅ Template synced

**Build**:
- ✅ Package built: bpsai_pair-X.Y.Z-py3-none-any.whl
- ✅ Installs cleanly
- ✅ Version verified

**Ready to Release**:
```bash
git push origin main
git push origin $ARGUMENTS
```

Then publish to PyPI:
```bash
cd tools/cli && twine upload dist/*
```
```

## Error Handling

### If tests fail:
1. Do not proceed with release
2. Fix failing tests
3. Re-run from Phase 1

### If secrets detected:
1. Do not proceed with release
2. Remove secrets from history (git filter-branch or BFG)
3. Rotate any exposed credentials
4. Re-run security scan

### If documentation is stale:
1. This is a WARNING, not a blocker
2. User can choose to update or proceed
3. Log the decision

### If cookiecutter differs:
1. Determine if difference is intentional
2. If template should be updated, do so
3. If difference is project-specific, document why

## Configuration Reference

Release configuration in `config.yaml`:
```yaml
release:
  version_source: tools/cli/pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
    - .paircoder/docs/FEATURE_MATRIX.md
  cookie_cutter:
    template_path: tools/cli/bpsai_pair/data/cookiecutter-paircoder
    sync_required: true
  freshness_days: 7
```

## Reminders

- Version format: `X.Y.Z` in files, `vX.Y.Z` for git tags
- CHANGELOG follows Keep a Changelog format
- Always verify package installs before pushing
- Security scans are BLOCKERS, not warnings
- User must explicitly approve the push
