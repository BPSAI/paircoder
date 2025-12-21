# PairCoder Roadmap: Sprints 18-21

> **Version:** 2.7.0 Target
> **Created:** 2025-12-21
> **Task Naming Convention:** `T{sprint}.{sequence}` (e.g., T18.1, T18.2)

---

## Task Naming Convention Change

**Effective Sprint 18**, we adopt a new task naming convention:

| Format | Example | Usage |
|--------|---------|-------|
| `T{sprint}.{seq}` | `T18.1` | Sprint tasks |
| `REL-{sprint}-{seq}` | `REL-18-01` | Release engineering tasks |
| `BUG-{num}` | `BUG-005` | Bug fixes (categorical, sprint-agnostic) |

**Rationale:**
- Clear sprint context at a glance
- Avoids conflicts with existing TASK-XXX in Trello (backlog uses 150+)
- Shorter, easier to type/reference
- Coexists with legacy `TASK-XXX` format

**Tooling Update Required (T18.1):**
- Regex: `TASK-\d+` → `(TASK-\d+|T\d+\.\d+|REL-\d+-\d+|BUG-\d+)`
- Trello card format: `[T18.1] Title`

---

## Sprint 17.5: Bug Fixes & Production Hardening (Current)

**Status:** In Progress
**Focus:** Fix all issues found during production testing before moving forward

### Completed ✅
- Skills optimization against Anthropic specs
- Frontmatter cleanup (removed invalid fields)
- Token efficiency improvements (50-80% reduction)
- CLI integration in skills
- Hook documentation in skills

### Remaining
- Production bug fixes from React SDK deployment
- Quick wins from PAIRCODER-BACKLOG.md

---

## Sprint 0: Pre-Sprint 18 Transition

**Status:** Pending (after Sprint 17.5)
**Duration:** ~1 hour
**Focus:** Prepare tooling for new task naming convention

### Tasks (handled by Transition Prompt)

| Task | Description | Status |
|------|-------------|--------|
| Update task ID regex | Support `T{sprint}.{seq}` alongside `TASK-XXX` | ⏳ |
| Rename `/plan` → `/pc-plan` | Avoid Claude Code built-in conflict | ⏳ |

See **Appendix A** for the complete transition prompt.

---

## Sprint 18: Release Engineering Foundation

**Target Version:** v2.6.1 → v2.7.0
**Duration:** 1 sprint
**Focus:** Automate releases, fix cookie cutter drift, resolve critical bugs

### Tasks

| ID | Title | Type | Priority | Effort | Description |
|----|-------|------|----------|--------|-------------|
| T18.1 | Fix version string single source | Bug | P0 | XS | Use `importlib.metadata` to read version from pyproject.toml (BUG-004) |
| T18.2 | Fix plan list task count | Bug | P1 | S | `plan list` shows "Tasks: 0" even when tasks exist (BUG-001) |
| T18.3 | Fix depends_on attribute | Bug | P1 | S | Task model missing `depends_on` breaks hook (BUG-003) |
| T18.4 | Create `release prep` command | Feature | P1 | M | Verify release readiness, generate tasks for missing items (ENH-005) |
| T18.5 | Cookie cutter drift detection | Feature | P1 | M | `template check` command + CI workflow (ENH-007) |
| T18.6 | Full cookie cutter audit | Chore | P1 | L | Audit all template files against current paircoder (REVIEW-001) |
| T18.7 | Release engineering docs | Docs | P2 | M | Create RELEASING.md, update CONTRIBUTING.md (DOC-005) |

### Acceptance Criteria
- [ ] `bpsai-pair --version` shows correct version
- [ ] `bpsai-pair plan list` shows accurate task counts
- [ ] `bpsai-pair release prep` exists and runs
- [ ] `bpsai-pair template check` detects drift
- [ ] Cookie cutter templates match source files
- [ ] RELEASING.md exists with complete process

### Sprint Deliverable
**v2.7.0 Release** with stable release engineering

---

## Sprint 19: Methodology & Session Management

**Target Version:** v2.8.0
**Duration:** 1 sprint
**Focus:** Enforce PairCoder methodology, improve session continuity

