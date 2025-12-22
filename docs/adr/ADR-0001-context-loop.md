# ADR 0001 — PairCoder Context Loop

**Status:** Accepted (Revised 2025-12-22)
**Original Date:** 2025-01-15
**Revision Date:** 2025-12-22

---

## Context

AI agents operate with limited context windows and benefit from a compact, structured state that is continuously maintained by developers. As AI capabilities evolved, the original simple loop needed enhancement to support planning systems and multi-session workflows.

---

## Decision

### Original Design (v1)

We maintain a persistent context loop in `context/development.md` with four fields:

- **Overall goal is:** one-sentence mission
- **Last action was:** the latest material change
- **Next action will be:** the immediate next step
- **Blockers:** any impediments or decisions needed

### Evolution (v2+)

The context loop has been superseded by a richer state management system:

| v1 Location | v2+ Location | Purpose |
|-------------|--------------|---------|
| `context/development.md` | `.paircoder/context/state.md` | Current task/sprint state |
| (embedded in development.md) | `.paircoder/context/project.md` | Project-level goals and constraints |
| (embedded in development.md) | `.paircoder/context/workflow.md` | How we work (branching, review, etc.) |

### state.md Structure (v2.6+)

```markdown
# Project State

## Active Sprint: Sprint N

| ID | Title | Status | Effort |
|----|-------|--------|--------|
| T{N}.1 | Task title | pending/in_progress/done | S/M/L |

## Session Log

### YYYY-MM-DD HH:MM - What Was Just Done
- Completed X
- Updated Y

### What's Next
- Start T{N}.2
```

### Future Direction (v3.0 - Trello-Native Mode)

In Trello-native mode, `state.md` becomes **auto-generated** from board state rather than manually maintained. See ADR 0003 for details.

---

## Consequences

### Positive
- Agents read stable state every session
- Clear separation of project, workflow, and state concerns
- Supports planning system integration
- Session log provides audit trail

### Negative
- Developers must update state.md after each change
- Multiple files to maintain (mitigated by CLI commands)
- Manual maintenance error-prone (addressed in v3.0 with auto-generation)

### Mitigations
- `bpsai-pair context-sync` CLI command for updates
- Task completion hooks auto-update state (v2.2+)
- v3.0 Trello-native mode eliminates manual maintenance

---

## References

- ADR 0002: PairCoder v2 Architecture
- ADR 0003: Trello Integration Architecture
- `.paircoder/context/state.md` specification
