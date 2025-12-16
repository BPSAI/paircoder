---
id: TASK-024
plan: plan-2025-01-paircoder-v2-upgrade
title: Implement hooks for auto context-sync
type: feature
priority: P1
complexity: 45
status: done
sprint: sprint-5
tags: [claude-code, hooks, automation]
---

# Objective

Implement Claude Code hooks that automatically sync context and log activity
during PairCoder workflows. Hooks provide deterministic control over behavior.

# Background

Claude Code hooks:
- Execute shell commands at specific lifecycle points
- Run automatically (not relying on LLM choice)
- Can block operations (PreToolUse) or respond to them (PostToolUse)
- Configured in `.claude/settings.json`

# Hook Events Available

| Event | When | Use For |
|-------|------|---------|
| PreToolUse | Before tool calls | Block dangerous operations |
| PostToolUse | After tool calls | Log changes, format code |
| Stop | Conversation ends | Sync state, cleanup |
| SessionStart | New session begins | Load context |
| Notification | Notification sent | Custom alerts |

# Hooks to Implement

## 1. PostToolUse: File Change Logger
Log edited files to task context for traceability.

```json
{
  "PostToolUse": [{
    "matcher": "Edit|Write",
    "hooks": [{
      "type": "command",
      "command": "jq -r '.tool_input.file_path' >> /tmp/paircoder-changes.log"
    }]
  }]
}
```

## 2. Stop: Context Sync
Sync state when conversation ends.

```json
{
  "Stop": [{
    "hooks": [{
      "type": "command",
      "command": "bpsai-pair sync --auto 2>/dev/null || true"
    }]
  }]
}
```

## 3. SessionStart: State Check (Optional)
Remind about current state on session start.

```json
{
  "SessionStart": [{
    "hooks": [{
      "type": "command",
      "command": "cat .paircoder/context/state.md 2>/dev/null | head -20 || true"
    }]
  }]
}
```

# Implementation Plan

1. Create hooks configuration in `.claude/settings.json`
2. Create helper scripts if needed for complex logic
3. Test each hook independently
4. Document hook behavior in CLAUDE.md

# settings.json Structure

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date -Iseconds) $CLAUDE_TOOL_INPUT_FILE_PATH\" >> .paircoder/history/changes.log"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bpsai-pair sync --auto 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

# Acceptance Criteria

- [ ] PostToolUse hook logs file changes
- [ ] Stop hook syncs context (graceful if bpsai-pair not installed)
- [ ] Hooks documented in CLAUDE.md
- [ ] settings.json added to cookiecutter template
- [ ] Hooks tested and working

# Verification

```bash
# Test PostToolUse
# Make a file edit, check log file exists

# Test Stop
# End conversation, verify state synced
```

# Files to Create/Modify

- `.claude/settings.json` - Hook configuration
- `.paircoder/scripts/hook-helpers.sh` (optional) - Helper scripts

# Security Considerations

- Hooks run with user credentials
- Don't store sensitive data in logs
- Use 2>/dev/null || true for optional hooks
- Review all hook commands before committing

# Notes

Hooks provide deterministic behavior vs relying on LLM choices.
Start simple; add more hooks as patterns emerge.