### Tasks

| ID | Title | Type | Priority | Effort | Description |
|----|-------|------|----------|--------|-------------|
| T19.1 | Mandatory state.md update hook | Feature | P0 | M | Block task completion if state.md not updated |
| T19.2 | Session restart enforcement | Feature | P0 | M | Detect new sessions, prompt for state.md read |
| T19.3 | Compaction detection/recovery | Feature | P1 | L | Detect auto-compaction, restore from state.md |
| T19.4 | Token-aware batch planning | Feature | P1 | M | Estimate tokens for plan, suggest batching |
| T19.5 | Sprint completion with release | Feature | P2 | M | `sprint complete` triggers `release prep` (ENH-006) |
| T19.6 | Skill validator CLI | Feature | P2 | M | `bpsai-pair skill validate` checks skill format (TASK-116) |
| T19.7 | Merge trello-task-workflow skill | Chore | P3 | S | Consolidate into paircoder-task-lifecycle |
| T19.8 | Document built-in slash commands | Docs | P2 | S | Reference Claude Code's 37 built-in commands |

### Acceptance Criteria
- [ ] Cannot complete task without state.md update
- [ ] New sessions prompt for context loading
- [ ] Compaction is detected and handled gracefully
- [ ] `bpsai-pair skill validate` exists

---

## Sprint 20: Cross-Platform Skills

**Target Version:** v2.9.0
**Duration:** 1 sprint
**Focus:** Make skills portable, improve skill creation

### Tasks

| ID | Title | Type | Priority | Effort | Description |
|----|-------|------|----------|--------|-------------|
| T20.1 | Skill naming convention update | Chore | P2 | S | Rename to gerund form (e.g., `reviewing-code`) |
| T20.2 | Third-person voice in descriptions | Chore | P2 | S | Update all skill descriptions to third-person |
| T20.3 | Create skill-creation skill | Feature | P1 | M | Skill that teaches how to create skills (TASK-119) |
| T20.4 | Skill installer command | Feature | P1 | M | `bpsai-pair skill install <url>` |
| T20.5 | Cross-platform skill structure | Feature | P2 | L | Make skills work in Claude Code + other IDEs |
| T20.6 | Preset validation command | Feature | P3 | M | `config validate` + `config update --preset` (ENH-003) |
| T20.7 | Trello custom fields CLI | Feature | P2 | M | `trello set-field`, `trello apply-defaults` (ENH-004) |
| T20.8 | Document Trello board conventions | Docs | P1 | S | Protected cards, custom fields, PR workflow (DOC-004) |

### Acceptance Criteria
- [ ] All skills use gerund naming
- [ ] skill-creation skill exists
- [ ] `bpsai-pair skill install` works
- [ ] Skills are cross-platform compatible

---

## Sprint 21: Emergent Skill Discovery

**Target Version:** v2.10.0
**Duration:** 1 sprint
**Focus:** AI-driven skill creation and discovery

### Tasks

| ID | Title | Type | Priority | Effort | Description |
|----|-------|------|----------|--------|-------------|
| T21.1 | /update-skills slash command | Feature | P1 | M | Update skills based on conversation patterns (TASK-131) |
| T21.2 | Skill gap detection | Feature | P1 | L | Detect when user needs skill that doesn't exist |
| T21.3 | Auto-skill creation | Feature | P2 | L | Generate skill drafts from detected gaps |
| T21.4 | Skill quality scoring | Feature | P2 | M | Score skills on token efficiency, relevance |
| T21.5 | Skill marketplace foundation | Feature | P3 | L | Share skills across projects/teams |
| T21.6 | Trello board from template | Feature | P2 | M | `trello init-board --from-template` (ENH-001) |
| T21.7 | Preset-specific CI workflows | Feature | P3 | M | React preset = Node CI only (MISSING-003) |
| T21.8 | Slash commands documentation | Docs | P3 | S | Document .claude/commands/ feature (DOC-001) |

### Acceptance Criteria
- [ ] `/update-skills` command works
- [ ] Gap detection suggests missing skills
- [ ] Skills can be scored and ranked
- [ ] Trello board can be created from template

