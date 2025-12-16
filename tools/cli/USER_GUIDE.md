# PairCoder User Guide

## Overview

PairCoder is an AI-augmented pair programming framework that provides structure and workflow for collaboration between developers and AI coding agents (Claude, GPT, Codex, etc.). It introduces conventions for maintaining project memory, tracking development progress, and ensuring quality through defined workflows.

### What's New in v2

- **`.paircoder/` directory** - Centralized configuration, context, and workflows
- **Planning system** - Plans with goals, tasks, and sprints
- **Flows** - Defined workflows for common development patterns
- **LLM capability manifest** - Tells AI agents what they can do and when
- **Enhanced CLI** - New `plan`, `task`, and `flow` commands

### Key Features

| Feature | Description |
|---------|-------------|
| **Planning System** | Create plans with goals, break into tasks, track progress |
| **Flows** | Structured workflows (TDD, design-plan-implement, review) |
| **Context Management** | Project state, what was done, what's next |
| **LLM Integration** | Capability manifest tells AI what it can do |
| **Quality Gates** | Pre-commit hooks, linting, secret scanning |
| **CLI Tool** | `bpsai-pair` for all operations |

## Installation

### Requirements

- **Python 3.9+**
- **Git** (for branch management)
- **Virtual Environment** (recommended)

### Install from PyPI

```bash
pip install bpsai-pair
```

### Development Install

```bash
git clone https://github.com/bps-ai/paircoder.git
cd paircoder
python3 -m venv .venv && source .venv/bin/activate
pip install -e tools/cli
```

### Verify Installation

```bash
bpsai-pair --version
bpsai-pair --help
```

## Directory Structure

### v2 Structure (`.paircoder/`)

```
your-project/
├── .paircoder/                    # PairCoder configuration
│   ├── config.yaml                # Project configuration
│   ├── capabilities.yaml          # LLM capability manifest
│   ├── context/
│   │   ├── project.md             # Project overview & constraints
│   │   ├── workflow.md            # Development workflow
│   │   └── state.md               # Current state & progress
│   ├── flows/
│   │   ├── tdd-implement.flow.md  # TDD workflow
│   │   ├── design-plan-implement.flow.md
│   │   ├── review.flow.md
│   │   └── finish-branch.flow.md
│   ├── plans/                     # Plan files
│   │   └── plan-YYYY-MM-slug.plan.yaml
│   └── tasks/                     # Task files by plan
│       └── plan-slug/
│           └── TASK-001.task.md
├── AGENTS.md                      # Root pointer for AI agents
├── CLAUDE.md                      # Root pointer for Claude Code
└── context/                       # Legacy context (optional)
    ├── development.md
    └── project_tree.md
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `config.yaml` | Project settings, model routing, enabled flows |
| `capabilities.yaml` | Tells LLMs what they can do and when |
| `context/project.md` | Project overview, tech stack, constraints |
| `context/workflow.md` | Development process, standards, gates |
| `context/state.md` | Current plan, tasks, what's next |
| `AGENTS.md` | Entry point for any AI agent |
| `CLAUDE.md` | Entry point for Claude Code specifically |

## CLI Commands

### Status & Info

```bash
# Show overall status
bpsai-pair status

# Validate project structure
bpsai-pair validate

# Show version
bpsai-pair --version
```

### Planning Commands

```bash
# Create a new plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# List all plans
bpsai-pair plan list

# Show plan details
bpsai-pair plan show plan-2025-01-my-feature

# List tasks for a plan
bpsai-pair plan tasks plan-2025-01-my-feature

# Add a task to a plan
bpsai-pair plan add-task plan-2025-01-my-feature \
    --id TASK-001 \
    --title "Implement login form" \
    --priority P1 \
    --complexity 50
```

### Task Commands

```bash
# List all tasks
bpsai-pair task list

# List tasks for a specific plan
bpsai-pair task list --plan plan-2025-01-my-feature

# Show task details
bpsai-pair task show TASK-001

# Update task status
bpsai-pair task update TASK-001 --status in_progress
bpsai-pair task update TASK-001 --status done

# Get next task to work on
bpsai-pair task next
```

### Flow Commands

```bash
# List available flows
bpsai-pair flow list

# Show flow details
bpsai-pair flow show tdd-implement

# Run a flow (display steps)
bpsai-pair flow run tdd-implement

