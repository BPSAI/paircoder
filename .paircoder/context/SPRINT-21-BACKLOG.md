# Sprint 21: Emergent Skill Discovery

> **Target Version:** v2.10.0
> **Type:** feature
> **Slug:** sprint-21-emergent-skills
> **Focus:** AI-driven skill creation, gap detection, and quality scoring

---

## Sprint Goal

Enable PairCoder to learn from usage patterns and suggest or create new skills automatically. Transform from a static skill system to an evolving capability platform.

**Note:** Sprint 17.5 already completed:
- Trello board from template (TASK-159)
- Preset-specific CI workflows (TASK-163)
- Slash commands documentation (TASK-164)

---

## Backlog Items

### T21.1: /update-skills Slash Command

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Create a slash command that analyzes recent conversation patterns and suggests skill updates or new skills.

#### Implementation

```markdown
# .claude/commands/update-skills.md
---
description: Analyze recent conversations and suggest skill improvements
allowed-tools: Bash(bpsai-pair skill:*)
---

Analyze the current conversation for:
1. Repeated workflows not captured in existing skills
2. Commands or patterns used frequently
3. Gaps where a skill would have helped

Then:
1. Run `bpsai-pair skill suggest` to get AI recommendations
2. Present suggestions to user
3. If approved, create skill draft with `bpsai-pair skill create`
```

#### CLI Support

```bash
# Analyze conversation for skill opportunities
bpsai-pair skill suggest

Analyzing recent patterns...

Suggested Skills:
1. "debugging-python-tests" (confidence: 85%)
   - Pattern: pytest failures → read traceback → fix → rerun
   - Would save: ~5 min per debug cycle

2. "reviewing-pull-requests" (confidence: 72%)
   - Pattern: checkout PR → review files → add comments
   - Note: Overlaps with existing code-review skill

Create skill draft? [1/2/skip]:
```

#### Acceptance Criteria

- [ ] `/update-skills` command exists
- [ ] Analyzes conversation for patterns
- [ ] Suggests new skills with confidence scores
- [ ] Can create skill drafts from suggestions
- [ ] Integrates with skill validator

---

### T21.2: Skill Gap Detection

**Priority:** P1
**Effort:** L (6 hrs)
**Type:** feature

#### Description

Detect when user needs a skill that doesn't exist. Monitor for repeated manual workflows and suggest skill creation.

#### Detection Signals

1. **Repeated commands:** Same sequence of commands run multiple times
2. **Repeated questions:** User asks similar clarifying questions
3. **Manual workarounds:** User describes process that could be automated
4. **Error patterns:** Same type of error handled the same way

#### Implementation

```python
class SkillGapDetector:
    def analyze_session(self, session_log: List[Message]) -> List[SkillGap]:
        """Detect potential skill gaps from session."""
        patterns = self.extract_patterns(session_log)
        gaps = []
        for pattern in patterns:
            if pattern.frequency >= 3 and not self.has_matching_skill(pattern):
                gaps.append(SkillGap(
                    pattern=pattern,
                    suggested_name=self.generate_name(pattern),
                    confidence=pattern.frequency / 10,
                ))
        return gaps
```

#### User Notification

```
💡 Skill Gap Detected

You've performed this workflow 4 times this session:
  1. Read error log
  2. Search codebase for error string
  3. Find related test
  4. Run test in isolation

Would you like to create a "debugging-from-logs" skill? [y/n]
```

#### Acceptance Criteria

- [ ] Detects repeated command sequences
- [ ] Identifies manual workarounds
- [ ] Calculates confidence score
- [ ] Notifies user of detected gaps
- [ ] Integrates with skill creation flow

---

### T21.3: Auto-Skill Creation

**Priority:** P2
**Effort:** L (6 hrs)
**Type:** feature

#### Description

Generate skill drafts automatically from detected gaps, requiring only user approval and minor edits.

#### Generation Process

1. Analyze detected pattern
2. Extract key commands and decision points
3. Generate SKILL.md structure
4. Populate with observed steps
5. Add placeholders for user customization
6. Validate against skill spec

#### Generated Skill Example