---

## Dependency Graph

```
Sprint 17.5 (current)
    │
    ▼
Sprint 0: Transition ────────────── Regex update + /pc-plan rename
    │
    ▼
Sprint 18: Release Engineering ──┬── T18.1-T18.3 (bug fixes)
                                 ├── T18.4-T18.5 (release automation)
                                 └── T18.6-T18.7 (docs + audit)
    │
    ▼
Sprint 19: Methodology ──────────┬── T19.1-T19.3 (session enforcement)
                                 ├── T19.4 (token planning)
                                 └── T19.6 (skill validator) ─→ enables T20.x
    │
    ▼
Sprint 20: Cross-Platform ───────┬── T20.1-T20.2 (naming + voice)
                                 ├── T20.3-T20.4 (skill creation)
                                 └── T20.5 (cross-platform) ─→ enables T21.5
    │
    ▼
Sprint 21: Emergent Skills ──────┬── T21.1-T21.3 (discovery + creation)
                                 └── T21.4-T21.5 (quality + marketplace)
    │
    ▼
EPIC-001: Multi-Project Workspace (Sprints 22-23)
```

---

## Claude Code Integration Notes

### Built-in Commands We Leverage

| Claude Code Command | PairCoder Integration |
|--------------------|----------------------|
| `/compact` | Reference in skills for context management |
| `/context` | Check before large tasks |
| `/review` | Use built-in (we renamed ours to `/pc-review`) |
| `/sandbox` | Use for security-sensitive execution |
| `/security-review` | Complements our security agent |
| `/todos` | Could sync with our task system (future) |

### PairCoder Slash Commands (No Conflicts)

| Command | Purpose | Status |
|---------|---------|--------|
| `/plan` | Create/show plans | ✅ No conflict |
| `/task` | Manage tasks | ✅ No conflict |
| `/flow` | Run workflows | ✅ No conflict |
| `/sprint` | Sprint operations | ✅ No conflict |
| `/pc-review` | PairCoder code review | ✅ Renamed from `/review` |

---

## Version Milestones

| Version | Sprint | Key Features |
|---------|--------|--------------|
| v2.6.1 | 17.5 | Bug fixes, skills optimization |
| v2.7.0 | 18 | Release automation, template sync |
| v2.8.0 | 19 | Session enforcement, methodology |
| v2.9.0 | 20 | Cross-platform skills, installer |
| v2.10.0 | 21 | Emergent skill discovery |

---

## Migration Notes

### From TASK-XXX to T{sprint}.{seq}

1. **Legacy tasks remain unchanged** - Don't renumber existing TASK-XXX
2. **New tasks use new format** - Starting Sprint 18
3. **Trello coexistence** - Both formats work, no data loss
4. **Gradual tooling update** - T18.1 adds support, no breaking change

### Task ID Regex Update (T18.1)

**Before:**
```python
TASK_PATTERN = r"TASK-(\d+)"
```

**After:**
```python
TASK_PATTERN = r"(TASK-\d+|T\d+\.\d+|REL-\d+-\d+|BUG-\d+)"
```

---

## Backlog Items (Post-Sprint 21)

These items are tracked but not yet scheduled:

| ID | Description | Source |
|----|-------------|--------|
| MISSING-001 | /commands directory in cookie cutter | BACKLOG |
| MISSING-004 | docs/ vs .paircoder/docs/ confusion | BACKLOG |
| BUG-002 | project_tree.yml wrong path | BACKLOG |
| DOC-002 | Trello setup in quick start | BACKLOG |
| DOC-003 | Clarify task update vs ttask | BACKLOG |

---

## Appendix A: Sprint 0 Transition Prompt

Use this prompt with Claude Code **after Sprint 17.5, before Sprint 18**:

