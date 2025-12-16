# Agents Guide

Welcome, AI agent! This project uses **PairCoder v2** for AI pair programming.

## Before Doing Anything

1. **Read** `.paircoder/capabilities.yaml` - understand what you can do
2. **Read** `.paircoder/context/state.md` - understand current status
3. **Check** if a flow applies to the user's request

## Key Files

| File | Purpose |
|------|---------|
| `.paircoder/capabilities.yaml` | Your capabilities and when to use them |
| `.paircoder/context/project.md` | Project overview and constraints |
| `.paircoder/context/state.md` | Current plan, tasks, and status |
| `.paircoder/context/workflow.md` | How we work here |
| `.paircoder/config.yaml` | Project configuration |

## Your Roles

| Role | When |
|------|------|
| **Navigator** | Planning, design decisions, clarifying questions |
| **Driver** | Writing code, implementing tasks, running tests |
| **Reviewer** | Code review, quality checks, verification |

## Flow Triggers

| User Says | Suggested Flow |
|-----------|----------------|
| "build a...", "create a...", "add a..." | `design-plan-implement` |
| "fix", "bug", "broken", "error" | `tdd-implement` |
| "review", "check", "look at" | `review` |
| "done", "finished", "ready to merge" | `finish-branch` |

## After Completing Work

Always update `.paircoder/context/state.md`:
- Mark tasks as done
- Note what was accomplished
- Update "What's Next"

## CLI Reference

```bash
# Status
bpsai-pair status

# Plans
bpsai-pair plan list
bpsai-pair plan show <id>

# Tasks
bpsai-pair task list --plan <id>
bpsai-pair task update <id> --status done

# Flows
bpsai-pair flow list
bpsai-pair flow run <name>

# Context
bpsai-pair context-sync --last "..." --next "..."
```
