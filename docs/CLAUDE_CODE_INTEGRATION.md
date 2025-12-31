# Claude Code Integration Guide

> How PairCoder integrates with Claude Code's built-in features

---

## Overview

PairCoder is designed to complement Claude Code, not replace its built-in functionality. This guide documents how to use both effectively together.

---

## Built-in Claude Code Commands

Claude Code provides several built-in slash commands. Here's how they relate to PairCoder:

### Commands PairCoder Leverages

| Command | Purpose | PairCoder Integration |
|---------|---------|----------------------|
| `/compact` | Compress conversation context | Use before large tasks; PairCoder's compaction detection (`bpsai-pair compaction check`) monitors this |
| `/context` | Show token usage | Helps budget context for PairCoder's token-aware planning |
| `/plan` | Create session plan | Use for session-level planning; PairCoder handles sprint/task-level planning |
| `/memory` | Manage persistent memory | Complements `.paircoder/context/` files |
| `/help` | Show help | Works alongside PairCoder's CLI help (`bpsai-pair --help`) |

### Commands to Be Aware Of

| Command | Notes |
|---------|-------|
| `/clear` | Clears conversation - PairCoder state persists in files |
| `/cost` | Shows API costs - complements `bpsai-pair metrics summary` |
| `/doctor` | Diagnoses issues - use alongside `bpsai-pair validate` |
| `/init` | Creates CLAUDE.md - PairCoder has its own `bpsai-pair init` |

### Commands PairCoder Doesn't Conflict With

These Claude Code commands work independently:

- `/bug` - Report bugs to Anthropic
- `/vim` - Toggle vim mode
- `/theme` - Change theme
- `/terminal-setup` - Configure terminal
- `/permissions` - Manage tool permissions
- `/mcp` - Manage MCP servers
- `/config` - Claude Code configuration

---

## PairCoder Slash Commands

PairCoder provides its own slash commands via `.claude/commands/`:

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `/pc-plan` | Show current plan | Reads state.md and plan files |
| `/start-task` | Start working on task | Updates status, triggers hooks |
| `/update-skills` | Analyze and update skills | Detects skill gaps, suggests improvements |

**Note**: For project status, use `bpsai-pair status` CLI command. The `/status` slash command conflicts with Claude Code's built-in command.

### Creating Custom Commands

Add markdown files to `.claude/commands/`:

```markdown
# .claude/commands/my-command.md
Description of what this command does.

Steps:
1. First step
2. Second step
```

Then use `/my-command` in Claude Code.

---

## Context Management

### Claude Code Context vs PairCoder Context

| Aspect | Claude Code | PairCoder |
|--------|-------------|-----------|
| Scope | Conversation | Project |
| Persistence | Session | Git-tracked |
| Reset | `/clear` | Manual file edit |
| Token limit | Model-dependent | Estimated via `bpsai-pair plan estimate` |

### Best Practices

1. **Use `/compact` before large tasks**
   - Frees up context for complex work
   - PairCoder tracks compaction events

2. **Check `/context` when planning**
   - Monitor token budget
   - Use `bpsai-pair plan estimate` for batch planning

3. **Leverage `/memory` for preferences**
   - User-specific preferences
   - PairCoder handles project-specific context

---

## Session Management

### Starting a Session

Recommended workflow:

```bash
# 1. Check project status
bpsai-pair status

# 2. Review current state
# Claude Code will read .paircoder/context/state.md automatically

# 3. Start a task
bpsai-pair task update T19.1 --status in_progress
```

### Handling Compaction

When Claude Code compacts context:

1. PairCoder detects via file watching or hook
2. Critical context is preserved in `.paircoder/context/`
3. Use `bpsai-pair compaction reload` to restore context

```bash
# Check if compaction occurred
bpsai-pair compaction check

# Reload context after compaction
bpsai-pair compaction reload
```

### Ending a Session

1. Update state.md with progress
2. Mark tasks appropriately
3. Commit changes

```bash
# Update task status
bpsai-pair task update T19.1 --status done

# state.md is automatically updated via hooks
```

---

## Planning Integration

### When to Use Claude Code's `/plan`

Use `/plan` for:
- Session-level planning (what to do in this conversation)
- Breaking down immediate work
- Quick brainstorming

