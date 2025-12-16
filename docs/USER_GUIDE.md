# PairCoder v2.4 User Guide

> Complete documentation for the AI-augmented pair programming framework

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Concepts](#core-concepts)
5. [Project Structure](#project-structure)
6. [Planning System](#planning-system)
7. [Flows & Skills](#flows--skills)
8. [Orchestration](#orchestration)
9. [Metrics & Analytics](#metrics--analytics)
10. [Time Tracking](#time-tracking)
11. [Benchmarking](#benchmarking)
12. [Caching](#caching)
13. [Trello Integration](#trello-integration)
14. [MCP Server](#mcp-server)
15. [Auto-Hooks](#auto-hooks)
16. [CLI Reference](#cli-reference)
17. [Configuration Reference](#configuration-reference)
18. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is PairCoder?

PairCoder is a repo-native toolkit for pairing with AI coding agents (Claude, GPT, Codex, Gemini). It provides:

- **Structured context** — Project memory in `.paircoder/` that AI agents can read and update
- **Planning workflows** — Plans, sprints, and tasks with YAML+Markdown format
- **Skills & flows** — Reusable workflow templates for common patterns
- **Multi-agent orchestration** — Route tasks to the right AI based on complexity
- **Analytics** — Token tracking, cost estimation, time tracking
- **Integrations** — Trello for visual task boards, MCP for Claude Desktop

### Philosophy

PairCoder treats AI as a **pair programming partner**:
- The AI navigates (plans, designs, reviews)
- You drive (approve, implement, test)
- Context is shared via standardized files

### v2 vs v1

| Aspect | v1 | v2 |
|--------|----|----|
| Structure | Scattered files | `.paircoder/` directory |
| Planning | None | Full planning system |
| Skills | None | Claude Code native skills |
| Orchestration | Manual | Automatic routing |
| Analytics | None | Token/cost/time tracking |

---

## Installation

### Basic Install

```bash
pip install bpsai-pair
bpsai-pair --version  # Should show 2.4.0
```

### With MCP Support

```bash
pip install 'bpsai-pair[mcp]'
```

### Development Install

```bash
git clone https://github.com/yourusername/paircoder.git
cd paircoder/tools/cli
pip install -e .
pytest -v  # 245 tests
```

### Verify Installation

```bash
bpsai-pair --help
bpsai-pair status
```

---

## Getting Started

### Initialize a New Project

```bash
bpsai-pair init my-project
cd my-project
```

### Initialize an Existing Project

```bash
cd your-project
bpsai-pair init .
```

### Your First Workflow

1. **Create a plan**
   ```bash
   bpsai-pair plan new my-feature --type feature --title "My Feature"
   ```

2. **Add tasks**
   ```bash
   bpsai-pair plan add-task plan-2025-12-my-feature \
     --id TASK-001 --title "Implement core logic"
   ```

3. **Check status**
   ```bash
   bpsai-pair plan status
   ```

4. **Work on tasks**
   ```bash
   bpsai-pair task next
   bpsai-pair task update TASK-001 --status in_progress
   # ... do the work ...
   bpsai-pair task update TASK-001 --status done
   ```

5. **Archive completed work**
   ```bash
   bpsai-pair task archive --completed
   ```

---

## Core Concepts

### Context Loop

The context loop is how PairCoder maintains project understanding:

1. **Read** — AI reads `project.md`, `workflow.md`, `state.md`
2. **Work** — AI performs tasks, writes code
3. **Update** — AI updates `state.md` with progress
4. **Persist** — Changes are committed to repo

### Plans & Tasks

**Plans** are high-level goals:
```yaml
# .paircoder/plans/plan-2025-12-feature.plan.yaml
id: plan-2025-12-feature
title: Add new feature
type: feature
status: in_progress
goals:
  - Implement core functionality
  - Add tests
  - Update documentation
sprints:
  - id: sprint-1
    title: Core Implementation
    task_ids: [TASK-001, TASK-002]
```

**Tasks** are specific work items:
```yaml
# .paircoder/tasks/feature/TASK-001.task.md
---
id: TASK-001
plan: plan-2025-12-feature
title: Implement core logic
status: pending
priority: P0
complexity: 50
sprint: sprint-1
---

# Objective
Implement the core business logic for the feature.

# Implementation Plan
- Create service class
- Add database models
- Write unit tests

# Verification
- [ ] Tests pass
- [ ] Code reviewed
```

### Flows

Flows are workflow templates in `.paircoder/flows/`:
```markdown
# .paircoder/flows/tdd-implement.flow.md
---
name: tdd-implement
description: Test-driven implementation
triggers: ["fix", "bug", "test"]
---

## Steps
1. Write failing test
2. Implement minimum code
3. Refactor
4. Verify all tests pass
```

### Skills

Skills are Claude Code native workflows in `.claude/skills/`:
```markdown
# .claude/skills/tdd-implement/SKILL.md
---
name: TDD Implementation
triggers: ["fix", "bug", "test"]
---

## When to Use
Use this skill when fixing bugs or implementing features with tests.

## Steps
1. Understand the requirement
2. Write failing test
3. Implement solution
4. Verify tests pass

## Recording Your Work
After completing work:
- CLI: `bpsai-pair task update TASK-XXX --status done`
- MCP: Call `paircoder_task_complete` tool
```

---

## Project Structure

### .paircoder/ Directory

```
.paircoder/
├── config.yaml           # Project configuration
├── capabilities.yaml     # LLM capability manifest
├── context/
│   ├── project.md       # Project overview, goals, constraints
│   ├── workflow.md      # How work is done here
│   └── state.md         # Current state, active tasks
├── flows/               # Workflow definitions (.flow.md)
├── plans/               # Plan files (.plan.yaml)
├── tasks/               # Task files (.task.md)
│   └── <plan-slug>/     # Tasks grouped by plan
└── history/             # Archives, metrics
    ├── archives/        # Archived task files
    ├── metrics.jsonl    # Token/cost tracking
    └── manifest.json    # Archive manifest
```

### .claude/ Directory

```
.claude/
├── skills/              # Claude Code skills
│   ├── design-plan-implement/SKILL.md
│   ├── tdd-implement/SKILL.md
│   ├── code-review/SKILL.md
│   ├── finish-branch/SKILL.md
│   ├── trello-task-workflow/SKILL.md
│   └── trello-aware-planning/SKILL.md
├── agents/              # Custom subagents
│   ├── planner.md      # Planning specialist
│   └── reviewer.md     # Code review specialist
└── settings.json        # Claude Code settings
```

### Root Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Universal AI entry point - works with any agent |
| `CLAUDE.md` | Claude Code specific pointer |

---

## Planning System

### Creating Plans

```bash
# Create a feature plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# Create a bugfix plan
bpsai-pair plan new fix-issue-123 --type bugfix --title "Fix login bug"

# With goals
bpsai-pair plan new my-feature \
  --goal "Implement core logic" \
  --goal "Add comprehensive tests"
```

### Managing Plans

```bash
# List all plans
bpsai-pair plan list

# Show plan details
bpsai-pair plan show plan-2025-12-my-feature

# Show plan with tasks
bpsai-pair plan tasks plan-2025-12-my-feature

# Show plan status with progress
bpsai-pair plan status plan-2025-12-my-feature
# or for active plan:
bpsai-pair plan status
```

### Adding Tasks

```bash
bpsai-pair plan add-task plan-2025-12-my-feature \
  --id TASK-001 \
  --title "Implement core logic" \
  --type feature \
  --priority P0 \
  --complexity 50 \
  --sprint sprint-1
```

### Task Lifecycle

```
pending → in_progress → done
                     ↘ blocked → pending (when unblocked)
                     ↘ cancelled
```

```bash
# Get next recommended task
bpsai-pair task next

# Start working
bpsai-pair task update TASK-001 --status in_progress

# Mark complete
bpsai-pair task update TASK-001 --status done

# Mark blocked
bpsai-pair task update TASK-001 --status blocked
```

### Archiving Tasks

```bash
# Archive specific task
bpsai-pair task archive TASK-001

# Archive all completed
bpsai-pair task archive --completed

# Archive by sprint
bpsai-pair task archive --sprint sprint-1

# Restore from archive
bpsai-pair task restore TASK-001

# List archived
bpsai-pair task list-archived

# Preview changelog
bpsai-pair task changelog-preview --sprint sprint-1 --version v1.0.0

# Clean old archives (90 days default)
bpsai-pair task cleanup --retention 90
```

---

## Flows & Skills

### Using Flows

```bash
# List available flows
bpsai-pair flow list

# Show flow details
bpsai-pair flow show tdd-implement

# Run a flow (renders steps)
bpsai-pair flow run tdd-implement

# Validate flow syntax
bpsai-pair flow validate tdd-implement
```

### Available Skills

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `design-plan-implement` | "design", "plan", "feature" | Feature development |
| `tdd-implement` | "fix", "bug", "test" | Test-driven implementation |
| `code-review` | "review", "check", "PR" | Code review workflow |
| `finish-branch` | "finish", "merge", "complete" | Branch completion |
| `trello-task-workflow` | "work on task", "TRELLO-" | Trello task execution |
| `trello-aware-planning` | "plan feature", "create tasks" | Planning with Trello |

---

## Orchestration

### Model Routing

PairCoder routes tasks to appropriate models based on complexity:

```yaml
# In config.yaml
routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }
```

### Orchestration Commands

```bash
# Route a task to best agent
bpsai-pair orchestrate task TASK-001

# Analyze without executing
bpsai-pair orchestrate analyze TASK-001

# Create handoff package for another agent
bpsai-pair orchestrate handoff TASK-001 \
  --from claude-code --to codex \
  --progress "Completed step 1 and 2"
```

---

## Metrics & Analytics

### Token Tracking

```bash
# Session/daily summary
bpsai-pair metrics summary

# Task-specific metrics
bpsai-pair metrics task TASK-001

# Breakdown by dimension
bpsai-pair metrics breakdown --by agent
bpsai-pair metrics breakdown --by model
bpsai-pair metrics breakdown --by task
```

### Budget Management

```bash
# Check budget status
bpsai-pair metrics budget

# Export metrics
bpsai-pair metrics export --format csv --output metrics.csv
```

### Metrics Storage

Metrics are stored in `.paircoder/history/metrics.jsonl`:
```json
{"timestamp": "2025-12-16T10:00:00", "agent": "claude-code", "model": "claude-sonnet-4-5", "input_tokens": 1500, "output_tokens": 800, "cost_usd": 0.0115}
```

---

## Time Tracking

### Built-in Timer

```bash
# Start timer for a task
bpsai-pair timer start TASK-001

# Check current timer
bpsai-pair timer status

# Stop timer
bpsai-pair timer stop

# View time entries for a task
bpsai-pair timer show TASK-001

# Summary across tasks
bpsai-pair timer summary --plan plan-2025-12-feature
```

### Toggl Integration

Configure in `config.yaml`:
```yaml
time_tracking:
  provider: toggl
  api_token: ${TOGGL_API_TOKEN}
  workspace_id: 12345
```

---

## Benchmarking

### Running Benchmarks

```bash
# Run default benchmark suite
bpsai-pair benchmark run --suite default

# View latest results
bpsai-pair benchmark results --latest

# Compare two agents
bpsai-pair benchmark compare claude-code codex

# List available benchmarks
bpsai-pair benchmark list
```

### Benchmark Suite Format

```yaml
# .paircoder/benchmarks/default.yaml
name: default
description: Standard benchmark suite
benchmarks:
  - id: simple-function
    description: Write a simple function
    prompt: "Write a function that adds two numbers"
    validation:
      - type: exists
        path: solution.py
      - type: contains
        path: solution.py
        pattern: "def add"
```

---

## Caching

### Context Cache

PairCoder caches context files for efficiency:

```bash
# View cache statistics
bpsai-pair cache stats

# Clear entire cache
bpsai-pair cache clear

# Invalidate specific file
bpsai-pair cache invalidate .paircoder/context/state.md
```

### Lite Pack for Codex

```bash
# Create minimal pack for 32KB context limit
bpsai-pair pack --lite
```

---

## Trello Integration

### Setup

1. Get API key from https://trello.com/app-key
2. Generate token from the API key page
3. Connect PairCoder:

```bash
bpsai-pair trello connect
# Enter API key and token when prompted
```

### Board Management

```bash
# Check connection
bpsai-pair trello status

# List boards
bpsai-pair trello boards

# Set active board
bpsai-pair trello use-board <board-id>

# View board lists
bpsai-pair trello lists

# View/modify config
bpsai-pair trello config --show
```

### Working with Trello Tasks

```bash
# List tasks from board
bpsai-pair ttask list

# Show task details
bpsai-pair ttask show <card-id>

# Start working (moves to In Progress)
bpsai-pair ttask start <card-id>

# Complete task (moves to Done)
bpsai-pair ttask done <card-id> --summary "Implemented feature X"

# Mark blocked
bpsai-pair ttask block <card-id> --reason "Waiting for API"

# Add comment
bpsai-pair ttask comment <card-id> --message "50% complete"

# Move to different list
bpsai-pair ttask move <card-id> --list "In Review"
```

### Plan-to-Trello Sync

```bash
# Preview sync
bpsai-pair plan sync-trello plan-2025-12-feature --dry-run

# Sync tasks to Trello
bpsai-pair plan sync-trello plan-2025-12-feature --board <board-id>
```

---

## MCP Server

### What is MCP?

MCP (Model Context Protocol) allows AI agents to call PairCoder tools directly. Claude Desktop and other MCP-compatible clients can use PairCoder autonomously.

### Installation

```bash
pip install 'bpsai-pair[mcp]'
```

### Starting the Server

```bash
# Start server (stdio transport)
bpsai-pair mcp serve

# List available tools
bpsai-pair mcp tools

# Test a tool locally
bpsai-pair mcp test paircoder_task_list
```

### Available Tools (13)

| Tool | Description | Parameters |
|------|-------------|------------|
| `paircoder_task_list` | List tasks with filters | status, plan, sprint |
| `paircoder_task_next` | Get next recommended task | - |
| `paircoder_task_start` | Start a task | task_id, agent |
| `paircoder_task_complete` | Complete a task | task_id, summary |
| `paircoder_context_read` | Read context files | file (state/project/workflow/config/capabilities) |
| `paircoder_plan_status` | Get plan progress | plan_id |
| `paircoder_plan_list` | List available plans | - |
| `paircoder_orchestrate_analyze` | Analyze task complexity | task_id, context, prefer_agent |
| `paircoder_orchestrate_handoff` | Create handoff package | task_id, from_agent, to_agent, progress_summary |
| `paircoder_metrics_record` | Record token usage | task_id, agent, model, input_tokens, output_tokens |
| `paircoder_metrics_summary` | Get metrics summary | scope, scope_id |
| `paircoder_trello_sync_plan` | Sync plan to Trello | plan_id, board_id, create_lists, link_cards |
| `paircoder_trello_update_card` | Update Trello card | task_id, action, comment |

### Claude Desktop Setup

See [MCP Setup Guide](MCP_SETUP.md) for detailed configuration.

---

## Auto-Hooks

### Configuration

Configure hooks in `.paircoder/config.yaml`:

```yaml
hooks:
  enabled: true
  on_task_start:
    - start_timer      # Start time tracking
    - sync_trello      # Update Trello card
    - update_state     # Refresh state.md
  on_task_complete:
    - stop_timer       # Stop time tracking
    - record_metrics   # Record token usage
    - sync_trello      # Update Trello card
    - update_state     # Refresh state.md
    - check_unblocked  # Find newly unblocked tasks
  on_task_block:
    - sync_trello      # Update Trello card
    - update_state     # Refresh state.md
```

### Available Hooks

| Hook | Description |
|------|-------------|
| `start_timer` | Start time tracking for task |
| `stop_timer` | Stop time tracking, calculate duration |
| `record_metrics` | Record token usage from context.extra |
| `sync_trello` | Update Trello card status |
| `update_state` | Reload and refresh state.md |
| `check_unblocked` | Find tasks unblocked by completion |

### Disabling Hooks

```yaml
hooks:
  enabled: false
```

---

## CLI Reference

### All Commands (64 total)

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

See [README.md](../README.md) for complete command details.

---

## Configuration Reference

### Full config.yaml Schema

```yaml
version: "2.4"

project:
  name: "my-project"
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

pack:
  default_name: "agent_pack.tgz"
  excludes:
    - ".git"
    - ".venv"
    - "__pycache__"
    - "node_modules"

models:
  navigator: claude-opus-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5
  providers:
    anthropic:
      models: [claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5]
    openai:
      models: [gpt-5.1-codex-max, gpt-5.1-codex]

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

flows:
  enabled:
    - design-plan-implement
    - tdd-implement
    - review
    - finish-branch
  triggers:
    feature_request: [design-plan-implement]
    bugfix: [tdd-implement]
    pre_merge: [review, finish-branch]

metrics:
  enabled: true
  store_path: .paircoder/history/metrics.jsonl

hooks:
  enabled: true
  on_task_start: [start_timer, sync_trello, update_state]
  on_task_complete: [stop_timer, record_metrics, sync_trello, update_state, check_unblocked]
  on_task_block: [sync_trello, update_state]

trello:
  board_id: null  # Set with `trello use-board`
  lists:
    backlog: "Backlog"
    in_progress: "In Progress"
    review: "In Review"
    done: "Done"
```

---

## Troubleshooting

### Common Issues

**Command not found**
```bash
# If bpsai-pair not on PATH:
python -m bpsai_pair.cli --help
```

**No .paircoder directory**
```bash
# Initialize the project
bpsai-pair init .
```

**Task not found**
```bash
# List all tasks to find ID
bpsai-pair task list
```

**MCP server won't start**
```bash
# Verify MCP extra installed
pip show mcp

# Test locally
bpsai-pair mcp test paircoder_task_list
```

**Trello not connected**
```bash
# Check status
bpsai-pair trello status

# Reconnect
bpsai-pair trello connect
```

### Debug Commands

```bash
# Validate repo structure
bpsai-pair validate

# Show current state
bpsai-pair status

# List all plans
bpsai-pair plan list

# Show cache state
bpsai-pair cache stats
```

### Getting Help

- GitHub Issues: https://github.com/anthropics/paircoder/issues
- Documentation: This guide and README.md
- MCP Setup: docs/MCP_SETUP.md

---

*PairCoder v2.4.0 - MIT License*