# Validate a flow
bpsai-pair flow validate tdd-implement
```

### Context Commands

```bash
# Update context sync
bpsai-pair context-sync \
    --last "Implemented login form" \
    --next "Add validation" \
    --blockers "None"

# Package context for AI handoff
bpsai-pair pack

# Package with extra files
bpsai-pair pack --extra README.md docs/API.md
```

### Feature Branch Commands

```bash
# Create a feature branch
bpsai-pair feature login-system \
    --primary "Implement user authentication" \
    --phase "Phase 1: Basic login flow"

# Branch types: feature, fix, refactor, chore
bpsai-pair feature --type fix bug-123 --primary "Fix null pointer"
```

### Initialization

```bash
# Initialize in existing repo
bpsai-pair init

# Initialize with custom template path
bpsai-pair init path/to/template
```

## Planning System

### Creating a Plan

Plans organize work into goals and tasks:

```bash
bpsai-pair plan new user-auth --type feature --title "User Authentication"
```

This creates `.paircoder/plans/plan-YYYY-MM-user-auth.plan.yaml`.

### Plan Structure

```yaml
id: plan-2025-01-user-auth
title: User Authentication
type: feature
status: planned
created_at: 2025-01-15
owner: developer

goals:
  - Implement secure login flow
  - Add session management
  - Support OAuth providers

sprints:
  - id: sprint-1
    title: Basic Auth
    goal: Implement username/password login
    task_ids: [TASK-001, TASK-002, TASK-003]

tasks:
  - id: TASK-001
    title: Create login form
    priority: P0
    complexity: 30
    type: feature
```

### Task Files

Each task can have a detailed file in `.paircoder/tasks/<plan-slug>/TASK-XXX.task.md`:

```markdown
---
id: TASK-001
title: Create login form
plan_id: plan-2025-01-user-auth
type: feature
priority: P0
complexity: 30
status: pending
sprint: sprint-1
tags: [ui, auth]
---

# TASK-001: Create login form

## Objective
Create a responsive login form with username and password fields.

## Acceptance Criteria
- [ ] Form validates input
- [ ] Shows error messages
- [ ] Submits to auth endpoint

## Technical Notes
- Use React Hook Form
- Follow existing form patterns
```

### Task Status Flow

```
pending → in_progress → done
                ↓
            blocked → cancelled
```

Update status:
```bash
bpsai-pair task update TASK-001 --status in_progress
# ... do the work ...
bpsai-pair task update TASK-001 --status done
```

## Flows (Workflows)

Flows are structured workflows for common development patterns.

### Available Flows

| Flow | When to Use |
|------|-------------|
| `design-plan-implement` | New features requiring design |
| `tdd-implement` | Bug fixes, implementing tasks |
| `review` | Code review before merge |
| `finish-branch` | Complete work, prepare PR |

### Flow Structure

Flows use YAML frontmatter + Markdown body (`.flow.md`):

```markdown
---
name: tdd-implement
version: 1
description: Test-Driven Development workflow
triggers: [bugfix, implement_task]
roles:
  driver: { primary: true }
---

# TDD Implementation Flow

## Phase 1 - Red (Write Failing Test)
1. Identify what to test
2. Write the test
3. Run and confirm failure

## Phase 2 - Green (Make Test Pass)
1. Write minimal code
2. Run test
3. Confirm pass

## Phase 3 - Refactor
1. Improve code
2. Keep tests green
```

### Running Flows

```bash
# View flow steps
bpsai-pair flow run tdd-implement

# With variables
bpsai-pair flow run tdd-implement --var task=TASK-001
```

## LLM Integration

### Capability Manifest

The `.paircoder/capabilities.yaml` file tells AI agents what they can do:

```yaml
version: "2.0"
name: my-project

context_files:
  project: .paircoder/context/project.md
  workflow: .paircoder/context/workflow.md
  state: .paircoder/context/state.md

capabilities:
  - id: create_plan
    name: "Create a new plan"
    when_to_use:
      - User describes a feature
      - User says "let's plan"
    how_to_invoke:
      cli: "bpsai-pair plan new <slug>"
    flow_to_run: design-plan-implement

flow_triggers:
  - trigger: "user_describes_feature"
    patterns: ["build a", "create a", "add a"]
    suggested_flow: design-plan-implement
