# ADR 0002 — Paircoder v2 Architecture (Revised)

**Status:** Accepted (Revised 2025-12-15)
**Date:** 2025-12-12 (Original), 2025-12-15 (Revised)
**Authors:** BPS AI Software Team

---

## Context

Paircoder v1 established a disciplined workflow for AI pair programming: context loops, agent packs, 
feature branching, and validation tooling. As AI capabilities advance, users need:

1. **Native workflow orchestration** — Human-readable "flows" that agents can execute step-by-step
2. **Multi-provider support** — Freedom to use OpenAI, Anthropic, Google, or other providers
3. **Smart routing** — Automatic model selection based on task complexity and cost constraints
4. **Efficiency controls** — Token budgets, prompt caching, and cost awareness
5. **Planning system** — Goals decomposed into tasks organized into sprints (**NEW in revision**)
6. **LLM discoverability** — Capability manifest so LLMs know what they can do (**NEW in revision**)

This ADR locks the design constraints and compatibility rules for v2.

---

## Decision

### What Stays Stable (v1 Compatibility)

The following **MUST NOT** change behavior or break existing workflows:

| Component | Location | Guarantee |
|-----------|----------|-----------|
| CLI commands | `bpsai-pair init/feature/pack/context-sync/status/validate/ci` | Same flags, same output semantics |
| Context Loop | `context/development.md` with Overall/Last/Next/Blockers fields | **DEPRECATED** — migrated to `.paircoder/context/state.md` |
| Agent Pack | `.tgz` respecting `.agentpackignore`, includes context, prompts | Same archive structure |
| Cross-platform | Pure Python, no bash-only dependencies | Windows/macOS/Linux parity |

**Migration policy:** No dedicated migration command. v2 features are opt-in additions; v1 repos continue working unchanged.

### What's New (v2 Additions)

#### 1. Directory Consolidation

All PairCoder system files move under `.paircoder/`:

```
.paircoder/
├── config.yaml                    # Project configuration (v2)
├── capabilities.yaml              # LLM capability manifest (NEW)
├── context/
│   ├── project.md                 # High-level project constraints & goals
│   ├── workflow.md                # How we work here (branches, tests, review)
│   └── state.md                   # Current plan/task state (replaces Context Sync)
├── flows/
│   ├── design-plan-implement.flow.md
│   ├── tdd-implement.flow.md
│   ├── review.flow.md
│   └── finish-branch.flow.md
├── plans/
│   └── plan-YYYY-MM-<slug>.plan.yaml
├── tasks/
│   └── <plan-slug>/
│       └── TASK-NNN.task.md
└── history/
    ├── metrics.jsonl
    └── log.md
```

Root-level files (minimal):
- `AGENTS.md` — Pointer to `.paircoder/context/`
- `CLAUDE.md` — Pointer to `.paircoder/context/`

#### 2. Planning System (Goals → Tasks → Sprints)

**Plan Schema** (`.paircoder/plans/<id>.plan.yaml`):

```yaml
id: plan-2025-01-workspace-filter
title: Workspace filter feature
type: feature            # feature | bugfix | refactor | chore
owner: david
created_at: 2025-01-10T12:00:00Z
flows:
  - design-plan-implement
status: in_progress      # planned | in_progress | complete | archived

goals:
  - Allow users to filter workspaces by owner and status
  - Maintain API compatibility for existing clients

sprints:
  - id: sprint-1
    title: "Design & Backend"
    tasks: [TASK-001, TASK-002]
  - id: sprint-2
    title: "Frontend & Polish"
    tasks: [TASK-003]

tasks:
  - id: TASK-001
    title: Design API shape and UI flows
    priority: P0
    complexity: 40
    status: done
  - id: TASK-002
    title: Implement backend filter endpoints
    priority: P0
    complexity: 60
    status: in_progress
```

**Task Schema** (`.paircoder/tasks/<plan-slug>/TASK-NNN.task.md`):

```yaml
---
id: TASK-001
plan: plan-2025-01-workspace-filter
title: Design API shape and UI flows
type: design
priority: P0
complexity: 40
status: done
tags: [frontend, api, design]
---

# Objective

Define the API endpoints and user flows needed...

# Implementation Plan

- Review current implementation
- Propose 2–3 designs with tradeoffs
- Select one design

# Acceptance Criteria

- Design covers: query parameters, pagination
- UI states for all scenarios

# Verification

- Design doc exists and is checked in
- Owner has approved
```

#### 3. Flows System (YAML Frontmatter + Markdown)

Flows use a hybrid format: YAML frontmatter for metadata, Markdown body for instructions.