### When to Use PairCoder Planning

Use `bpsai-pair plan` for:
- Sprint-level planning (what to do this week)
- Multi-task coordination
- Progress tracking across sessions
- Trello synchronization

### Example Combined Workflow

```bash
# Sprint planning with PairCoder
bpsai-pair plan new sprint-19 --type feature --title "Sprint 19"
bpsai-pair plan add-task sprint-19 --id T19.1 --title "Feature A"

# Session planning with Claude Code
# In Claude Code: /plan Today I'll work on T19.1
```

---

## Skills and Tools

### Claude Code Tools vs PairCoder Tools

| Claude Code | PairCoder |
|-------------|-----------|
| `Read`, `Write`, `Edit` | File operations |
| `Bash` | Shell commands |
| `Task` (subagents) | `bpsai-pair orchestrate` |
| `WebSearch`, `WebFetch` | Research |

### PairCoder Extends Claude Code

PairCoder's MCP server provides additional tools:

```
paircoder_task_list      - List tasks with filters
paircoder_task_start     - Start a task
paircoder_task_complete  - Complete a task
paircoder_context_read   - Read context files
paircoder_plan_status    - Get plan progress
```

### Skill Registration

PairCoder skills are registered in `.claude/skills/`:

```
.claude/skills/
├── design-plan-implement/SKILL.md
├── tdd-implement/SKILL.md
├── code-review/SKILL.md
└── paircoder-task-lifecycle/SKILL.md
```

Claude Code automatically loads these as available skills.

---

## Command Quick Reference

### Claude Code Built-in

| Command | When to Use |
|---------|-------------|
| `/compact` | Before large tasks, when context is full |
| `/context` | Check token usage |
| `/plan` | Session planning |
| `/clear` | Start fresh (preserves PairCoder state) |
| `/help` | Get Claude Code help |

### PairCoder Commands

| Command | When to Use |
|---------|-------------|
| `/pc-plan` | Review current plan |
| `/start-task` | Begin work on task |
| `/update-skills` | Analyze and update skills |

### PairCoder CLI

| Command | When to Use |
|---------|-------------|
| `bpsai-pair status` | Full project status |
| `bpsai-pair task list` | See all tasks |
| `bpsai-pair task next` | Get recommended task |
| `bpsai-pair compaction check` | Check for compaction |

---

## Best Practices

### 1. Let Each Tool Do What It Does Best

- **Claude Code**: Conversation, immediate planning, tool execution
- **PairCoder**: Project state, task tracking, sprint management

### 2. Keep State in Sync

```bash
# After completing work, always:
bpsai-pair task update TASK-XXX --status done

# This triggers hooks to update state.md, Trello, timers
```

### 3. Use Hooks for Automation

PairCoder hooks fire on task status changes:
- `start_timer` / `stop_timer` - Time tracking
- `sync_trello` - Card updates
- `update_state` - state.md refresh

### 4. Check Context Before Complex Tasks

```bash
# In Claude Code: /context
# If context is >80% full, consider /compact

# Then check PairCoder estimates
bpsai-pair plan estimate current-plan
```

### 5. Document Session Progress

At session end:
1. Update state.md "What Was Just Done" section
2. Mark completed tasks as done
3. Note any blockers or decisions

---

## Troubleshooting

### "Task not found" after compaction

Context was cleared. Reload with:
```bash
bpsai-pair status
# Claude Code will re-read state.md
```

### Hooks not firing

Check hooks are enabled:
```bash
bpsai-pair config show hooks
```

### State.md out of sync

Manually trigger state refresh:
```bash
bpsai-pair context-sync
```

### MCP tools not available

Verify MCP server is configured:
```bash
bpsai-pair mcp tools
```

---

## Further Reading

- [User Guide](../.paircoder/docs/USER_GUIDE.md) - Full PairCoder documentation
- [MCP Setup](../.paircoder/docs/MCP_SETUP.md) - MCP server configuration
- [Skills Reference](.claude/skills/) - Available skills
- [Claude Code Documentation](https://docs.anthropic.com/claude-code) - Official docs

---

*PairCoder + Claude Code = Enhanced AI Pair Programming*
