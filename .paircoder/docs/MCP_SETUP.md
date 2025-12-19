# MCP Setup Guide

> Configure PairCoder MCP server for Claude Desktop and other MCP-compatible clients

## Prerequisites

- Python 3.10+
- bpsai-pair installed with MCP extra
- Claude Desktop (or other MCP client)

## Installation

```bash
pip install 'bpsai-pair[mcp]'

# Verify installation
bpsai-pair mcp tools
```

## Claude Desktop Configuration

### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paircoder": {
      "command": "bpsai-pair",
      "args": ["mcp", "serve"],
      "env": {
        "PAIRCODER_PROJECT": "/path/to/your/project"
      }
    }
  }
}
```

### Linux

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paircoder": {
      "command": "bpsai-pair",
      "args": ["mcp", "serve"],
      "env": {
        "PAIRCODER_PROJECT": "/path/to/your/project"
      }
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paircoder": {
      "command": "bpsai-pair",
      "args": ["mcp", "serve"],
      "env": {
        "PAIRCODER_PROJECT": "C:\\path\\to\\your\\project"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PAIRCODER_PROJECT` | Path to project root | Current directory |

## Verification

1. Restart Claude Desktop after config change
2. Start a new conversation
3. Ask: "List my pending tasks using paircoder"
4. Claude should call `paircoder_task_list` tool
5. Verify tasks are returned

## Available Tools

Run `bpsai-pair mcp tools` for the complete list:

| Tool | Description |
|------|-------------|
| `paircoder_task_list` | List tasks with filters (status, plan, sprint) |
| `paircoder_task_next` | Get the next recommended task to work on |
| `paircoder_task_start` | Start a task - updates status and triggers hooks |
| `paircoder_task_complete` | Complete a task - updates status and triggers hooks |
| `paircoder_context_read` | Read project context files |
| `paircoder_plan_status` | Get plan status with sprint/task breakdown |
| `paircoder_plan_list` | List available plans |
| `paircoder_orchestrate_analyze` | Analyze task complexity and get recommendation |
| `paircoder_orchestrate_handoff` | Create handoff package for agent transition |
| `paircoder_metrics_record` | Record token usage and cost metrics |
| `paircoder_metrics_summary` | Get metrics summary |
| `paircoder_trello_sync_plan` | Sync plan tasks to Trello board |
| `paircoder_trello_update_card` | Update Trello card on task state change |

## Testing Tools Locally

Test any tool without Claude Desktop:

```bash
# Test task listing
bpsai-pair mcp test paircoder_task_list

# Test with parameters
bpsai-pair mcp test paircoder_task_list --status pending --plan plan-2025-12-feature

# Test plan status
bpsai-pair mcp test paircoder_plan_status

# Test context read
bpsai-pair mcp test paircoder_context_read --file state
```

## Troubleshooting

### Server won't start

```bash
# Verify bpsai-pair is installed
which bpsai-pair

# Check MCP extra is installed
pip show mcp

# Test server locally
bpsai-pair mcp serve
# Press Ctrl+C to stop
```

### Tools not appearing in Claude

1. Restart Claude Desktop completely (quit and reopen)
2. Check config JSON is valid (no syntax errors)
3. Verify path in config is absolute
4. Check Claude Desktop logs for errors

### Tools return errors

```bash
# Check PAIRCODER_PROJECT points to valid project
ls $PAIRCODER_PROJECT/.paircoder/

# Ensure .paircoder/ directory exists
bpsai-pair validate

# Run tool test to debug
bpsai-pair mcp test paircoder_task_list
```

### Permission denied

On macOS/Linux, ensure bpsai-pair is executable:
```bash
chmod +x $(which bpsai-pair)
```

### Python not found

Use full path to Python:
```json
{
  "mcpServers": {
    "paircoder": {
      "command": "/usr/bin/python3",
      "args": ["-m", "bpsai_pair.cli", "mcp", "serve"],
      "env": {
        "PAIRCODER_PROJECT": "/path/to/project"
      }
    }
  }
}
```

## Example Conversations

Once configured, you can have conversations like:

**User**: What tasks are pending?

**Claude**: *Calls paircoder_task_list with status=pending*

Here are the pending tasks:
- TASK-054: Audit state and sync documentation
- TASK-055: Version bump to 2.4.0
...

**User**: Start working on TASK-054

**Claude**: *Calls paircoder_task_start with task_id=TASK-054*

Started TASK-054. The hooks have been triggered:
- Timer started
- State updated
- Trello card moved to "In Progress"

**User**: I've finished the task

**Claude**: *Calls paircoder_task_complete with task_id=TASK-054*

Completed TASK-054. The hooks have recorded:
- Time: 2h 15m
- Metrics updated
- State refreshed

## Related Documentation

- [User Guide](USER_GUIDE.md) - Full PairCoder documentation
- [README](../README.md) - Project overview
- [Feature Matrix](FEATURE_MATRIX.md) - Complete feature inventory