```markdown
---
name: debugging-from-logs
description: Guides systematic debugging workflow starting from error logs.
  Covers log analysis, codebase search, test isolation, and fix verification.
---

# Debugging from Logs

## Trigger
Use when you see an error in logs and need to trace to root cause.

## Workflow

### 1. Analyze Error
Read the error log and identify:
- Error type/message
- Stack trace location
- Timestamp and context

### 2. Search Codebase
\`\`\`bash
grep -rn "error_string" src/
\`\`\`

### 3. Find Related Tests
[Auto-detected pattern: user usually runs related test]

### 4. Isolate and Fix
[Placeholder: Add your debugging approach]

---
*Auto-generated from session patterns. Please review and customize.*
```

#### Acceptance Criteria

- [ ] Generates valid SKILL.md from patterns
- [ ] Includes observed commands
- [ ] Marks placeholders for customization
- [ ] Passes skill validator
- [ ] `--auto-approve` flag for trusted generation

---

### T21.4: Skill Quality Scoring

**Priority:** P2
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Score skills on multiple quality dimensions to identify improvement opportunities and rank for discovery.

#### Quality Dimensions

| Dimension | Weight | Measurement |
|-----------|--------|-------------|
| Token Efficiency | 25% | Lines / information density |
| Trigger Clarity | 20% | How clear is when to use |
| Completeness | 20% | Covers full workflow |
| Usage Frequency | 20% | How often invoked |
| User Satisfaction | 15% | Thumbs up/down on skill use |

#### CLI Output

```bash
$ bpsai-pair skill score

Skill Quality Report:

| Skill | Score | Token Eff | Triggers | Complete | Usage |
|-------|-------|-----------|----------|----------|-------|
| managing-task-lifecycle | 92 | 95 | 90 | 88 | 95 |
| planning-with-trello | 87 | 80 | 92 | 90 | 85 |
| implementing-with-tdd | 78 | 70 | 85 | 82 | 75 |
| debugging-from-logs | 65 | 60 | 70 | 65 | - |

Recommendations:
- implementing-with-tdd: Consider splitting into smaller skills
- debugging-from-logs: Add more trigger examples
```

#### Acceptance Criteria

- [ ] `skill score` command exists
- [ ] Scores all skills on defined dimensions
- [ ] Generates improvement recommendations
- [ ] Tracks usage frequency over time
- [ ] Exportable report format

---

### T21.5: Skill Marketplace Foundation

**Priority:** P3
**Effort:** L (8 hrs)
**Type:** feature

#### Description

Enable sharing skills across projects and teams. Foundation for future public marketplace.

#### Components

1. **Skill Registry:** Central index of available skills
2. **Skill Packaging:** Bundle skill with metadata
3. **Skill Publishing:** Push to registry
4. **Skill Discovery:** Search and browse

#### Registry Structure

```yaml
# ~/.paircoder/skill-registry.yaml
registries:
  - name: local
    url: file://~/.paircoder/skills/
  - name: team
    url: https://github.com/bpsai/paircoder-skills
  - name: community
    url: https://skills.paircoder.dev  # Future

installed:
  - name: security-audit
    source: team
    version: 1.2.0
  - name: api-design
    source: community
    version: 2.0.1
```

#### CLI Commands

```bash
# Search registry
bpsai-pair skill search "security"

# Install from registry
bpsai-pair skill install @team/security-audit

# Publish to registry
bpsai-pair skill publish my-skill --registry team

# List installed
bpsai-pair skill list --source all
```

#### Acceptance Criteria

- [ ] Local registry working
- [ ] Team (git-based) registry working
- [ ] Skill packaging with metadata
- [ ] `skill search` command
- [ ] `skill publish` command
- [ ] Version tracking

---

## Sprint Totals

| Priority | Count | Effort |
|----------|-------|--------|
| P1 | 2 | M + L |
| P2 | 2 | L + M |
| P3 | 1 | L |
| **Total** | **5** | ~28-32 hrs |

---

## Dependencies

| Task | Depends On |
|------|------------|
| T21.1 | T20.3 (skill-creation skill) |
| T21.3 | T21.2 (gap detection provides patterns) |
| T21.4 | T19.5 (skill validator for quality checks) |
| T21.5 | T20.4 (skill installer as foundation) |

---

## Post-Sprint: EPIC-001

After Sprint 21, the next major initiative is **EPIC-001: Multi-Project Workspace Support** (estimated Sprints 22-23).

EPIC-001 depends on:
- T19.1 (hooks system) for workspace hooks
- T20.3 (skill-creation) for workspace-aware skill

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Skill gap detection working
- [ ] Auto-skill creation functional
- [ ] Marketplace foundation operational
- [ ] Version bumped to 2.10.0
- [ ] Ready for EPIC-001
