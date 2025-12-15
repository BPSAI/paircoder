# PairCoder - AI Agent Instructions

> **This is a pointer file.** Full context is in `.paircoder/`

## Quick Start for AI Agents

1. **Read capabilities**: `.paircoder/capabilities.yaml`
2. **Understand project**: `.paircoder/context/project.md`
3. **Check current state**: `.paircoder/context/state.md`
4. **Follow workflows**: `.paircoder/context/workflow.md`

## What You Can Do

See `.paircoder/capabilities.yaml` for the full list. Key capabilities:

- **Create plans** for features, bugs, refactors
- **Run flows** for structured work (design, implement, review)
- **Update state** to track progress
- **Pack context** for handoff

## Current Status

Check `.paircoder/context/state.md` for:
- Active plan and sprint
- Task statuses
- What was just done
- What's next
- Any blockers

## Project Structure

```
.paircoder/           # All PairCoder system files
├── config.yaml       # Configuration
├── capabilities.yaml # What you can do
├── context/          # Project memory
├── flows/            # Workflow definitions
├── plans/            # Active plans
└── tasks/            # Task files

tools/cli/            # CLI package source
docs/adr/             # Architecture decisions
```

## How to Help

1. Read the context files listed above
2. Check if a flow applies to the user's request
3. Suggest or run the appropriate flow
4. Update `state.md` after completing work

## CLI Commands

```bash
bpsai-pair status              # Show current status
bpsai-pair plan show <id>      # Show plan details
bpsai-pair flow list           # List available flows
bpsai-pair flow run <name>     # Run a flow
```
