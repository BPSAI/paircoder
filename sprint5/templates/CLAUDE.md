# CLAUDE.md

This project uses **PairCoder v2** for structured human-AI pair programming.

## Project Context

Read these files to understand the project:

| File | Purpose |
|------|---------|
| `.paircoder/context/project.md` | Project overview, constraints, architecture |
| `.paircoder/context/workflow.md` | Branch conventions, commit format, code style |
| `.paircoder/context/state.md` | **Current state**: active plan, sprint, tasks |

## Before Starting Work

1. **Check state**: Read `.paircoder/context/state.md`
2. **Find your task**: Look in `.paircoder/tasks/{plan-slug}/` for task files
3. **Follow the workflow**: Appropriate skill will auto-activate based on your request

## Available Skills

Claude Code will auto-discover and use these skills in `.claude/skills/`:

| Skill | Triggers On | Purpose |
|-------|-------------|---------|
| `design-plan-implement` | "design", "plan", "approach", "feature" | New feature development |
| `tdd-implement` | "fix", "bug", "test", "implement" | Test-driven development |
| `code-review` | "review", "check", "PR" | Code review workflow |
| `finish-branch` | "finish", "merge", "complete", "ship" | Branch completion |

**Skills are model-invoked**: You don't need to explicitly call them. Describe what you want and the appropriate skill activates.

## Slash Commands

- `/plan` - View or create development plans
- `/task` - View task details or get next task
- `/status` - Show current project state

## Custom Agents

Available subagents in `.claude/agents/`:

- **planner** - For design and planning (read-only, no code changes)
- **reviewer** - For code review (read-only analysis)

## Hooks (Automatic)

These hooks run automatically:
- **PostToolUse**: Logs file changes to task context
- **Stop**: Syncs state when conversation ends

## Working with Tasks

### Task File Structure
```yaml
---
id: TASK-XXX
plan: plan-name
title: Task title
status: pending | in_progress | done | blocked
priority: P0 | P1 | P2
complexity: 10-100
---

# Objective
What needs to be accomplished

# Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

# Implementation Notes
Additional context for implementation
```

### Status Updates
- Set `status: in_progress` when you start working
- Set `status: done` when all criteria are met
- Add notes under `# Implementation Notes` as you work

## Directory Structure Reference

```
.claude/                      # Claude Code native
├── skills/                   # Model-invoked skills
│   ├── design-plan-implement/
│   │   └── SKILL.md
│   ├── tdd-implement/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   └── finish-branch/
│       └── SKILL.md
├── agents/                   # Custom subagents
│   ├── planner.md
│   └── reviewer.md
├── commands/                 # Slash commands
│   ├── plan.md
│   ├── task.md
│   └── status.md
└── settings.json             # Hooks configuration

.paircoder/                   # Cross-agent content
├── context/                  # Project context
├── flows/                    # Workflow definitions
├── plans/                    # Plan files
└── tasks/                    # Task files
```

## Integration with Other Agents

This project also supports other AGENTS.md-compatible agents:
- See `AGENTS.md` in project root for universal instructions
- Flows in `.paircoder/flows/` work with Codex, Cursor, etc.
- Claude Code skills are optimized versions of flows

## Quick Start Checklist

- [ ] Read `.paircoder/context/state.md`
- [ ] Identify current task from state or use `/task next`
- [ ] Set task status to `in_progress`
- [ ] Follow appropriate workflow (skill auto-activates)
- [ ] Update task status to `done` when complete
- [ ] Commit with message format: `[TASK-XXX] Description`
