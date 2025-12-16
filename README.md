# PairCoder — AI-Augmented Pair Programming Framework

PairCoder gives teams a **drop-in, repo-native toolkit** for pairing with AI coding agents (Claude, GPT, Codex, etc.). It standardizes project memory in `.paircoder/`, provides structured workflows via flows/skills, and ships a CLI to orchestrate the entire development lifecycle.

> **v2.1.0** — Planning system, multi-agent orchestration, lifecycle management

## What's New in v2

- **Planning System** — Create plans with goals, tasks, and sprints
- **Flows & Skills** — Structured workflows (TDD, design-plan-implement, review)
- **Multi-Agent Orchestration** — Route tasks to Claude Code, Codex CLI, or other agents
- **Lifecycle Management** — Archive completed tasks, generate changelogs
- **LLM Integration** — Capability manifest tells AI what it can do
- **`.paircoder/` Directory** — Centralized configuration and context

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

This creates the v2 structure:

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
├── .claude/
│   ├── skills/               # Claude Code skills
│   └── agents/               # Custom subagents
├── AGENTS.md                 # AI agent entry point
└── CLAUDE.md                 # Claude Code entry point
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
| `bpsai-pair task archive` | Archive completed tasks |
| `bpsai-pair task restore <id>` | Restore archived task |

### Flows

| Command | Description |
|---------|-------------|
| `bpsai-pair flow list` | List available flows |
| `bpsai-pair flow show <name>` | Show flow details |
| `bpsai-pair flow run <name>` | Run a flow |

### Orchestration (v2.2)

| Command | Description |
|---------|-------------|
| `bpsai-pair orchestrate task <id>` | Route task to best agent |
| `bpsai-pair orchestrate analyze <id>` | Show routing decision |
| `bpsai-pair metrics summary` | Show token/cost metrics |
| `bpsai-pair benchmark run` | Run benchmark suite |

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

## Windows & Cross-Platform

PairCoder is fully Python-backed (no Bash required):

```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Install and use
pip install bpsai-pair
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
pytest -v
```

### Build

```bash
python -m build
```

## Documentation

- [User Guide](docs/USER_GUIDE.md) — Full documentation
- [Changelog](CHANGELOG.md) — Version history

## Repository Structure

This repository serves two purposes:

1. **Package development** — The installable `bpsai-pair` CLI tool in `tools/cli/`
2. **Living example** — Demonstrating how to use PairCoder effectively

## Contributing

See **CONTRIBUTING.md**. Use Conventional Commits. Keep diffs small & reversible.

## Security

See **SECURITY.md**. No secrets in repo or agent packs.

## License

MIT
