# Sprint 19: Methodology & Session Management

> **Target Version:** v2.8.0
> **Type:** feature
> **Slug:** sprint-19-methodology
> **Focus:** Enforce PairCoder methodology, improve session continuity

---

## Sprint Goal

Make PairCoder methodology enforcement automatic. Prevent context loss during sessions and ensure state.md is always current.

---

## Backlog Items

### T19.1: Mandatory state.md Update Hook

**Priority:** P0
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Block task completion if state.md hasn't been updated. Currently, Claude can mark tasks done without documenting what was accomplished, leading to context loss.

#### Implementation

Add a pre-completion hook that:
1. Checks if state.md was modified since task started
2. Verifies "What Was Just Done" section has new content
3. Blocks completion with helpful message if not updated

#### Hook Logic

```python
def check_state_updated(task_id: str, start_time: datetime) -> bool:
    """Check if state.md was updated since task started."""
    state_path = ".paircoder/context/state.md"
    state_mtime = os.path.getmtime(state_path)
    return state_mtime > start_time.timestamp()
```

#### CLI Behavior

```bash
$ bpsai-pair task update T19.1 --status done

❌ Cannot complete task: state.md not updated since task started.

Please update .paircoder/context/state.md with:
- Mark T19.1 as done in task list
- Add session entry under "What Was Just Done"
- Update "What's Next" section

Then retry: bpsai-pair task update T19.1 --status done
```

#### Bypass Option

```bash
bpsai-pair task update T19.1 --status done --skip-state-check
# Logs warning but allows completion
```

#### Acceptance Criteria

- [ ] Hook fires before task completion
- [ ] Checks state.md modification time
- [ ] Blocks completion with helpful message
- [ ] `--skip-state-check` flag for emergencies
- [ ] Warning logged when bypass used
- [ ] Test covers both paths

---

### T19.2: Session Restart Enforcement

**Priority:** P0
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Detect when a new Claude Code session starts and prompt for state.md read. Prevents Claude from starting work without context.

#### Implementation

Add startup detection that:
1. Checks for session continuity markers
2. If new session detected, prompts to read state.md
3. Logs session start in history

#### Detection Methods

1. **Timestamp gap:** >30 min since last activity
2. **Explicit signal:** `/clear` was run
3. **Session ID change:** Different Claude session ID

#### Startup Message

```
🔄 New session detected. Loading context...

Current state from .paircoder/context/state.md:
- Active plan: sprint-18-release-engineering
- Current task: T18.4 (in_progress)
- Last session: Completed T18.3

Continue with T18.4 or run `bpsai-pair status` for full context?
```

#### Acceptance Criteria

- [ ] Detects new session start
- [ ] Automatically reads state.md
- [ ] Shows current task status
- [ ] Logs session start time
- [ ] Works with Claude Code hooks system

---

### T19.3: Compaction Detection and Recovery

**Priority:** P1
**Effort:** L (6 hrs)
**Type:** feature

#### Description

Detect when Claude's auto-compaction has occurred and restore context from state.md. Compaction loses detailed context, which breaks ongoing work.

#### Detection Methods

1. **Token count drop:** Significant context reduction
2. **Missing file references:** Files previously in context now unknown
3. **Explicit marker:** Check for compaction signal

#### Recovery Flow

```
⚠️ Context compaction detected. Restoring from state.md...

Recovered context:
- Project: PairCoder v2.7.0
- Current task: T19.3 (Compaction Detection)
- Recent changes: hooks.py, lifecycle.py

Note: Some conversation details were compacted.
Run `bpsai-pair pack` to create full context snapshot.
```

#### Integration with /compact

When user runs `/compact`, PairCoder should:
1. Auto-save current state to state.md
2. Create context snapshot
3. Provide recovery instructions

#### Acceptance Criteria

- [ ] Detects compaction event
- [ ] Auto-restores from state.md
- [ ] Shows what context was recovered
- [ ] Integrates with Claude Code `/compact` command
- [ ] Test simulates compaction scenario

---

### T19.4: Token-Aware Batch Planning

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Estimate token usage for a plan and suggest batching if it exceeds comfortable limits. Prevents plans that are too large to complete in one session.

#### Token Estimation

Use existing `token_estimates` config:

```yaml
token_estimates:
  base_context: 15000
  per_complexity_point: 500
  by_task_type:
    feature: 1.2
    bugfix: 0.8
    docs: 0.6
  per_file_touched: 2000
```

#### CLI Output

```bash
$ bpsai-pair plan estimate sprint-19-methodology

Plan Token Estimate:
  Base context:     15,000
  Tasks (8):        40,000  (avg 5,000 per task)
  Files touched:    16,000  (8 files × 2,000)
  ─────────────────────────
  Total estimate:   71,000 tokens

⚠️ This plan may exceed comfortable session limits.

Recommendations:
  1. Split into 2 batches (T19.1-T19.4, T19.5-T19.8)
  2. Use intermediate commits for recovery points
  3. Update state.md frequently
```

#### Acceptance Criteria

