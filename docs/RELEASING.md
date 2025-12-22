# Releasing PairCoder

Step-by-step guide for preparing and publishing a new PairCoder release.

## Prerequisites

- Write access to the repository
- Python environment with `bpsai-pair` CLI installed
- GitHub CLI (`gh`) for creating releases

## Version Location

**Single Source of Truth:** `tools/cli/pyproject.toml`

The version is read at runtime via `importlib.metadata`, so you only need to update one file.

```toml
# tools/cli/pyproject.toml
[project]
version = "2.6.1"  # <-- Update this
```

## Release Checklist

### 1. Verify Release Readiness

Run the automated release prep command:

```bash
bpsai-pair release prep
```

This checks:
- Version consistency (pyproject.toml matches `__version__`)
- CHANGELOG.md has entry for current version
- Git working tree is clean
- Tests passing
- Documentation freshness

Example output:
```
Release Checklist for v2.6.1:
  ✅ Version bumped in pyproject.toml
  ✅ CHANGELOG.md has v2.6.1 entry
  ✅ Git working tree clean
  ✅ Tests passing
  ⚠️  README.md last updated 5 days ago
```

To check against a previous release:
```bash
bpsai-pair release prep --since v2.6.0
```

### 2. Update CHANGELOG.md

Add an entry for the new version at the top of CHANGELOG.md:

```markdown
## [v2.7.0] - 2025-MM-DD (Sprint XX: Theme)

### Added
- Feature descriptions with task IDs

### Changed
- Modifications with context

### Fixed
- Bug fixes with root cause

### Removed
- Deprecated items
```

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### 3. Check Cookie Cutter Template Sync

The cookie cutter template should match current source files:

```bash
bpsai-pair template check
```

If drift is detected:
```bash
# Auto-fix by syncing source → template
bpsai-pair template check --fix
```

### 4. Run Full Test Suite

```bash
cd tools/cli
pytest -v
```

All tests must pass before release.

### 5. Bump Version

Edit `tools/cli/pyproject.toml`:

```toml
version = "X.Y.Z"
```

Version format follows [Semantic Versioning](https://semver.org/):
- **MAJOR** (X): Breaking changes
- **MINOR** (Y): New features, backwards compatible
- **PATCH** (Z): Bug fixes, backwards compatible

### 6. Commit and Tag

```bash
git add tools/cli/pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### 7. Create GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - Release Title" \
  --notes-file CHANGELOG_EXCERPT.md
```

Or create via GitHub web UI:
1. Go to Releases → "Draft a new release"
2. Choose the tag
3. Copy the CHANGELOG section as release notes
4. Publish

### 8. Publish to PyPI (if applicable)

```bash
cd tools/cli
python -m build
twine upload dist/*
```

## Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `bpsai-pair release prep` | Verify release readiness |
| `bpsai-pair release prep --since vX.Y.Z` | Compare against baseline |
| `bpsai-pair release prep --create-tasks` | Generate tasks for missing items |
| `bpsai-pair release prep --skip-tests` | Skip test suite (faster check) |
| `bpsai-pair release checklist` | Show release checklist |
| `bpsai-pair template check` | Check template drift |
| `bpsai-pair template check --fix` | Auto-sync template |
| `bpsai-pair template check --fail-on-drift` | CI mode (exit 1 on drift) |
| `bpsai-pair template list` | List tracked template files |

## CI/CD Pipeline

### Template Drift Check

The `.github/workflows/template-check.yml` workflow runs on every push/PR:

```yaml
name: Template Drift Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install CLI
        run: pip install -e tools/cli
      - name: Check template drift
        run: bpsai-pair template check --fail-on-drift
```

### Release Workflow

The release workflow triggers on tags:

```yaml
on:
  push:
    tags:
      - 'v*'
```

## Troubleshooting

### Version Mismatch

If `bpsai-pair --version` shows wrong version:
1. Ensure you only have version in `pyproject.toml`
2. Reinstall the package: `pip install -e tools/cli`

### CHANGELOG Missing Entry

The `release prep` command checks for version in CHANGELOG.md. Add the entry before releasing.

### Template Drift

If CI fails with template drift:
```bash
bpsai-pair template check --fix
git add tools/cli/bpsai_pair/data/cookiecutter-paircoder/
git commit -m "chore: sync cookie cutter template"
```

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines including release process
- [CHANGELOG.md](../CHANGELOG.md) - Version history
- Task files from Sprint 18:
  - T18.1: Version string single source of truth
  - T18.2: Release prep command
  - T18.3: Cookie cutter drift detection CLI
