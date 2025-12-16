# bpsai-pair CLI

The PairCoder CLI tool for AI pair programming workflows.

## What's New in v2

- **Planning System** - Create plans with goals, tasks, and sprints
- **Flows** - Structured workflows (TDD, design-plan-implement, review)
- **LLM Integration** - Capability manifest tells AI what it can do
- **`.paircoder/` Directory** - Centralized configuration and context

## Quick Start

### Install

```bash
pip install bpsai-pair
bpsai-pair --help
```

### Initialize a Project

```bash
cd your-project
bpsai-pair init
```

### Create a Plan

```bash
bpsai-pair plan new my-feature --type feature --title "My Feature"
```

### Work on Tasks

```bash
bpsai-pair task next
bpsai-pair task update TASK-001 --status in_progress
# ... do the work ...
bpsai-pair task update TASK-001 --status done
```

### Use Flows

```bash
bpsai-pair flow list
bpsai-pair flow run tdd-implement
```

## Commands

### Status & Info

| Command | Description |
|---------|-------------|
| `bpsai-pair status` | Show current state |
| `bpsai-pair validate` | Check repo structure |
| `bpsai-pair --version` | Show version |

### Planning

| Command | Description |
|---------|-------------|
| `bpsai-pair plan new <slug>` | Create a new plan |
| `bpsai-pair plan list` | List all plans |
| `bpsai-pair plan show <id>` | Show plan details |
| `bpsai-pair plan tasks <id>` | List tasks for a plan |
| `bpsai-pair plan add-task <id>` | Add a task to a plan |

### Tasks

| Command | Description |
|---------|-------------|
| `bpsai-pair task list` | List all tasks |
| `bpsai-pair task show <id>` | Show task details |
| `bpsai-pair task update <id>` | Update task status |
| `bpsai-pair task next` | Get next task to work on |

### Flows

| Command | Description |
|---------|-------------|
| `bpsai-pair flow list` | List available flows |
| `bpsai-pair flow show <name>` | Show flow details |
| `bpsai-pair flow run <name>` | Run a flow |
| `bpsai-pair flow validate <name>` | Validate a flow |

### Context

| Command | Description |
|---------|-------------|
| `bpsai-pair context-sync` | Update context loop |
| `bpsai-pair pack` | Package context for AI |
| `bpsai-pair pack --list` | Preview pack contents |

### Feature Branches

| Command | Description |
|---------|-------------|
| `bpsai-pair feature <name>` | Create feature branch |
| `bpsai-pair init` | Initialize repo structure |

## Examples

### Planning Workflow

```bash
# Create a plan
bpsai-pair plan new user-auth --type feature --title "User Authentication"

# Add tasks
bpsai-pair plan add-task plan-2025-01-user-auth \
    --id TASK-001 \
    --title "Create login form" \
    --priority P1

# Work on tasks
bpsai-pair task update TASK-001 --status in_progress
bpsai-pair flow run tdd-implement
bpsai-pair task update TASK-001 --status done

# Update context
bpsai-pair context-sync --last "Implemented login" --next "Add validation"
```

### Feature Branch Workflow

```bash
# Create branch with context
bpsai-pair feature auth-refactor \
    --type refactor \
    --primary "Decouple auth via DI" \
    --phase "Refactor auth module + tests"

# Pack context for AI
bpsai-pair pack --out agent_pack.tgz
```

## Project Structure

After initialization, your project will have:

```
your-project/
├── .paircoder/
│   ├── config.yaml           # Configuration
│   ├── capabilities.yaml     # LLM capabilities
│   ├── context/
│   │   ├── project.md        # Project overview
│   │   ├── workflow.md       # Development workflow
│   │   └── state.md          # Current state
│   ├── flows/                # Workflow definitions
│   ├── plans/                # Plan files
│   └── tasks/                # Task files
├── AGENTS.md                 # AI agent entry point
└── CLAUDE.md                 # Claude Code entry point
```

## Windows & Cross-Platform

PairCoder is fully Python-backed (no Bash required):

```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install
pip install bpsai-pair

# Use
bpsai-pair --help
```

If entry point is not on PATH:

```powershell
python -m bpsai_pair.cli --help
```

## Development

### Install for Development

```bash
cd tools/cli
pip install -e .
```

### Run Tests

```bash
pytest -v
```

### Build

```bash
python -m build
```

## Documentation

- [User Guide](USER_GUIDE.md) - Full documentation
- [Capabilities](../../.paircoder/capabilities.yaml) - LLM capability manifest

## License

MIT
