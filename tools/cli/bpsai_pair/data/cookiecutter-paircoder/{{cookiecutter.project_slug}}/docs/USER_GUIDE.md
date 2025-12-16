# {{ cookiecutter.project_name }} - PairCoder Guide

This project uses **PairCoder v2** for AI-augmented pair programming.

## Quick Start

```bash
# Check status
bpsai-pair status

# List available flows
bpsai-pair flow list

# Create a plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# Work on a task
bpsai-pair task next
bpsai-pair task update TASK-001 --status in_progress
```

## Key Files

| File | Purpose |
|------|---------|
| `.paircoder/capabilities.yaml` | What AI agents can do |
| `.paircoder/context/state.md` | Current status |
| `.paircoder/context/project.md` | Project overview |
| `.paircoder/config.yaml` | Configuration |

## Commands Reference

### Planning

```bash
bpsai-pair plan new <slug> --type feature
bpsai-pair plan list
bpsai-pair plan show <id>
bpsai-pair plan add-task <id> --id TASK-XXX --title "..."
```

### Tasks

```bash
bpsai-pair task list
bpsai-pair task show <id>
bpsai-pair task update <id> --status done
bpsai-pair task next
```

### Flows

```bash
bpsai-pair flow list
bpsai-pair flow show <name>
bpsai-pair flow run <name>
```

### Context

```bash
bpsai-pair context-sync --last "..." --next "..."
bpsai-pair pack
```

## Working with AI

1. AI agents read `AGENTS.md` or `CLAUDE.md` at repo root
2. They check `.paircoder/capabilities.yaml` to understand what they can do
3. They read `.paircoder/context/state.md` for current status
4. They follow flows when appropriate

## More Information

See the full [PairCoder User Guide](https://github.com/bps-ai/paircoder/blob/main/tools/cli/USER_GUIDE.md).
