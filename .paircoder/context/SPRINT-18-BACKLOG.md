# Sprint 18: Release Engineering Foundation

> **Target Version:** v2.7.0
> **Type:** maintenance
> **Slug:** sprint-18-release-engineering
> **Focus:** Automate releases, fix cookie cutter drift, resolve critical bugs

---

## Sprint Goal

Establish automated release engineering processes to prevent version mismatches, stale templates, and missing documentation that plagued the v2.6.0 release.

---

## Backlog Items

### T18.1: Fix Version String Single Source of Truth

**Priority:** P0
**Effort:** XS (15 min)
**Type:** bugfix
**Source:** BUG-004

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
- [ ] No hardcoded version strings remain
- [ ] Test verifies version matches pyproject.toml

---

### T18.2: Fix Plan List Task Count

**Priority:** P1
**Effort:** S (1 hr)
**Type:** bugfix
**Source:** BUG-001

#### Description

`bpsai-pair plan list` shows "Tasks: 0" even when tasks exist for the plan.

#### Observed Behavior

```
┃ ID                            ┃ Title              ┃ Tasks ┃
│ plan-2025-12-react-sdk-phase1 │ React SDK Phase 1  │     0 │
```

But `bpsai-pair task list` shows 14 tasks with that plan_id.

#### Root Cause

Plan list command doesn't query TaskParser for associated tasks. Task count likely hardcoded or not computed.

#### Fix Location

`tools/cli/bpsai_pair/planning/cli_commands.py` - plan list command

#### Acceptance Criteria

- [ ] Plan list shows accurate task count
- [ ] Count derived from tasks with matching plan_id
- [ ] Test covers plan with tasks and plan without tasks

---

### T18.3: Fix depends_on Attribute Missing

**Priority:** P1
**Effort:** S (1 hr)
**Type:** bugfix
**Source:** BUG-003

#### Description

The `check_unblocked` hook fails with `'Task' object has no attribute 'depends_on'` when completing tasks.

#### Error Observed

```
✅ Updated T2.3 -> done
Unblock check failed: 'Task' object has no attribute 'depends_on'
```

#### Root Cause

1. Task model in `planning/models.py` may not have `depends_on` field
2. Task files don't include `depends_on: []`
3. Hook assumes field exists without checking

#### Implementation Options

1. Add `depends_on: List[str] = []` to Task model with default
2. Update hook to handle missing attribute gracefully
3. Update task template to always include `depends_on: []`

#### Fix Locations

- `tools/cli/bpsai_pair/planning/models.py` - Task dataclass
- `tools/cli/bpsai_pair/hooks.py` - check_unblocked handler
- Cookie cutter task templates

#### Acceptance Criteria

- [ ] Task model has `depends_on` field with default empty list
- [ ] Hook handles missing attribute gracefully
- [ ] New tasks created with `depends_on: []` by default
- [ ] Existing tasks without field don't cause errors
- [ ] Test covers task completion with and without depends_on

---

### T18.4: Create Release Prep Command

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature
**Source:** ENH-005

#### Description

Add `bpsai-pair release prep` command that verifies release readiness and generates tasks for missing items.

#### Proposed CLI

```bash
bpsai-pair release prep --since v2.5.4

Release Checklist for v2.7.0:
  ✅ Version bumped in pyproject.toml
  ❌ CHANGELOG.md missing v2.7.0 entry
  ❌ Cookie cutter config.yaml drift detected
  ⚠️  README.md last updated 2025-12-15
  ✅ Tests passing

Generated tasks:
  - REL-18-01: Update CHANGELOG.md
  - REL-18-02: Sync cookie cutter template
```

#### Checks to Implement

1. Version consistency (pyproject.toml matches __version__)
2. CHANGELOG has entry for current version
3. Cookie cutter template matches source files
4. Documentation freshness (warn if >7 days old)
5. Test suite passing
6. No uncommitted changes

#### Config Section

```yaml
release:
  version_source: pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
    - docs/FEATURE_MATRIX.md
  cookie_cutter:
    template_path: tools/cli/bpsai_pair/data/cookiecutter-paircoder
    sync_required: true
```

#### Acceptance Criteria

- [ ] `release prep` command exists
- [ ] Detects version mismatches
- [ ] Detects CHANGELOG gaps
- [ ] Detects cookie cutter drift
- [ ] Generates release tasks automatically
- [ ] Config section for customization
- [ ] `--since` flag for comparison baseline

---

### T18.5: Cookie Cutter Drift Detection

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature
**Source:** ENH-007

#### Description

Add CI check and CLI command to detect when cookie cutter templates have drifted from their source files.

#### Proposed CLI

```bash
bpsai-pair template check

Cookie Cutter Template Status:
  ❌ config.yaml - Missing: trello, estimation, security sections
  ❌ state.md - Format outdated (missing session tracking)
  ⚠️  ci.yml - Contains both Node and Python (consider preset-specific)
  ✅ CLAUDE.md - Up to date
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

### T18.6: Full Cookie Cutter Audit

**Priority:** P1
**Effort:** L (8 hrs)
**Type:** chore
**Source:** REVIEW-001

#### Description

Multiple template files in the cookie cutter are outdated. Full audit and sync required.

#### Affected Files (Confirmed Stale)

- `.paircoder/context/state.md` - Old format, missing session tracking
- `.paircoder/context/project.md` - Generic, not project-type specific
- `.paircoder/context/workflow.md` - Needs review
- `CODEOWNERS` - Generic placeholders
- `.github/workflows/ci.yml` - Too generic (both Node + Python)
- `.github/workflows/project_tree.yml` - Wrong output path (BUG-002)

#### Implementation

1. Full audit of all template files against current paircoder equivalents
2. Update all stale files to current format
3. Document which files are preset-specific vs universal
4. Create mapping file for future drift detection

#### Acceptance Criteria

- [ ] All template files audited against paircoder source
- [ ] state.md template matches current format
- [ ] project.md template is useful (or preset-specific)
- [ ] workflow.md template is current
- [ ] CI workflows are preset-appropriate
- [ ] CODEOWNERS has clear placeholders
- [ ] project_tree.yml outputs to correct path
- [ ] Audit results documented

---

### T18.7: Release Engineering Documentation

**Priority:** P2
**Effort:** M (3 hrs)
**Type:** docs
**Source:** DOC-005

#### Description

Document the release process to prevent future release issues.

#### Deliverables

1. `docs/RELEASING.md` - Step-by-step release guide
2. Updated CONTRIBUTING.md with release section
3. Release checklist in `.github/PULL_REQUEST_TEMPLATE.md`

#### Content for RELEASING.md

- Version bump locations (now just pyproject.toml)
- CHANGELOG format and conventions
- Cookie cutter sync process
- Release checklist
- How to use `bpsai-pair release prep`
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
| P0 | 1 | XS |
| P1 | 5 | S + S + M + M + L |
| P2 | 1 | M |
| **Total** | **7** | ~20-24 hrs |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Tests pass (`bpsai-pair ci`)
- [ ] Documentation updated
- [ ] `bpsai-pair release prep` shows all green
- [ ] Version bumped to 2.7.0
- [ ] CHANGELOG updated
- [ ] Tagged and released
