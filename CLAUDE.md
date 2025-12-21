# Claude Code Instructions

> **PairCoder v2** — AI-augmented pair programming framework

---

## ⚠️ NON-NEGOTIABLE REQUIREMENTS

These requirements MUST be followed. Failure to follow them is a serious workflow violation.

### 1. Update state.md After EVERY Task Completion

**IMMEDIATELY after completing any task**, you MUST update `.paircoder/context/state.md`:
- Mark the task as done in the task list
- Add a session entry under "What Was Just Done" describing what was accomplished
- Update "What's Next" if applicable

**DO NOT:**
- Proceed to other work before updating state.md
- Batch multiple task completions before updating
- Claim a task is complete without documenting it in state.md

### 2. Follow Trello Two-Step Completion

When completing tasks with Trello cards:
1. `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` (checks AC)
2. `bpsai-pair task update TASK-XXX --status done` (updates local file)

**DO NOT** skip `ttask done` - this checks acceptance criteria on Trello.

---

## Before Doing Anything

1. **Read** `.paircoder/capabilities.yaml` — understand what you can do
2. **Read** `.paircoder/context/state.md` — understand current status
3. **Check** if a flow applies to the user's request
4. **If starting a task**: Run `bpsai-pair task update TASK-XXX --status in_progress`

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

**⚠️ This is a NON-NEGOTIABLE requirement. See top of this document.**

1. **Trello** (if card exists): `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
2. **Local file**: `bpsai-pair task update <id> --status done`
3. **IMMEDIATELY update** `.paircoder/context/state.md`:
   - Mark task as done in task list (✓)
   - Add session entry under "What Was Just Done"
   - Update "What's Next"

**You are NOT done until state.md is updated.**

## Project-Specific Notes

This IS PairCoder — the tool we're building. We use PairCoder to develop PairCoder.

Current focus: **v2.1 Released**
- Planning system complete (plan, task commands)
- Skills and flows implemented
- Multi-agent architecture (skills, agents, hooks)
- Ready for ongoing development

## Slash Commands

Quick commands available via `/command` in Claude Code:

| Command | Purpose |
|---------|---------|
| `/status` | Show project status, current sprint, active tasks |
| `/pc-plan` | Show current plan details and progress |
| `/task [ID]` | Show current or specific task details |

**Usage**: Type `/status` in the chat to run the status command.

### Creating Custom Commands

Place markdown files in `.claude/commands/` to create custom slash commands:

```markdown
# .claude/commands/my-command.md
Run these steps:
1. First step
2. Second step
```

Then use `/my-command` in Claude Code.

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
