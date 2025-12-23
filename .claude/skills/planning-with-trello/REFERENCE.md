# BPS Trello Board Conventions for Planning

> Reference document for BPS AI Software Trello board conventions during planning.
> This is a project-specific reference that complements the generic skill.

---

## Protected Cards (NEVER MOVE)

The **"Info"** list contains dashboard/header cards that must NEVER be touched:
- Weekly Completed, Frontend Completed, Backend Completed
- Worker/Function Completed, Aging WIP, Board Setup
- Any card with colored counter backgrounds

**Rule:** If a card is in the "Info" list, leave it alone.

---

## Required Custom Fields When Creating Cards

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **Project** | Yes | The project name | "Support App", "PairCoder" |
| **Stack** | Yes | Technology stack | "React", "Python", "Flask" |
| **Repo URL** | Yes | GitHub repository URL | `https://github.com/org/repo` |
| **Effort** | Yes | Task size estimate | XS, S, M, L, XL |
| **Agent Task** | If AI-assignable | Check if AI can work on this | Checkbox |

---

## Effort Sizing Guide

| Size | Time Estimate | Complexity Range |
|------|---------------|------------------|
| XS | < 1 hour | 0-10 |
| S | 1-4 hours | 11-25 |
| M | 4-8 hours (half to full day) | 26-50 |
| L | 1-2 days | 51-75 |
| XL | 3+ days | 76+ |

---

## Acceptance Criteria on New Cards

Always add acceptance criteria as a checklist when creating cards:

```markdown
Checklist: Acceptance Criteria
- [ ] Feature X is implemented
- [ ] Unit tests pass
- [ ] Documentation updated
```

---

## PR URL Workflow

When a PR is created for a card:

1. Add PR URL to the card:
   ```bash
   bpsai-pair ttask update TRELLO-XX --pr-url "https://github.com/org/repo/pull/123"
   ```

2. Include Trello link in PR description:
   ```markdown
   ## Related
   - Trello: https://trello.com/c/shortId
   ```

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

## Common Mistakes to Avoid

| Mistake | Correct Action |
|---------|----------------|
| Moving Info list cards | Never touch Info list cards |
| Leaving custom fields empty | Always set Project, Stack, Repo URL, Effort |
| Not adding acceptance criteria | Always add AC checklist to new cards |
| Creating cards in wrong list | Sprint tasks go in "Planned/Ready", not "Intake/Backlog" |
