# Sprint 18: Release Engineering Foundation

> **Target Version:** v2.6.2
> **Type:** chore
> **Slug:** sprint-18-release-engineering
> **Focus:** Automate releases, create release prep tooling

---

## Trello Card Defaults

When syncing to Trello, use these values for ALL cards in this sprint:

```yaml
Project: PairCoder
Stack: Worker/Function
Repo URL: https://github.com/BPSAI/paircoder
Status: Planning
```

---

## Sprint Goal

Establish automated release engineering processes. Build on Sprint 17.5's cookie cutter audit to create ongoing drift detection and release automation.

**Note:** Sprint 17.5 already completed:
- Cookie cutter full audit (TASK-150)
- Missing preset config sections (TASK-151)
- depends_on fix (TASK-152)
- Plan list task count fix (TASK-153)
- Sprint completion checklist (TASK-160)

---

## Backlog Items

### T18.1: Fix Version String Single Source of Truth

**Priority:** P0
**Effort:** S
**Type:** bugfix

#### Description

`bpsai-pair --version` shows 2.5.4 but package is 2.6.0. The `__version__` in `__init__.py` wasn't updated during release.

#### Root Cause

Version defined in two places:
- `pyproject.toml` (bumped) ✅
- `tools/cli/bpsai_pair/__init__.py` (not bumped) ❌

#### Implementation

Use `importlib.metadata` to read version from pyproject.toml:

```python
# tools/cli/bpsai_pair/__init__.py
from importlib.metadata import version
__version__ = version("bpsai-pair")
```

#### Acceptance Criteria

- [ ] Single source of truth for version (pyproject.toml)
- [ ] `bpsai-pair --version` shows correct version
- [ ] No hardcoded version strings remain in __init__.py
- [ ] Test verifies version matches pyproject.toml

---

### T18.2: Create Release Prep Command

**Priority:** P1
**Effort:** M
**Type:** feature

#### Description

Add `bpsai-pair release prep` command that verifies release readiness and generates tasks for missing items.

#### Proposed CLI

```bash
bpsai-pair release prep --since v2.6.0

Release Checklist for v2.7.0:
  ✅ Version bumped in pyproject.toml
  ❌ CHANGELOG.md missing v2.7.0 entry
  ❌ Cookie cutter template drift detected
  ⚠️  README.md last updated 2025-12-15
  ✅ Tests passing

Generated tasks:
  - REL-18-01: Update CHANGELOG.md
  - REL-18-02: Sync cookie cutter template
```

#### Checks to Implement

1. Version consistency (pyproject.toml matches __version__)
2. CHANGELOG has entry for current version
3. Cookie cutter template matches source files (use drift detection)
4. Documentation freshness (warn if >7 days old)
5. Test suite passing
6. No uncommitted changes

#### Acceptance Criteria

- [ ] `release prep` command exists
- [ ] Detects version mismatches
- [ ] Detects CHANGELOG gaps
- [ ] Detects cookie cutter drift
- [ ] Generates release tasks automatically
- [ ] `--since` flag for comparison baseline

---

### T18.3: Cookie Cutter Drift Detection CLI

**Priority:** P1
**Effort:** M
**Type:** feature

#### Description

Sprint 17.5's TASK-150 did a one-time audit. Now add ongoing drift detection as a CLI command and CI check.

#### Proposed CLI

```bash
bpsai-pair template check

Cookie Cutter Template Status:
  ✅ config.yaml - Up to date
  ✅ state.md - Up to date
  ⚠️  CLAUDE.md - Minor drift (3 lines changed)
  ✅ ci.yml - Up to date

All critical files in sync.
```

#### CI Integration

```yaml
# .github/workflows/template-check.yml
- name: Check template drift
  run: bpsai-pair template check --fail-on-drift
```

#### Acceptance Criteria

- [ ] `template check` command exists
- [ ] Compares template files to source equivalents
- [ ] Reports drift with actionable messages
- [ ] CI workflow for automated checking
- [ ] `--fail-on-drift` flag for CI enforcement
- [ ] `--fix` flag to auto-sync (with confirmation)

---

### T18.4: Release Engineering Documentation

**Priority:** P2
**Effort:** M
**Type:** chore

#### Description

Document the release process to prevent future release issues.

#### Deliverables

1. `docs/RELEASING.md` - Step-by-step release guide
2. Updated CONTRIBUTING.md with release section
3. Release checklist in `.github/PULL_REQUEST_TEMPLATE.md`

#### Content for RELEASING.md

- Version bump locations (now just pyproject.toml)
- CHANGELOG format and conventions
- How to use `bpsai-pair release prep`
- Cookie cutter sync process (and `template check`)
- CI/CD pipeline overview

#### Acceptance Criteria

- [ ] RELEASING.md created with complete process
- [ ] CONTRIBUTING.md updated with release section
- [ ] PR template includes release checklist for version PRs
- [ ] Examples included for each step

---

## Sprint Totals

| Priority | Count | Effort |
|----------|-------|--------|
| P0 | 1 | S |
| P1 | 2 | M + M |
| P2 | 1 | M |
| **Total** | **4** | ~12 hrs |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Tests pass (`bpsai-pair ci`)
- [ ] `bpsai-pair release prep` shows all green
- [ ] Version bumped to 2.7.0
- [ ] CHANGELOG updated
- [ ] Tagged and released