```markdown
## Pre-Sprint 18 Transition Tasks

Two things to complete before starting Sprint 18 proper:

### 1. Update Task ID Regex Patterns

Starting Sprint 18, PairCoder uses a new task naming convention:
- Sprint tasks: T18.1, T18.2 (format: T{sprint}.{seq})
- Release tasks: REL-18-01 (format: REL-{sprint}-{seq})
- Bugs: BUG-005 (format: BUG-{num})

**Requirements:**
1. Update all regex patterns that match task IDs to support BOTH old and new formats
2. Old format: TASK-123, TASK-456
3. New formats: T18.1, T19.5, REL-18-01, BUG-007

**Files to Search:**
```bash
grep -rn "TASK-" tools/cli/bpsai_pair/
```

**New Combined Pattern:**
```python
TASK_PATTERN = r"(TASK-\d+|T\d+\.\d+|REL-\d+-\d+|BUG-\d+)"
```

**Files likely needing updates:**
- tools/cli/bpsai_pair/planning/task_parser.py
- tools/cli/bpsai_pair/tasks/lifecycle.py
- tools/cli/bpsai_pair/hooks.py
- tools/cli/bpsai_pair/trello/sync.py (if task IDs in card titles)

**Acceptance Criteria:**
- [ ] All existing TASK-xxx references still work
- [ ] New T18.x format is recognized
- [ ] REL-xx-xx format is recognized  
- [ ] BUG-xxx format is recognized
- [ ] Tests pass
- [ ] Trello sync works with new format

### 2. Rename /plan Slash Command to /pc-plan

The `/plan` command conflicts with Claude Code's built-in `/plan` command (added in v2.0.75+).

**Rename:**
```bash
mv .claude/commands/plan.md .claude/commands/pc-plan.md
```

**Update any references:**
- CLAUDE.md (if mentioned)
- .claude/skills/ (if any skill references /plan)
- docs/USER_GUIDE.md (if documented)
- README.md (if documented)

**Acceptance Criteria:**
- [ ] .claude/commands/pc-plan.md exists
- [ ] .claude/commands/plan.md deleted
- [ ] /pc-plan shows in Claude Code autocomplete
- [ ] No references to old /plan command remain
- [ ] Test: typing `/pc-plan backlog.md` works as expected

### Verification

After completing both tasks:
```bash
# Test regex
bpsai-pair task list  # Should work with existing TASK-xxx
# Create a test task with new format and verify it's recognized

# Test slash command
# In Claude Code, type /pc- and verify pc-plan shows up
```

### Update state.md

Add session entry:
```markdown
## Session: Sprint 0 - Transition Complete

**What Was Done:**
- Updated task ID regex to support T{sprint}.{seq} format
- Renamed /plan → /pc-plan to avoid Claude Code built-in conflict
- Verified backward compatibility with TASK-xxx format

**What's Next:**
- Begin Sprint 18: T18.1 (Fix version string single source)
```
```

---

## Appendix B: EPIC-001 Compatibility Notes

The **Multi-Project Workspace Support** epic (EPIC-001) is planned for post-Sprint 21.

### Task Naming for Epic

Epic tasks use format `TASK-W{nn}` (e.g., TASK-W01, TASK-W15) to distinguish from sprint tasks.

### Dependencies on Sprint 18-21

| Epic Task | Depends On | Notes |
|-----------|------------|-------|
| TASK-W11 (Workspace Hooks) | T19.1 | Build on enhanced hook system |
| TASK-W12 (workspace-aware skill) | T20.1-T20.5 | Follow skill conventions |

### Timeline

| Phase | Sprints | Focus |
|-------|---------|-------|
| Foundation | 18-21 | Release engineering, methodology, skills |
| Epic | 22-23 (est.) | Multi-project workspace support |

---

## Appendix C: Claude Code Built-in Commands Reference

Commands to leverage (not conflict with):

| Command | Purpose | PairCoder Integration |
|---------|---------|----------------------|
| `/compact` | Compress context | Reference in skills for context management |
| `/context` | Show token usage | Use before large tasks |
| `/plan` | Session planning | **We use /pc-plan instead** |
| `/review` | Code review | Use built-in (complements our skills) |
| `/sandbox` | Isolated execution | Use for security-sensitive tasks |
| `/security-review` | Security check | Complements security agent |
| `/todos` | List todos | Future: sync with task system |
| `/hooks` | Manage hooks | Complements our hooks.py |

Full list: 37 built-in commands as of v2.0.75
