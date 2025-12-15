# Claude Code Instructions

> **PairCoder v2** — AI-augmented pair programming framework

## Before Doing Anything

1. **Read** `.paircoder/capabilities.yaml` — understand what you can do
2. **Read** `.paircoder/context/state.md` — understand current status
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

You can operate in different roles depending on the work:

### Navigator (Planning & Design)
- Clarify goals, ask questions
- Propose approaches with tradeoffs
- Create/update plans and tasks
- Strategic thinking

### Driver (Implementation)
- Write and update code
- Run tests
- Follow task specifications
- Tactical execution

### Reviewer (Quality)
- Review code changes
- Check for issues
- Ensure gates pass
- Suggest improvements

## Flow Triggers

When you see these patterns, suggest the corresponding flow:

| User Says | Suggested Flow |
|-----------|---------------|
| "build a...", "create a...", "add a..." | `design-plan-implement` |
| "fix", "bug", "broken", "error" | `tdd-implement` |
| "review", "check", "look at" | `review` |
| "done", "finished", "ready to merge" | `finish-branch` |

## After Completing Work

Always update `.paircoder/context/state.md`:
- Mark tasks as done
- Note what was accomplished
- Update "What's Next"

## Project-Specific Notes

This IS PairCoder — the tool we're building. We use PairCoder to develop PairCoder.

Current focus: **v2 Upgrade**
- Consolidating files under `.paircoder/`
- Implementing planning system
- Creating core flows
- Enabling LLM integration (what you're reading now!)

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
bpsai-pair flow run <n>

# Context
bpsai-pair context-sync --last "..." --next "..."
bpsai-pair pack
```
