# PairCoder v2.4 Feature Matrix

> Generated from Sprint 1-11 audit on 2025-12-16

## CLI Commands Summary

| Group | Commands | Count |
|-------|----------|-------|
| Core | init, feature, pack, context-sync, status, validate, ci | 7 |
| Planning | plan new/list/show/tasks/status/sync-trello/add-task | 7 |
| Tasks | task list/show/update/next/archive/restore/list-archived/cleanup/changelog-preview | 9 |
| Flows | flow list/show/run/validate | 4 |
| Orchestration | orchestrate task/analyze/handoff | 3 |
| Metrics | metrics summary/task/breakdown/budget/export | 5 |
| Timer | timer start/stop/status/show/summary | 5 |
| Benchmark | benchmark run/results/compare/list | 4 |
| Cache | cache stats/clear/invalidate | 3 |
| Trello | trello connect/status/disconnect/boards/use-board/lists/config | 7 |
| Trello Tasks | ttask list/show/start/done/block/comment/move | 7 |
| MCP | mcp serve/tools/test | 3 |
| **Total** | | **64** |

## Features by Sprint

### Sprint 1-3: Foundation (v2.0)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| v2 directory structure | `bpsai-pair init` | ✅ Works | Creates .paircoder/ and .claude/ |
| LLM capability manifest | - | ✅ Exists | .paircoder/capabilities.yaml |
| Context files | - | ✅ Exists | project.md, workflow.md, state.md |
| ADR documentation | - | ✅ Exists | docs/architecture/ |
| Flow parser | `flow list/show/run` | ✅ Works | .flow.md format |

### Sprint 4: Planning System (v2.0)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Plan YAML parser | - | ✅ Works | .plan.yaml format |
| Task YAML+MD parser | - | ✅ Works | .task.md format |
| Plan commands | `plan new/list/show/tasks/add-task` | ✅ Works | Full CRUD |
| Task commands | `task list/show/update/next` | ✅ Works | Status management |

### Sprint 5: Claude Code Alignment (v2.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Skills (SKILL.md) | - | ✅ Exists | 6 skills in .claude/skills/ |
| Custom subagents | - | ✅ Exists | planner.md, reviewer.md |
| AGENTS.md | - | ✅ Exists | Universal entry point |
| CLAUDE.md | - | ✅ Exists | Claude Code pointer |

### Sprint 6: Multi-Agent Orchestration (v2.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Orchestrator service | `orchestrate task/analyze/handoff` | ✅ Works | Model routing |
| Complexity analysis | `orchestrate analyze` | ✅ Works | Routing recommendation |
| Handoff packages | `orchestrate handoff` | ✅ Works | Agent transitions |

### Sprint 7: Lifecycle & Analytics (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Task archival | `task archive/restore/list-archived/cleanup` | ✅ Works | .gz compression |
| Changelog generation | `task changelog-preview` | ✅ Works | From archived tasks |
| Token tracking | `metrics summary/task/breakdown` | ✅ Works | JSONL storage |
| Cost estimation | `metrics budget` | ✅ Works | Model pricing |
| Metrics export | `metrics export` | ✅ Works | CSV format |
| Time tracking | `timer start/stop/status/show/summary` | ✅ Works | Toggl integration |
| Benchmarking | `benchmark run/results/compare/list` | ✅ Works | YAML suites |

### Sprint 8: Consolidation (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Doc consolidation | - | ✅ Done | docs/ directory |
| Template cleanup | - | ✅ Done | Removed prompts/ |

### Sprint 9: Prompt Caching (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Context cache | `cache stats/clear/invalidate` | ✅ Works | mtime-based |
| Lite pack | `pack --lite` | ✅ Works | For Codex 32KB limit |

### Sprint 10: Trello Integration (v2.3)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Trello connection | `trello connect/status/disconnect` | ✅ Works | API key + token |
| Board management | `trello boards/use-board/lists/config` | ✅ Works | Board selection |
| Task operations | `ttask list/show/start/done/block/comment/move` | ✅ Works | Card management |
| Trello skills | - | ✅ Exists | trello-task-workflow, trello-aware-planning |

### Sprint 11: MCP Server (v2.4)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| MCP server | `mcp serve` | ✅ Works | stdio transport |
| MCP tools list | `mcp tools` | ✅ Works | 13 tools |
| MCP tool testing | `mcp test` | ✅ Works | Local testing |
| Plan-to-Trello sync | `plan sync-trello` | ✅ Works | Creates cards |
| Plan status | `plan status` | ✅ Works | Task breakdown |
| Auto-hooks | - | ✅ Works | In config.yaml |

## MCP Tools (13 total)