```

### Root Pointer Files

`AGENTS.md` and `CLAUDE.md` at repo root guide AI agents to read:
1. `.paircoder/capabilities.yaml` - what they can do
2. `.paircoder/context/state.md` - current status
3. Check if a flow applies to the request

### Roles

AI agents can operate in different roles:

| Role | Purpose |
|------|---------|
| **Navigator** | Planning, design, asking clarifying questions |
| **Driver** | Writing code, implementing tasks, running tests |
| **Reviewer** | Code review, quality checks, verification |

## Day-to-Day Workflow

### 1. Starting a New Feature

```bash
# Create a plan
bpsai-pair plan new user-profile --type feature --title "User Profile Page"

# Add tasks
bpsai-pair plan add-task plan-2025-01-user-profile \
    --id TASK-001 --title "Design profile layout" --priority P0

# Create feature branch
bpsai-pair feature user-profile --primary "Implement user profile page"

# Check what's next
bpsai-pair task next
```

### 2. Working on a Task

```bash
# Start the task
bpsai-pair task update TASK-001 --status in_progress

# Use TDD flow
bpsai-pair flow run tdd-implement

# ... implement with tests ...

# Mark done
bpsai-pair task update TASK-001 --status done

# Update context
bpsai-pair context-sync \
    --last "Implemented profile layout" \
    --next "Add profile editing"
```

### 3. Working with AI

```bash
# Package context for AI
bpsai-pair pack

# Share with AI agent, or use Claude Code with CLAUDE.md
# AI reads .paircoder/capabilities.yaml to understand what it can do
# AI reads .paircoder/context/state.md to see current status
```

### 4. Finishing Work

```bash
# Run review flow
bpsai-pair flow run review

# Finish branch
bpsai-pair flow run finish-branch

# Update final status
bpsai-pair context-sync \
    --last "Completed user profile feature" \
    --next "Create PR and merge"
```

## Configuration

### config.yaml

```yaml
version: "2.0"

project:
  name: "my-project"
  description: "My awesome project"
  primary_goal: "Build the thing"
  coverage_target: 80

workflow:
  default_branch_type: "feature"
  main_branch: "main"
  context_dir: ".paircoder/context"
  flows_dir: ".paircoder/flows"

models:
  navigator: claude-sonnet-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5

routing:
  by_complexity:
    trivial: { max_score: 20, model: claude-haiku-4-5 }
    simple: { max_score: 40, model: claude-haiku-4-5 }
    moderate: { max_score: 60, model: claude-sonnet-4-5 }
    complex: { max_score: 80, model: claude-opus-4-5 }

flows:
  enabled:
    - design-plan-implement
    - tdd-implement
    - review
    - finish-branch
```

### Environment Variables

```bash
# Override project name
export PAIRCODER_PROJECT_NAME="my-project"

# Override primary goal
export PAIRCODER_PRIMARY_GOAL="Ship v2"
```

## Quality Gates

### Pre-commit Hooks

PairCoder includes `.pre-commit-config.yaml` for:
- Ruff (Python linting/formatting)
- Prettier (Markdown, JSON, YAML)
- Gitleaks (secret scanning)

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI/CD

GitHub Actions workflows included:
- `ci.yml` - Run tests, linting on push/PR
- `project_tree.yml` - Auto-update project tree snapshot

## Migration from v1

If you have an existing v1 PairCoder project:

1. The old `context/` directory is still supported
2. Run `bpsai-pair init` to add `.paircoder/` structure
3. Migrate content from `context/development.md` to `.paircoder/context/state.md`
4. Update `AGENTS.md` and `CLAUDE.md` to point to `.paircoder/`

## Troubleshooting

### Command Not Found

```bash
# Use module invocation
python -m bpsai_pair.cli --help
```

### No .paircoder Directory

```bash
# Initialize first
bpsai-pair init
```

### Plan/Task Not Found

```bash
# List available plans
bpsai-pair plan list

# Check task with plan context
bpsai-pair task show TASK-001 --plan plan-2025-01-my-feature
```

## Platform Support

PairCoder v2 is fully supported on:
- Linux
- macOS
- Windows

All features work identically across platforms.

## Getting Help

- Run `bpsai-pair --help` for command list
- Run `bpsai-pair <command> --help` for command options
- Check `.paircoder/capabilities.yaml` for what AI can do
- Report issues: https://github.com/bps-ai/paircoder/issues
