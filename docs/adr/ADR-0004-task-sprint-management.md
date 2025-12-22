# ADR 0004 — Task & Sprint Management

**Status:** Accepted
**Date:** 2025-12-22
**Authors:** BPS AI Software Team

---

## Context

Over 18 sprints of PairCoder development, we refined the task and sprint management approach through trial and error. This ADR documents the conventions and lessons learned.

---

## Decision

### Task Naming Conventions

| Format | Example | Use Case |
|--------|---------|----------|
| `T{sprint}.{seq}` | T18.1, T19.3 | **Preferred** for sprint tasks |
| `TASK-{num}` | TASK-150 | Legacy format (still supported) |
| `REL-{sprint}-{seq}` | REL-18-01 | Release-specific tasks |
| `BUG-{num}` | BUG-005 | Bug fixes (optional) |

**Why T{sprint}.{seq}?**
- Clear sprint association at a glance
- No global counter conflicts
- Matches backlog document structure
- Works with Trello card naming

### Plan Types

Only four plan types are valid:

| Type | Use For | Example |
|------|---------|---------|
| `feature` | New functionality | Add workspace filtering |
| `bugfix` | Bug fixes | Fix version mismatch |
| `refactor` | Code improvements | Consolidate Trello modules |
| `chore` | Maintenance, cleanup, docs, releases | Sprint 18 release engineering |

**`maintenance` is NOT valid** — use `chore` instead.

### Sprint Backlog Structure

```markdown
# Sprint N: Title

> **Target Version:** vX.Y.Z
> **Type:** chore | feature | bugfix | refactor
> **Slug:** sprint-n-short-name
> **Focus:** One-line summary

---

## Trello Card Defaults

When syncing to Trello, use these values for ALL cards:

```yaml
Project: PairCoder
Stack: Worker/Function
Repo URL: https://github.com/BPSAI/paircoder
Status: Planning
```

---

## Sprint Goal

2-3 sentences on what this sprint accomplishes.

---

## Backlog Items

### T{N}.1: Task Title

**Priority:** P0 | P1 | P2
**Effort:** S | M | L
**Type:** bugfix | feature | chore | refactor

#### Description
What and why.

#### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---

## Sprint Totals

| Priority | Count | Effort |
|----------|-------|--------|
| P0 | X | ... |
| **Total** | **Y** | ~Z hrs |
```

### Task File Structure

```markdown
---
id: T18.1
plan: plan-2025-12-sprint-18-release-engineering
status: pending
priority: P0
complexity: 25
type: bugfix
depends_on: []
---

# T18.1: Task Title

## Description
What this task accomplishes.

## Implementation Notes
How to implement.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Verification
How to verify completion.
```

### Effort Mapping

| Effort | Complexity | Hours | Description |
|--------|------------|-------|-------------|
| **S** | 0-30 | < 4 hrs | Small task, single focus |
| **M** | 31-60 | 4-8 hrs | Medium task, may touch multiple files |
| **L** | 61-100 | 1+ days | Large task, significant work |

**Note:** Only S, M, L exist in Trello. No XS or XL.

### Sprint Completion Checklist

Before marking a sprint complete:

- [ ] All tasks marked done
- [ ] state.md updated with final status
- [ ] CHANGELOG.md entry added
- [ ] Version bumped in pyproject.toml
- [ ] Cookie cutter template checked for drift
- [ ] Sprint archived to sprint_archive.md

### EPICs (Cross-Sprint Work)

EPICs span multiple sprints. In Trello-native mode:

```
📋 Sprint Planning list
├── Sprint 19 (card)
├── Sprint 20 (card)
├── EPIC-001: Multi-Project Workspace (card)
│   └── 📎 EPIC-001-workspace.md (attachment)
└── EPIC-002: Trello-Native Mode (card)
    └── 📎 EPIC-002-native.md (attachment)
```

EPICs are cards in the Sprint Planning list with:
- Attached specification document
- Checklist of component sprints
- Labels for tracking

---

## Lessons Learned

### Sprint 18 Incident (2025-12-21)

**What happened:** Planning failed due to:
1. CLI attempted invalid Trello custom field values
2. Claude Code ignored task naming convention in backlog
3. Plan type `maintenance` not recognized

**Root causes:**
1. CLI didn't validate against actual board options
2. No reference doc for valid Trello values
3. Backlog template used invalid plan type

**Fixes applied:**
1. `trello fields` command + validation (v2.6.1 hotfix)
2. `bps-board-conventions.md` reference document
3. Updated backlog templates to use valid types

### Key Principles

1. **Always read existing files first** before creating new ones
2. **Use values from reference docs** not assumptions
3. **Naming conventions are in the backlog** — follow them
4. **Trello fields have fixed options** — fetch and validate
5. **state.md must be updated** after every task completion
6. **Sprint backlogs include Trello defaults** section

---

## Consequences

### Positive
- Consistent naming across sprints
- Clear backlog structure
- Validated Trello integration
- Documented lessons prevent repeat failures

### Negative
- More ceremony in backlog creation
- Requires reading reference docs

### Mitigations
- Templates enforce structure
- CLI validation catches errors early
- Reference docs are small and focused

---

## References

- ADR 0002: PairCoder v2 Architecture
- ADR 0003: Trello Integration Architecture
- `.paircoder/context/bps-board-conventions.md`
- `SPRINT-*-BACKLOG.md` templates
