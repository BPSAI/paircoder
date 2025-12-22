# ADR 0002 — PairCoder v2 Architecture

**Status:** Accepted (Revised 2025-12-22)
**Original Date:** 2025-12-12
**Revision Dates:** 2025-12-15, 2025-12-22
**Authors:** BPS AI Software Team

---

## Context

PairCoder v1 established a disciplined workflow for AI pair programming: context loops, agent packs, feature branching, and validation tooling. v2 expanded this with planning systems, multi-agent orchestration, and external integrations.

This ADR documents the architecture as implemented through v2.6, incorporating lessons learned from 18 sprints of development.

---

## Decision

### Core Architecture

```
.paircoder/                          # All PairCoder system files
├── config.yaml                      # Project configuration
├── capabilities.yaml                # LLM capability manifest
├── context/
│   ├── project.md                   # Project constraints & goals
│   ├── workflow.md                  # How we work here
│   ├── state.md                     # Current plan/task state
│   └── bps-board-conventions.md     # Trello field reference (if using Trello)
├── flows/                           # Workflow definitions
│   └── *.flow.md
├── plans/                           # Plan files
│   └── plan-*.plan.yaml
├── tasks/                           # Task files by plan
│   └── <plan-slug>/
│       └── T*.task.md
├── cache/                           # Runtime caches
│   └── trello_fields_*.json
└── history/                         # Metrics and archives
    ├── metrics.jsonl
    └── archive/

.claude/                             # Claude Code native integration
├── skills/                          # Model-invoked skills
│   └── */SKILL.md
├── agents/                          # Custom subagents
│   └── *.md
└── commands/                        # Slash commands
    └── *.md

CLAUDE.md                            # Claude Code entry point
AGENTS.md                            # Universal AI entry point
```

### CLI Command Groups (88 commands as of v2.6)

| Group | Commands | Purpose |
|-------|----------|---------|
| Core | init, feature, pack, context-sync, status, validate, ci | Foundation |
| Planning | plan new/list/show/tasks/status/sync-trello/add-task | Goal → Task decomposition |
| Tasks | task list/show/update/next/auto-next/archive/restore | Task lifecycle |
| Flows | flow list/show/run/validate | Workflow execution |
| Orchestration | orchestrate task/analyze/handoff/auto-run | Multi-agent routing |
| Trello | trello connect/status/boards/fields/... | Trello integration |
| Trello Tasks | ttask list/start/done/block/comment | Card-based task work |
| GitHub | github status/create/list/merge/auto-pr | PR management |
| Metrics | metrics summary/task/breakdown/budget | Analytics |
| Timer | timer start/stop/status/summary | Time tracking |
| MCP | mcp serve/tools/test | Model Context Protocol |

### Planning System

**Plan Types (YAML):**
- `feature` - New functionality
- `bugfix` - Bug fixes
- `refactor` - Code improvements
- `chore` - Maintenance, cleanup, docs

**Task Naming Convention:**
- Sprint tasks: `T{sprint}.{seq}` (e.g., T18.1, T19.2)
- Legacy: `TASK-{num}` (e.g., TASK-150)
- Release: `REL-{sprint}-{seq}` (e.g., REL-18-01)

**Task Lifecycle:**
```
pending → in_progress → review → done
                ↓
             blocked
```

### Integration Modes

| Mode | Source of Truth | Sync Direction | Use Case |
|------|-----------------|----------------|----------|
| **Disabled** | Local files only | N/A | Solo development |
| **Sync** | Local files | Files → Trello | Team visibility |
| **Native** | Trello | Trello → state.md | Full Trello workflow (v3.0) |

### Model Routing

```yaml
routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }
  overrides:
    security: claude-opus-4-5
    architecture: claude-opus-4-5
```

### Hooks System

```yaml
hooks:
  on_task_start: [start_timer, sync_trello, update_state]
  on_task_complete: [stop_timer, record_metrics, sync_trello, update_state, check_unblocked]
  on_task_block: [sync_trello, update_state]
```

---

## Implementation History

| Version | Sprint | Key Features |
|---------|--------|--------------|
| 2.0 | 1-5 | Directory structure, planning system, flows, Claude Code alignment |
| 2.1 | 5-6 | Skills, subagents, multi-agent orchestration |
| 2.2 | 7-9 | Task lifecycle, metrics, time tracking, prompt caching |
| 2.3 | 10 | Trello integration (sync mode) |
| 2.4 | 11-12 | MCP server, Trello webhooks, GitHub integration |
| 2.5 | 13-15 | Presets, intent detection, autonomous workflow, security sandbox |
| 2.6 | 16-17.5 | Real sub-agents, velocity metrics, backlog remediation |
| 2.6.1 | Hotfix | Trello field validation, `trello fields` command |

---

## What's Explicitly NOT Included

| Exclusion | Rationale |
|-----------|-----------|
| Project memory graphs | File-based state is sufficient |
| Auto-commit or git automation | Too opinionated; users control git |
| GUI or web interface | Out of scope for CLI tool |
| Plugin marketplace | Premature; start with built-in providers |
| Automatic migration | v1 → v2 is additive; no migration needed |

---

## Future Direction

### v2.7.0 (Sprint 18) - Release Engineering
- Single source of truth for version (importlib.metadata)
- Release prep command
- Cookie cutter drift detection

### v2.8.0-2.10.0 (Sprints 19-21) - Methodology & Skills
- Mandatory state.md update enforcement
- Session restart context recovery
- Cross-platform skill structure
- Emergent skill discovery

### v3.0.0 (Sprints 24-26) - Trello-Native Mode
- Trello as source of truth
- Auto-generated state.md
- Sprint cards with backlog attachments
- See ADR 0003 for details

---

## References

- ADR 0001: Context Loop
- ADR 0003: Trello Integration Architecture
- ADR 0004: Task & Sprint Management
- `.paircoder/capabilities.yaml` specification
- FEATURE_MATRIX.md for complete command reference