- [ ] `plan estimate` command exists
- [ ] Uses existing token_estimates config
- [ ] Warns when plan exceeds threshold
- [ ] Suggests batching strategy
- [ ] Factors in task types and complexity

---

### T19.5: Sprint Completion with Release Integration

**Priority:** P2
**Effort:** M (3 hrs)
**Type:** feature
**Source:** ENH-006

#### Description

Enhance `bpsai-pair sprint complete` to enforce release checklist and optionally trigger `release prep`.

#### Proposed Flow

```bash
$ bpsai-pair sprint complete sprint-18

Sprint 18 Summary:
  Tasks: 7/7 complete (45 points)
  
Pre-completion checklist:
  [?] Run release prep? (Recommended after feature sprints)

Running release prep...
  ❌ CHANGELOG.md needs update
  ❌ Cookie cutter drift detected

Cannot complete sprint with release issues.
Fix issues or use --force to skip.
```

#### Acceptance Criteria

- [ ] Sprint complete prompts for release prep
- [ ] Blocks completion if release issues found (unless --force)
- [ ] Archives sprint tasks after successful completion
- [ ] Updates state.md automatically
- [ ] Generates sprint summary report

---

### T19.6: Skill Validator CLI

**Priority:** P2
**Effort:** M (4 hrs)
**Type:** feature
**Source:** TASK-116 (from original roadmap)

#### Description

Add `bpsai-pair skill validate` command to check skill format against Anthropic specs.

#### Validations

1. **Frontmatter:** Only `name` and `description` fields
2. **Description:** Under 1024 characters, third-person voice
3. **File size:** SKILL.md under 500 lines
4. **Naming:** Lowercase, hyphens, gerund form preferred
5. **Structure:** Required sections present

#### CLI Output

```bash
$ bpsai-pair skill validate

Validating 8 skills...

✅ paircoder-task-lifecycle
✅ trello-aware-planning
⚠️  code-review
   - Name should use gerund form: "reviewing-code"
   - Description uses 2nd person ("Use when...")
✅ design-plan-implement
...

Summary: 6 pass, 2 warnings, 0 errors
```

#### Acceptance Criteria

- [ ] `skill validate` command exists
- [ ] Validates all skills in .claude/skills/
- [ ] Checks frontmatter fields
- [ ] Checks description length and voice
- [ ] Checks file size
- [ ] Reports warnings vs errors
- [ ] `--fix` flag for auto-corrections

---

### T19.7: Merge trello-task-workflow into paircoder-task-lifecycle

**Priority:** P3
**Effort:** S (2 hrs)
**Type:** chore
**Source:** BACKLOG-005 (from skills optimization)

#### Description

`trello-task-workflow` has 80% overlap with `paircoder-task-lifecycle`. Consolidate into one skill with a "Trello-Specific" section.

#### Implementation

1. Add "Trello-Specific Commands" section to `paircoder-task-lifecycle`
2. Move unique content from `trello-task-workflow`
3. Delete `trello-task-workflow` skill
4. Keep `trello-aware-planning` separate (different purpose: creating plans vs executing tasks)

#### Acceptance Criteria

- [ ] `paircoder-task-lifecycle` has Trello section
- [ ] All unique trello-task-workflow content preserved
- [ ] `trello-task-workflow` skill deleted
- [ ] `trello-aware-planning` unchanged
- [ ] No broken references

---

### T19.8: Document Built-in Slash Commands

**Priority:** P2
**Effort:** S (1 hr)
**Type:** docs

#### Description

Document Claude Code's 37 built-in commands and how PairCoder integrates with them.

#### Deliverable

Add section to docs/USER_GUIDE.md or create docs/CLAUDE_CODE_INTEGRATION.md:

- List of built-in commands we leverage
- Commands to avoid conflicting with
- How PairCoder commands complement built-ins
- Best practices for combined usage

#### Key Commands to Document

| Command | Integration |
|---------|-------------|
| `/compact` | Use before large tasks; triggers state save |
| `/context` | Check token budget |
| `/plan` | Use built-in for session planning (we use `/pc-plan` for backlog) |
| `/sandbox` | Use for security-sensitive execution |
| `/todos` | Future: could sync with task system |

#### Acceptance Criteria

- [ ] Documentation created
- [ ] All 37 built-in commands listed
- [ ] PairCoder integration notes for relevant commands
- [ ] Added to skill reference docs

---

## Sprint Totals

| Priority | Count | Effort |
|----------|-------|--------|
| P0 | 2 | M + M |
| P1 | 2 | L + M |
| P2 | 3 | M + M + S |
| P3 | 1 | S |
| **Total** | **8** | ~28-32 hrs |

---

## Dependencies

| Task | Depends On |
|------|------------|
| T19.5 | T18.4 (release prep command) |
| T19.6 | Sprint 18 complete |
| T19.7 | T19.6 (skill validator to verify after merge) |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Tests pass
- [ ] state.md enforcement working
- [ ] Session continuity improved
- [ ] Version bumped to 2.8.0