| Tool | Description | Parameters |
|------|-------------|------------|
| paircoder_task_list | List tasks with filters | status, plan, sprint |
| paircoder_task_next | Get next recommended task | - |
| paircoder_task_start | Start a task | task_id, agent |
| paircoder_task_complete | Complete a task | task_id, summary |
| paircoder_context_read | Read project context files | file |
| paircoder_plan_status | Get plan status | plan_id |
| paircoder_plan_list | List available plans | - |
| paircoder_orchestrate_analyze | Analyze task complexity | task_id, context, prefer_agent |
| paircoder_orchestrate_handoff | Create handoff package | task_id, from_agent, to_agent, progress_summary |
| paircoder_metrics_record | Record token usage | task_id, agent, model, input_tokens, output_tokens |
| paircoder_metrics_summary | Get metrics summary | scope, scope_id |
| paircoder_trello_sync_plan | Sync plan to Trello | plan_id, board_id, create_lists, link_cards |
| paircoder_trello_update_card | Update Trello card | task_id, action, comment |

## Skills (6 total)

| Skill | Purpose | Triggers |
|-------|---------|----------|
| design-plan-implement | Feature development workflow | "design", "plan", "feature" |
| tdd-implement | Test-driven implementation | "fix", "bug", "test" |
| code-review | Code review workflow | "review", "check", "PR" |
| finish-branch | Branch completion workflow | "finish", "merge", "complete" |
| trello-task-workflow | Work on Trello tasks | "work on task", "TRELLO-" |
| trello-aware-planning | Create plans synced to Trello | "plan feature", "create tasks" |

## Hooks (6 built-in)

| Hook | Event | Description |
|------|-------|-------------|
| start_timer | on_task_start | Start time tracking |
| stop_timer | on_task_complete | Stop time tracking |
| record_metrics | on_task_complete | Record token usage |
| sync_trello | on_task_start/complete/block | Update Trello card |
| update_state | on_task_start/complete/block | Refresh state.md |
| check_unblocked | on_task_complete | Find unblocked tasks |

## Project Structure

```
my-project/
├── .paircoder/                    # PairCoder data
│   ├── config.yaml               # Project configuration
│   ├── capabilities.yaml         # LLM capability manifest
│   ├── context/                  # Project context files
│   │   ├── project.md           # Project overview
│   │   ├── workflow.md          # Workflow guidelines
│   │   └── state.md             # Current state
│   ├── flows/                    # Workflow definitions
│   ├── plans/                    # Plan files (.plan.yaml)
│   ├── tasks/                    # Task files (.task.md)
│   └── history/                  # Archives, metrics
├── .claude/                       # Claude Code native
│   ├── skills/                   # Model-invoked skills
│   │   ├── design-plan-implement/SKILL.md
│   │   ├── tdd-implement/SKILL.md
│   │   ├── code-review/SKILL.md
│   │   ├── finish-branch/SKILL.md
│   │   ├── trello-task-workflow/SKILL.md
│   │   └── trello-aware-planning/SKILL.md
│   └── agents/                   # Custom subagents
│       ├── planner.md
│       └── reviewer.md
├── AGENTS.md                      # Universal AI entry point
├── CLAUDE.md                      # Claude Code pointer
└── docs/                          # Documentation
```

## Configuration (config.yaml)

```yaml
version: "2.4"

project:
  name: "project-name"
  description: "Project description"
  primary_goal: "Main objective"
  coverage_target: 80

workflow:
  default_branch_type: "feature"
  main_branch: "main"
  context_dir: ".paircoder/context"
  flows_dir: ".paircoder/flows"
  plans_dir: ".paircoder/plans"
  tasks_dir: ".paircoder/tasks"

models:
  navigator: claude-opus-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5

routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }

metrics:
  enabled: true
  store_path: .paircoder/history/metrics.jsonl

hooks:
  enabled: true
  on_task_start:
    - start_timer
    - sync_trello
    - update_state
  on_task_complete:
    - stop_timer
    - record_metrics
    - sync_trello
    - update_state
    - check_unblocked
  on_task_block:
    - sync_trello
    - update_state
```

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Core CLI | 50+ | ✅ Pass |
| Planning | 40+ | ✅ Pass |
| Orchestration | 20+ | ✅ Pass |
| Metrics | 20+ | ✅ Pass |
| Time Tracking | 15+ | ✅ Pass |
| Benchmarks | 15+ | ✅ Pass |
| Cache | 14 | ✅ Pass |
| Trello | 21 | ✅ Pass |
| MCP | 29 | ✅ Pass |
| **Total** | **245** | ✅ Pass |
