# Sprint 20: Cross-Platform Skills

> **Target Version:** v2.9.0
> **Type:** feature
> **Slug:** sprint-20-cross-platform-skills
> **Focus:** Make skills portable, improve skill creation and installation

---

## Sprint Goal

Establish PairCoder as a skill platform. Skills should be easy to create, share, and install across projects and platforms.

---

## Backlog Items

### T20.1: Skill Naming Convention Update

**Priority:** P2
**Effort:** S (2 hrs)
**Type:** chore

#### Description

Rename existing skills to follow Anthropic's recommended gerund form naming convention.

#### Current → New Names

| Current | New |
|---------|-----|
| `code-review` | `reviewing-code` |
| `design-plan-implement` | `designing-and-implementing` |
| `finish-branch` | `finishing-branches` |
| `tdd-implement` | `implementing-with-tdd` |
| `paircoder-task-lifecycle` | `managing-task-lifecycle` |
| `trello-aware-planning` | `planning-with-trello` |

#### Implementation

1. Rename directories
2. Update `name` field in SKILL.md frontmatter
3. Update any cross-references between skills
4. Update documentation references

#### Acceptance Criteria

- [ ] All skills use gerund form naming
- [ ] Frontmatter `name` matches directory
- [ ] No broken references
- [ ] `bpsai-pair skill validate` passes
- [ ] Documentation updated

---

### T20.2: Third-Person Voice in Skill Descriptions

**Priority:** P2
**Effort:** S (1 hr)
**Type:** chore

#### Description

Update all skill descriptions to use third-person voice instead of second-person directives.

#### Current → New Style

| Current (2nd person) | New (3rd person) |
|---------------------|------------------|
| "Use when reviewing code..." | "Provides code review workflow for identifying issues..." |
| "Use when you need to..." | "Enables developers to..." |

#### Acceptance Criteria

- [ ] All descriptions use third-person voice
- [ ] Descriptions remain under 1024 characters
- [ ] `bpsai-pair skill validate` passes with no voice warnings

---

### T20.3: Create skill-creation Skill

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature
**Source:** TASK-119 (from original roadmap)

#### Description

Create a meta-skill that teaches Claude how to create new skills following Anthropic's specifications.

#### Skill Content

```markdown
---
name: creating-skills
description: Guides the creation of new agent skills following Anthropic specifications.
  Provides templates, validation rules, and best practices for skill development.
---

# Creating Skills

## When to Create a Skill

Create a skill when:
- A workflow is repeated across multiple sessions
- Complex multi-step processes need documentation
- Team needs standardized approach to a task

## Skill Structure

.claude/skills/{skill-name}/
├── SKILL.md          # Required: Main skill document
├── reference/        # Optional: Supporting documents
└── scripts/          # Optional: Automation scripts

## SKILL.md Template

[Template with frontmatter, sections, examples]

## Validation Checklist

- [ ] Frontmatter: only name + description
- [ ] Description < 1024 chars, third-person voice
- [ ] SKILL.md < 500 lines
- [ ] Name: lowercase, hyphens, gerund form
- [ ] No "Claude already knows this" content

## CLI Commands

bpsai-pair skill create <name>    # Scaffold new skill
bpsai-pair skill validate         # Check all skills
bpsai-pair skill validate <name>  # Check specific skill
```

#### Acceptance Criteria

- [ ] Skill created at `.claude/skills/creating-skills/`
- [ ] Includes complete template
- [ ] Documents all validation rules
- [ ] References CLI commands
- [ ] Self-validates (passes skill validator)

---

### T20.4: Skill Installer Command

**Priority:** P1
**Effort:** M (4 hrs)
**Type:** feature

#### Description

Add `bpsai-pair skill install` command to install skills from URLs or local paths.

#### CLI Signatures

```bash
# Install from URL
bpsai-pair skill install https://github.com/user/repo/tree/main/.claude/skills/my-skill

# Install from local path
bpsai-pair skill install ~/my-skills/custom-review

# Install from skill registry (future)
bpsai-pair skill install @bpsai/security-review
```

#### Installation Process

1. Download/copy skill directory
2. Validate against skill spec
3. Check for conflicts with existing skills
4. Install to `.claude/skills/` or `~/.claude/skills/`
5. Report installation status

#### CLI Output

```bash
$ bpsai-pair skill install https://github.com/example/skills/security-audit

Downloading skill: security-audit...
Validating...
  ✅ Frontmatter valid
  ✅ Description under 1024 chars
  ✅ No conflicts with existing skills

Install to:
  [1] .claude/skills/ (project)
  [2] ~/.claude/skills/ (personal)

Choice: 1

✅ Installed security-audit to .claude/skills/security-audit/
```

#### Acceptance Criteria

- [ ] `skill install <url>` works for GitHub URLs
- [ ] `skill install <path>` works for local paths
- [ ] Validates skill before installation
- [ ] Detects naming conflicts
- [ ] Prompts for project vs personal installation
- [ ] `--project` and `--personal` flags to skip prompt

---

### T20.5: Cross-Platform Skill Structure

**Priority:** P2
**Effort:** L (6 hrs)
**Type:** feature

#### Description

Ensure skills work across different AI coding tools, not just Claude Code.

#### Compatibility Matrix

