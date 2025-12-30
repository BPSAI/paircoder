# BPS Trello Board Conventions

> Reference document for AI agents working with BPS AI Software Trello boards.
> **CRITICAL:** Use ONLY the exact values listed below for custom fields.

---

## Custom Field Options (EXACT VALUES)

These are the **only valid values** for custom fields. Do not invent new values.

### Project Field (Dropdown)

| Value                 | Use For                     |
|-----------------------|-----------------------------|
| `--`                  | Not specified               |
| `Aurora`              | Aurora project              |
| `CodexAgent-Trello`   | CodexAgent-Trello project   |
| `DanHil AP Invoices`  | DanHil AP Invoices project  |
| `DanHil RFQ`          | DanHil RFQ project          |
| `Prompt Acadamy`      | Prompt Acadamy project      |
| `Weber SSRS Analysis` | Weber SSRS Analysis project |
| `PairCoder`           | **All PairCoder tasks**     |
| `Support App`         | BPS Support App SDK project |



### Stack Field (Dropdown)

| Value           | Use For                           |
|-----------------|-----------------------------------|
| `--`            | Not specified                     |
| `React`         | Frontend React work               |
| `Flask`         | Flask/Python API work             |
| `Worker`        | Background jobs, utilities        |
| `Infra`         | Infrastructure, CI/CD, deployment |
| `Collection`    | Documentation, meta-tasks         |
| `Container App` | Containers                        |
| `Package`       | CLI tools, Packages               |


### Status Field (Dropdown)

| Value | Maps To | Use When |
|-------|---------|----------|
| `--` | Not set | Never use |
| `Planning` | pending | Task is being planned |
| `In progress` | in_progress | Work has started |
| `Testing` | review | Under test/review |
| `Done` | done | Completed |
| `Enqueued` | ready | Ready to start, waiting |
| `Waiting` | blocked | Waiting on external dependency |
| `Blocked` | blocked | Cannot proceed |

### Effort Field (Dropdown)

| Value | Complexity Range | Hours |
|-------|------------------|-------|
| `--` | Not specified | - |
| `S` | 0-30 | < 4 hrs |
| `M` | 31-60 | 4-8 hrs |
| `L` | 61-100 | 1+ days |

**Note:** Only S, M, L are available. No XS or XL options exist.

```

---

## Protected Cards (NEVER MOVE)

The **"Info"** list contains dashboard/header cards. NEVER move, modify, or delete:

- Weekly Completed
- Frontend Completed
- Backend Completed
- Worker/Function Completed
- Aging WIP
- Board Setup card
- Any card with colored counter backgrounds

---

## Valid Plan Types

The CLI only accepts these plan types:

| Type | Use For |
|------|---------|
| `feature` | New functionality |
| `bugfix` | Bug fixes |
| `refactor` | Code improvements |
| `chore` | Maintenance, cleanup, docs |

**Note:** `maintenance` is NOT valid. Use `chore` instead.

---

## Task Naming Convention

| Format | Example | Use For |
|--------|---------|---------|
| `T{sprint}.{seq}` | T18.1, T18.2 | Sprint tasks (preferred) |
| `TASK-{num}` | TASK-150 | Legacy format |
| `REL-{sprint}-{seq}` | REL-18-01 | Release tasks |
| `BUG-{num}` | BUG-005 | Bug fixes |

---

## Board List Structure

| List | Purpose |
|------|---------|
| **Info** | Dashboard cards (PROTECTED) |
| **Intake/Backlog** | New unplanned work |
| **Planned/Ready** | Ready for upcoming work |
| **In Progress** | Active development |
| **Review/Testing** | Under review |
| **Deployed/Done** | Completed |
| **Issues/Tech Debt** | Bugs, improvements |

---

## Quick Reference for `plan sync-trello`

```bash
# Sync plan to Trello (uses board_id from config)
bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"

# If board_id not in config, specify explicitly
bpsai-pair plan sync-trello <plan-id> --board <board-id> --target-list "Planned/Ready"
```

---

## Common Mistakes to AVOID

| Mistake | Correct                                  |
|---------|------------------------------------------|
| `Project: "Sprint 18 - Release Engineering"` | `Project: PairCoder`                     |
| `Stack: CLI` | `Stack: Package`                         |
| `Stack: Bug/Issue` | Use **labels** for Bug/Issue, not Stack  |
| `Stack: Documentation` | `Stack: Collection`                      |
| `Status: To do` | `Status: Planning` or `Status: Enqueued` |
| `Type: maintenance` | `Type: chore`                            |
| Inventing new dropdown values | Use ONLY values listed above             |