```markdown
---
name: design-plan-implement
version: 1
description: >
  Turn a feature request into a validated design, a concrete implementation plan,
  and a sequence of TDD-anchored tasks.
when_to_use:
  - feature_request
  - large_refactor
roles:
  navigator: { primary: true }
  driver: { primary: true }
triggers:
  - on: user_describes_feature
requires:
  tools: [git, test_runner]
  context:
    - .paircoder/context/project.md
    - .paircoder/context/workflow.md
tags: [design, planning, implementation]
---

# Design → Plan → Implement Flow

## Phase 1 — Design (Navigator-led)

1. Navigator reads `project.md` and relevant code
2. Navigator runs brainstorming sub-flow
3. Navigator writes design doc

## Phase 2 — Plan (Navigator-led)

1. Decompose design into 5–20 tasks
2. Save plan to `.paircoder/plans/`
3. Generate task files

## Phase 3 — Implement (Driver-led)

1. For each task, run `tdd-implement` flow
2. Run tests, lint, typecheck
3. Run `review` flow
```

#### 4. LLM Capability Manifest

New file `.paircoder/capabilities.yaml` that tells LLMs:
- What capabilities are available
- When to use each one
- How to invoke them (CLI or programmatic)
- Which flows to suggest based on user intent

This enables Claude Code, Codex CLI, and similar tools to use PairCoder 
without requiring users to memorize CLI commands.

#### 5. Extended CLI Commands

**New commands:**

```bash
# Planning
bpsai-pair plan new <slug> --type <type> [--flow <flow>]
bpsai-pair plan list
bpsai-pair plan show <id>
bpsai-pair plan tasks <id>
bpsai-pair plan add-task <id>
bpsai-pair plan complete-task <id> <task-id>

# Tasks
bpsai-pair task list [--plan <id>]
bpsai-pair task show <id>
bpsai-pair task update <id> --status <status>

# Models
bpsai-pair models test
bpsai-pair models routes
bpsai-pair models explain --task-id <id>
```

**Enhanced existing commands:**

```bash
bpsai-pair feature <slug> --flow <flow> --plan <plan>
bpsai-pair pack --scope <plan|branch>
```

#### 6. Orchestration Layer

Provider-agnostic runtime that routes requests to the best model:

| Provider | Models | Key Features |
|----------|--------|--------------|
| **Anthropic** | Claude Opus 4.5, Sonnet 4.5, Haiku 4.5 | `effort` parameter, 200k context |
| **OpenAI** | GPT-5.1-Codex variants | Compaction, Windows native |
| **Google** | Gemini 3 Pro, Deep Think | `thinking_level`, 1M context |

Configuration in `.paircoder/config.yaml`:

```yaml
models:
  navigator: claude-sonnet-4-5
  driver: gpt-5.1-codex
  reviewer: claude-sonnet-4-5

routing:
  by_complexity:
    trivial: claude-haiku-4-5
    simple: claude-haiku-4-5
    moderate: claude-sonnet-4-5
    complex: claude-opus-4-5
    epic: claude-opus-4-5
```

### What's Explicitly NOT Included

These features are **out of scope** for v2:

| Exclusion | Rationale |
|-----------|-----------|
| Project memory graphs | Speculative; file-based state is sufficient |
| Auto-commit or git automation | Too opinionated; users control git |
| GUI or web interface | Out of scope for CLI tool |
| Migration command | v1 → v2 is additive; no migration needed |
| Plugin marketplace | Premature; start with built-in providers |

---

## Architecture Constraints

### Module Structure (v2)

```
tools/cli/bpsai_pair/
├── cli.py                 # Existing CLI (extended)
├── ops.py                 # Existing operations (stable)
├── config.py              # Extended for v2 config
├── orchestrator/          # Model routing + runtime
│   ├── router.py
│   ├── classifier.py
│   └── budget.py
├── providers/             # Provider adapters
│   ├── base.py
│   ├── openai.py
│   ├── anthropic.py
│   └── google.py
├── flows/                 # Flow engine (extended)
│   ├── parser.py          # YAML frontmatter + MD
│   ├── models.py
│   └── executor.py
└── planning/              # NEW: Planning system
    ├── models.py          # Plan, Task, Sprint
    ├── parser.py          # YAML/MD parsing
    └── state.py           # State management
```

---

## Implementation Phases

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| 1 | Foundation | Directory structure, capability manifest, state.md |
| 2 | Planning System | Plan/task parsing, CLI commands |
| 3 | Flows & CLI | Core flows, extended CLI |
| 4 | Template & Docs | Updated cookiecutter, documentation |
| 5 | Orchestration | Provider routing (optional for MVP) |

---

## References

### Internal
- ADR 0001: Context Loop design
- `/context/agents.md`: Development workflow
- `/tools/cli/README.md`: Current CLI documentation

### External
- [obra/superpowers](https://github.com/obra/superpowers) — Skill/flow patterns
- Anthropic Claude documentation — Prompt caching, effort parameter
- OpenAI Codex documentation — Compaction, long-running tasks