| Platform | Skill Discovery | Script Execution |
|----------|----------------|------------------|
| Claude Code | ✅ Native | ✅ Native |
| Cursor | ⚠️ Rules file | ⚠️ Manual |
| Continue.dev | ⚠️ Context file | ⚠️ Manual |
| GitHub Copilot | ❌ N/A | ❌ N/A |

#### Implementation

1. Document portable skill subset (SKILL.md only, no scripts)
2. Create export command for other platforms
3. Generate platform-specific formats

#### Export Formats

```bash
# Export for Cursor
bpsai-pair skill export my-skill --format cursor
# Creates .cursor/rules/my-skill.md

# Export for Continue.dev
bpsai-pair skill export my-skill --format continue
# Creates .continue/context/my-skill.md
```

#### Acceptance Criteria

- [ ] Document portable skill requirements
- [ ] `skill export` command exists
- [ ] Cursor format export works
- [ ] Continue.dev format export works
- [ ] Exported skills maintain core functionality

---

### T20.6: Preset Validation and Update Command

**Priority:** P3
**Effort:** M (3 hrs)
**Type:** feature
**Source:** ENH-003

#### Description

After updating PairCoder, existing projects may have outdated config. Add command to validate and update config against current preset standards.

#### CLI Signatures

```bash
# Check config against preset
bpsai-pair config validate
# Shows: Missing sections: trello, estimation, security

# Update config from preset
bpsai-pair config update --preset react
# Adds missing sections while preserving existing values
```

#### Validation Output

```bash
$ bpsai-pair config validate

Config Validation (preset: react):
  ✅ version: 2.7
  ✅ project section
  ✅ workflow section
  ❌ Missing: trello section
  ❌ Missing: estimation section
  ⚠️  Outdated: hooks section (missing new hooks)

Run `bpsai-pair config update --preset react` to fix.
```

#### Acceptance Criteria

- [ ] `config validate` shows missing/outdated sections
- [ ] `config update` adds missing sections from preset
- [ ] Existing values preserved during update
- [ ] `--dry-run` flag shows what would change
- [ ] Backup created before update

---

### T20.7: Trello Custom Fields CLI

**Priority:** P2
**Effort:** M (4 hrs)
**Type:** feature
**Source:** ENH-004

#### Description

Add CLI commands to set Trello custom fields programmatically.

#### CLI Signatures

```bash
# Set individual field
bpsai-pair trello set-field <card-id> --project "Support App"
bpsai-pair trello set-field <card-id> --stack "React"
bpsai-pair trello set-field <card-id> --repo-url "https://github.com/..."

# Apply all defaults from config
bpsai-pair trello apply-defaults <card-id>

# Apply defaults during sync
bpsai-pair plan sync-trello <plan-id> --apply-defaults
```

#### Config Addition

```yaml
trello:
  board_id: "..."
  defaults:
    project: "PairCoder"
    stack: "Python"
    repo_url: "https://github.com/bpsai/paircoder"
```

#### Acceptance Criteria

- [ ] Can set custom fields via CLI
- [ ] Can apply project defaults to cards
- [ ] `plan sync-trello` has `--apply-defaults` option
- [ ] `ttask start` optionally applies defaults
- [ ] Config section documented

---

### T20.8: Document Trello Board Conventions

**Priority:** P1
**Effort:** S (2 hrs)
**Type:** docs
**Source:** DOC-004

#### Description

Document BPS-specific Trello board conventions so Claude doesn't move protected cards or miss required fields.

#### Content

```markdown
## BPS Board Conventions

### Protected Cards (NEVER MOVE)
Cards in the "Info" list are dashboard cards:
- Weekly Completed, Frontend Completed, Backend Completed
- Aging WIP, Worker/Function Completed
- Board Setup card
- Any card with colored counter backgrounds

### Required Custom Fields
When creating/completing cards, set:
- Project: The project name
- Stack: Technology stack
- Repo URL: GitHub repository URL
- Effort: Task size (XS, S, M, L, XL)
- Agent Task: Check if AI-assignable

### On Task Completion
1. Check ALL acceptance criteria items
2. Verify custom fields are set
3. Add completion summary as comment

### On PR Creation
Add PR URL to card's "PR URL" custom field
```

#### Deliverables

- Update `.claude/skills/planning-with-trello/SKILL.md`
- Create `.paircoder/context/bps-board-conventions.md` reference doc
- Update docs/USER_GUIDE.md

#### Acceptance Criteria

- [ ] Info list cards documented as protected
- [ ] Custom field requirements documented
- [ ] Acceptance criteria checking emphasized
- [ ] PR URL workflow documented
- [ ] Reference doc created

---

## Sprint Totals

| Priority | Count | Effort |
|----------|-------|--------|
| P1 | 3 | M + M + S |
| P2 | 4 | S + L + M + S |
| P3 | 1 | M |
| **Total** | **8** | ~26-30 hrs |

---

## Dependencies

| Task | Depends On |
|------|------------|
| T20.1, T20.2 | T19.6 (skill validator) |
| T20.3 | T20.1, T20.2 (naming conventions established) |
| T20.4 | T20.3 (skill-creation skill for validation) |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All skills pass validator
- [ ] Skill installer working
- [ ] Cross-platform export functional
- [ ] Version bumped to 2.9.0
