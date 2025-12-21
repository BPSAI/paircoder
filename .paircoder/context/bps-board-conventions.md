# BPS Trello Board Conventions

> Reference document for AI agents working with BPS AI Software Trello boards.

---

## Protected Cards (NEVER MOVE)

The **"Info"** list contains dashboard/header cards that aggregate board metrics. These cards must NEVER be moved, modified, or deleted.

### Dashboard Cards to Protect

| Card Name | Purpose |
|-----------|---------|
| Weekly Completed | Tracks weekly completion count |
| Frontend Completed | Counts frontend task completions |
| Backend Completed | Counts backend task completions |
| Worker/Function Completed | Tracks worker/function completions |
| Aging WIP | Shows work-in-progress aging metrics |
| Board Setup | Board configuration card |

### How to Identify Protected Cards

- Located in the "Info" list
- Often have colored counter backgrounds
- Display aggregate numbers or metrics
- Have automation rules attached

**Rule:** If a card is in the "Info" list, assume it's protected and leave it alone.

---

## Required Custom Fields

When creating or completing Trello cards, these custom fields MUST be populated:

### On Card Creation

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **Project** | Yes | The project name | "Support App", "PairCoder" |
| **Stack** | Yes | Technology stack | "React", "Python", "Flask", "CLI" |
| **Repo URL** | Yes | GitHub repository URL | `https://github.com/org/repo` |
| **Effort** | Yes | Task size estimate | XS, S, M, L, XL |
| **Agent Task** | If AI-assignable | Check if AI can work on this | Checkbox |

### On Card Completion

| Field | When | Description |
|-------|------|-------------|
| **PR URL** | When PR created | Link to the pull request |

### Effort Sizing Guide

| Size | Time Estimate | Complexity Range |
|------|---------------|------------------|
| XS | < 1 hour | 0-10 |
| S | 1-4 hours | 11-25 |
| M | 4-8 hours (half to full day) | 26-50 |
| L | 1-2 days | 51-75 |
| XL | 3+ days | 76+ |

---

## Acceptance Criteria Workflow

### Creating Acceptance Criteria

When creating cards, add acceptance criteria as a checklist named "Acceptance Criteria":

```markdown
Checklist: Acceptance Criteria
- [ ] Feature X is implemented
- [ ] Unit tests pass
- [ ] Documentation updated
- [ ] No console errors
```

### Checking Off Acceptance Criteria

**CRITICAL:** All acceptance criteria items MUST be checked before moving a card to "Deployed/Done".

Use the `ttask done` command which automatically checks all items:

```bash
bpsai-pair ttask done TRELLO-XX --summary "What was accomplished" --list "Deployed/Done"
```

**What this does:**
1. Moves card to specified list
2. **Automatically checks ALL acceptance criteria items**
3. Adds completion summary as comment

**DO NOT** manually move cards to Done without checking acceptance criteria.

---

## PR URL Workflow

### When Creating a Pull Request

1. Create the PR on GitHub
2. Add the PR URL to the Trello card:

```bash
bpsai-pair ttask update TRELLO-XX --pr-url "https://github.com/org/repo/pull/123"
```

Or manually set the "PR URL" custom field on the card.

### PR Link in Card Description

Also include in the PR description:

```markdown
## Related
- Trello: https://trello.com/c/shortId
```

---

## Board List Structure

Standard BPS board has 7 lists:

| List | Purpose | Cards Move Here When... |
|------|---------|------------------------|
| **Info** | Dashboard cards (PROTECTED) | Never - these are static |
| **Intake / Backlog** | New ideas, unplanned work | Newly created, not yet planned |
| **Planned / Ready** | Selected for upcoming work | Prioritized for next 1-2 weeks |
| **In Progress** | Active development | Work has started |
| **Review / Testing** | Under review | Implementation complete, needs review |
| **Deployed / Done** | Completed and live | Merged and deployed |
| **Issues / Tech Debt** | Bugs, improvements | Issues found, tech debt identified |

---

## Card Title Format

```
[Stack] Task Name
```

### Examples

- `[CLI] Implement MCP server core`
- `[Docs] Update README with v2.4 features`
- `[Flask] Add authentication middleware`
- `[React] Fix login form validation`

---

## Labels by Stack

| Label | Color | Use For |
|-------|-------|---------|
| Frontend | Green | React, UI, UX |
| Backend | Blue | Flask, API, Python |
| Worker | Purple | Background jobs, AI pipelines |
| Deployment | Red | CI/CD, infrastructure |
| Bug / Issue | Orange | Bugs, runtime issues |
| Security | Yellow | Auth, compliance |
| Documentation | Brown | Docs, guides |
| AI / ML | Black | Models, LLM, MCP |

---

## Quick Reference Commands

### Card Operations

```bash
# Start a task (moves to In Progress)
bpsai-pair ttask start TRELLO-XX

# Complete a task (checks AC, moves to Done)
bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"

# Add PR URL
bpsai-pair ttask update TRELLO-XX --pr-url "https://..."

# Add progress comment
bpsai-pair ttask comment TRELLO-XX "Progress update..."

# Move to specific list
bpsai-pair ttask move TRELLO-XX "List Name"
```

### Checking Custom Fields

```bash
# View card details including custom fields
bpsai-pair ttask show TRELLO-XX
```

---

## Common Mistakes to Avoid

| Mistake | Correct Action |
|---------|----------------|
| Moving Info list cards | Never touch Info list cards |
| Leaving custom fields empty | Always set Project, Stack, Repo URL, Effort |
| Moving to Done without checking AC | Use `ttask done` to auto-check criteria |
| Not adding PR URL | Add PR URL when creating pull request |
| Using `task update --status done` only | Use `ttask done` first, then `task update` |

---

## Completion Checklist

Before marking any task as done:

1. [ ] All acceptance criteria checked on Trello card
2. [ ] Custom fields populated (Project, Stack, Repo URL, Effort)
3. [ ] PR URL added (if applicable)
4. [ ] Completion summary added as comment
5. [ ] Card in correct list ("Deployed/Done")
