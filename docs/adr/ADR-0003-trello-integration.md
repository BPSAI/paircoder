# ADR 0003 — Trello Integration Architecture

**Status:** Accepted
**Date:** 2025-12-22
**Authors:** BPS AI Software Team

---

## Context

PairCoder's Trello integration evolved from simple card syncing (v2.3) to a more sophisticated system. During Sprint 18, we encountered critical failures in the sync-based approach:

1. **Custom field mismatches** - CLI attempted to set invalid dropdown values
2. **Dual source of truth** - Conflicts between local files and Trello cards
3. **Manual state.md maintenance** - Error-prone and frequently forgotten
4. **Sync failures** - Broke planning workflows entirely

This ADR documents the decision to support multiple integration modes, with Trello-native mode as the recommended approach for teams using Trello.

---

## Decision

### Integration Modes

PairCoder supports three Trello integration modes:

| Mode | Config | Source of Truth | Best For |
|------|--------|-----------------|----------|
| **Disabled** | `enabled: false` | Local files only | Solo dev, no Trello |
| **Sync** | `mode: sync` | Local files → Trello | Teams wanting visibility |
| **Native** | `mode: native` | Trello → local | Full Trello workflow |

### Mode Comparison

```
SYNC MODE (v2.3-2.6):
┌─────────────────────┐         ┌─────────────────────┐
│   Local Files       │ ──sync─→│      Trello         │
│   (source of truth) │ ←─sync──│   (visibility)      │
└─────────────────────┘         └─────────────────────┘
Problems: Sync conflicts, validation failures, dual maintenance

NATIVE MODE (v3.0+):
┌─────────────────────┐         ┌─────────────────────┐
│   Local Files       │         │      Trello         │
│   (config only)     │ ──read─→│  (source of truth)  │
│   state.md (gen'd)  │ ←─gen───│                     │
└─────────────────────┘         └─────────────────────┘
Benefits: Single source, no sync bugs, auto-generated state
```

### Custom Field Validation (v2.6.1+)

The CLI now validates custom field values against actual board options:

```bash
# Fetch and display valid options
bpsai-pair trello fields

# Output:
# Stack (list)
#   • React
#   • Flask
#   • Worker/Function
#   • Infra
#   • Collection
```

**Field mappings** translate common aliases:
- `cli` → `Worker/Function`
- `python` → `Flask`
- `frontend` → `React`
- `docs` → `Collection`

### BPS Board Conventions

For BPS projects, the following custom fields are standard:

| Field | Type | Options |
|-------|------|---------|
| **Project** | Dropdown | PairCoder, Aurora, CodexAgent-Trello, ... |
| **Stack** | Dropdown | React, Flask, Worker/Function, Infra, Collection |
| **Status** | Dropdown | Planning, In progress, Testing, Done, Enqueued, Waiting, Blocked |
| **Effort** | Dropdown | S, M, L (no XS or XL) |
| **Repo URL** | Dropdown | Repository URLs |
| **Agent Task** | Checkbox | AI-assignable flag |

### Configuration

```yaml
# .paircoder/config.yaml

trello:
  enabled: true
  board_id: "694176ebf4b9d27c6e7a0e73"
  mode: native  # disabled | sync | native
  
  # Default values for this project's cards
  defaults:
    project: PairCoder
    stack: Worker/Function
    repo_url: https://github.com/BPSAI/paircoder
  
  # Native mode settings (v3.0+)
  native:
    planning_list: "Sprint Planning"
    backlog_pattern: "*.md"
    auto_refresh_state: true
    archive_list: "Archived Sprints"
```

### Board Structure

```
Trello Board
├── 📋 Info (protected dashboard cards - NEVER MOVE)
├── 📋 Sprint Planning
│   ├── Sprint 19 (card) + 📎 backlog.md
│   ├── EPIC-001 (card) + 📎 epic.md
│   └── ...
├── 📋 Intake/Backlog
├── 📋 Planned/Ready
├── 📋 In Progress
├── 📋 Review/Testing
├── 📋 Deployed/Done
├── 📋 Issues/Tech Debt
└── 📋 Archived Sprints
```

---

## Consequences

### Positive
- **Native mode eliminates sync bugs** by design
- **Custom field validation** prevents invalid values
- **Auto-generated state.md** reduces manual maintenance
- **Field caching** improves performance
- **Backward compatible** - sync mode still works

### Negative
- **Network dependency** in native mode
- **Three modes to maintain** in codebase
- **Learning curve** for mode differences

### Mitigations
- Clear documentation of mode differences
- `bpsai-pair trello fields` command for discovery
- BPS preset defaults to native mode
- Graceful degradation with cached data

---

## Implementation

| Version | Feature |
|---------|---------|
| v2.3 | Initial Trello integration (sync mode) |
| v2.4 | Webhooks, GitHub integration |
| v2.5 | Custom fields, two-way sync |
| v2.6.1 | Field validation, `trello fields` command |
| v3.0 | Native mode (EPIC-002) |

---

## Alternatives Considered

### Option 1: Fix Sync Mode Only
- **Rejected** - Dual source of truth is fundamentally problematic

### Option 2: Trello Native Only
- **Rejected** - Need to support non-Trello users

### Option 3: Different Tool per Mode
- **Rejected** - Fragmenting the codebase is worse than modes

### Chosen: Multiple Modes
Support all three modes with clear documentation and sensible defaults.

---

## References

- EPIC-002: Trello-Native Mode specification
- Sprint 18 incident analysis
- `.paircoder/context/bps-board-conventions.md`
- `tools/cli/bpsai_pair/trello/fields.py` implementation
