# PairCoder MCP Server Specification

> Model Context Protocol server exposing PairCoder CLI as tools for Claude

## Overview

The PairCoder MCP server exposes `bpsai-pair` CLI functionality as callable tools, enabling Claude (and other MCP-compatible agents) to:

1. Manage plans and tasks programmatically
2. Track time and metrics automatically
3. Sync with Trello boards
4. Route tasks via orchestration
5. Update project context

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude / Agent                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (stdio/SSE)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    paircoder-mcp-server                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │ Tool Handlers │  │ Resource Hdlr │  │ Prompt Templates  │   │
│  └───────────────┘  └───────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Python API / subprocess
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      bpsai-pair CLI                              │
│  planning │ tasks │ orchestration │ metrics │ trello │ flows   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      .paircoder/                                 │
│  config.yaml │ context/ │ plans/ │ tasks/ │ flows/ │ history/  │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Tools

### Planning Tools

#### `paircoder_plan_create`
Create a new plan with sprints and tasks.

```json
{
  "name": "paircoder_plan_create",
  "description": "Create a new development plan with goals, sprints, and task breakdown",
  "inputSchema": {
    "type": "object",
    "properties": {
      "slug": {
        "type": "string",
        "description": "Short identifier (e.g., 'user-auth', 'api-refactor')"
      },
      "title": {
        "type": "string",
        "description": "Human-readable plan title"
      },
      "type": {
        "type": "string",
        "enum": ["feature", "bugfix", "refactor", "chore"],
        "default": "feature"
      },
      "goals": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of plan goals/acceptance criteria"
      },
      "sprints": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "goal": {"type": "string"},
            "tasks": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "title": {"type": "string"},
                  "type": {"type": "string", "enum": ["feature", "bugfix", "test", "docs", "chore"]},
                  "complexity": {"type": "integer", "minimum": 5, "maximum": 100},
                  "priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                  "estimate_hours": {"type": "number"},
                  "depends_on": {"type": "array", "items": {"type": "string"}}
                }
              }
            }
          }
        }
      }
    },
    "required": ["slug", "title", "goals"]
  }
}
```

#### `paircoder_plan_list`
List all plans in the project.

```json
{
  "name": "paircoder_plan_list",
  "description": "List all development plans",
  "inputSchema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "active", "completed", "archived"],
        "default": "active"
      }
    }
  }
}
```

#### `paircoder_plan_status`
Get detailed status of a plan including sprint progress.

```json
{
  "name": "paircoder_plan_status",
  "description": "Get plan status with sprint and task breakdown",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plan_id": {"type": "string", "description": "Plan ID or 'current' for active plan"}
    },
    "required": ["plan_id"]
  }
}
```

### Task Tools

#### `paircoder_task_list`
List tasks with optional filters.

```json
{
  "name": "paircoder_task_list",
  "description": "List tasks with filtering options",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plan": {"type": "string", "description": "Filter by plan ID"},
      "sprint": {"type": "string", "description": "Filter by sprint"},
      "status": {
        "type": "string",
        "enum": ["all", "pending", "in_progress", "done", "blocked"],
        "default": "all"
      },
      "assignee": {"type": "string", "description": "Filter by assignee/agent"}
    }
  }
}
```

#### `paircoder_task_next`
Get the next recommended task to work on.

```json
{
  "name": "paircoder_task_next",
  "description": "Get next task based on dependencies, priority, and complexity routing",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent": {
        "type": "string",
        "description": "Agent requesting task (for complexity routing)"
      },
      "plan": {"type": "string", "description": "Limit to specific plan"}
    }
  }
}
```

#### `paircoder_task_start`
Start working on a task (updates status, starts timer, notifies).

```json
{
  "name": "paircoder_task_start",
  "description": "Start a task - updates status, starts timer, syncs Trello",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "agent": {"type": "string", "description": "Agent claiming the task"}
    },
    "required": ["task_id"]
  }
}
```

#### `paircoder_task_complete`
Complete a task with summary.

```json
{
  "name": "paircoder_task_complete",
  "description": "Mark task complete - stops timer, records metrics, syncs Trello",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "summary": {"type": "string", "description": "What was accomplished"},
      "files_changed": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of files modified"
      },
      "tests_added": {"type": "integer", "default": 0},
      "notes": {"type": "string", "description": "Additional notes for handoff"}
    },
    "required": ["task_id", "summary"]
  }
}
```

#### `paircoder_task_block`
Mark a task as blocked.

```json
{
  "name": "paircoder_task_block",
  "description": "Mark task as blocked with reason",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "reason": {"type": "string"},
      "blocked_by": {"type": "string", "description": "Task ID or external blocker"}
    },
    "required": ["task_id", "reason"]
  }
}
```

### Orchestration Tools

#### `paircoder_orchestrate_analyze`
Analyze a task and get routing recommendation.

```json
{
  "name": "paircoder_orchestrate_analyze",
  "description": "Analyze task complexity and get model/agent routing recommendation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "context": {"type": "string", "description": "Additional context for analysis"}
    },
    "required": ["task_id"]
  }
}
```

**Returns:**
```json
{
  "task_id": "TASK-045",
  "complexity_score": 65,
  "complexity_band": "complex",
  "recommended_model": "claude-opus-4-5",
  "reasoning": "Architecture task with cross-cutting concerns",
  "tags_detected": ["architecture", "refactor"],
  "estimated_tokens": 15000,
  "estimated_cost": "$0.45"
}
```

#### `paircoder_orchestrate_handoff`
Create a handoff package for another agent.

```json
{
  "name": "paircoder_orchestrate_handoff",
  "description": "Create handoff context package for agent transition",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "from_agent": {"type": "string"},
      "to_agent": {"type": "string"},
      "progress_summary": {"type": "string"},
      "files_in_progress": {"type": "array", "items": {"type": "string"}},
      "decisions_made": {"type": "array", "items": {"type": "string"}},
      "open_questions": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["task_id", "progress_summary"]
  }
}
```

### Trello Tools

#### `paircoder_trello_sync_plan`
Sync a plan to Trello board (create cards for tasks).

```json
{
  "name": "paircoder_trello_sync_plan",
  "description": "Sync plan tasks to Trello board as cards",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plan_id": {"type": "string"},
      "board_id": {"type": "string", "description": "Trello board ID (uses default if not specified)"},
      "create_lists": {
        "type": "boolean",
        "default": true,
        "description": "Create sprint lists if they don't exist"
      },
      "link_cards": {
        "type": "boolean", 
        "default": true,
        "description": "Store Trello card IDs in task files"
      }
    },
    "required": ["plan_id"]
  }
}
```

#### `paircoder_trello_update_card`
Update a Trello card from task state.

```json
{
  "name": "paircoder_trello_update_card",
  "description": "Update Trello card status, add comment, move lists",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "action": {
        "type": "string",
        "enum": ["start", "complete", "block", "comment"]
      },
      "comment": {"type": "string"}
    },
    "required": ["task_id", "action"]
  }
}
```

### Metrics Tools

#### `paircoder_metrics_record`
Record metrics for a completed action.

```json
{
  "name": "paircoder_metrics_record",
  "description": "Record token usage, time, and cost metrics",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string"},
      "agent": {"type": "string"},
      "model": {"type": "string"},
      "input_tokens": {"type": "integer"},
      "output_tokens": {"type": "integer"},
      "duration_seconds": {"type": "number"},
      "action_type": {
        "type": "string",
        "enum": ["planning", "coding", "review", "testing", "documentation"]
      }
    },
    "required": ["task_id", "agent", "model"]
  }
}
```

#### `paircoder_metrics_summary`
Get metrics summary for reporting.

```json
{
  "name": "paircoder_metrics_summary",
  "description": "Get metrics summary by task, plan, sprint, or time period",
  "inputSchema": {
    "type": "object",
    "properties": {
      "scope": {
        "type": "string",
        "enum": ["task", "plan", "sprint", "day", "week", "month"]
      },
      "scope_id": {"type": "string", "description": "ID for task/plan/sprint scope"},
      "include_estimates": {
        "type": "boolean",
        "default": true,
        "description": "Include estimate vs actual comparison"
      }
    }
  }
}
```

### Context Tools

#### `paircoder_context_update`
Update project context files.

```json
{
  "name": "paircoder_context_update",
  "description": "Update .paircoder/context files (state.md, workflow.md, etc.)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file": {
        "type": "string",
        "enum": ["state", "workflow", "project"],
        "description": "Context file to update"
      },
      "section": {"type": "string", "description": "Section to update"},
      "content": {"type": "string", "description": "New content for section"},
      "append": {
        "type": "boolean",
        "default": false,
        "description": "Append to section instead of replace"
      }
    },
    "required": ["file", "section", "content"]
  }
}
```

#### `paircoder_context_read`
Read project context.

```json
{
  "name": "paircoder_context_read",
  "description": "Read .paircoder/context files",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file": {
        "type": "string", 
        "enum": ["state", "workflow", "project", "all"]
      },
      "section": {"type": "string", "description": "Specific section (optional)"}
    }
  }
}
```

## MCP Resources

Resources expose read-only project data:

### `paircoder://context/state`
Current project state (state.md contents).

### `paircoder://context/workflow`  
Workflow documentation.

### `paircoder://plans/current`
Currently active plan with tasks.

### `paircoder://tasks/pending`
List of pending tasks.

### `paircoder://metrics/today`
Today's metrics summary.

### `paircoder://trello/board`
Current Trello board state.

## MCP Prompts

Pre-built prompts for common workflows:

### `paircoder_start_session`
Initialize a work session - loads context, checks for pending tasks, shows status.

### `paircoder_plan_feature`
Guided feature planning - helps break down a feature into sprints and tasks.

### `paircoder_daily_standup`
Generate daily standup summary - what was done, what's next, any blockers.

### `paircoder_sprint_review`
Sprint review template - accomplishments, metrics, retrospective.

## Implementation Notes

### Server Structure

```
tools/cli/bpsai_pair/mcp/
├── __init__.py
├── server.py           # Main MCP server
├── tools/
│   ├── __init__.py
│   ├── planning.py     # Plan/task tools
│   ├── orchestration.py
│   ├── trello.py
│   ├── metrics.py
│   └── context.py
├── resources.py        # Resource handlers
└── prompts.py          # Prompt templates
```

### Configuration

Add to `.paircoder/config.yaml`:

```yaml
mcp:
  enabled: true
  server_name: "paircoder"
  transport: "stdio"  # or "sse" for HTTP
  auto_sync:
    trello: true
    metrics: true
    context: true
  hooks:
    on_task_start:
      - start_timer
      - sync_trello
    on_task_complete:
      - stop_timer
      - record_metrics
      - sync_trello
      - update_state
```

### Claude Desktop Integration

Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "paircoder": {
      "command": "bpsai-pair",
      "args": ["mcp", "serve"],
      "env": {
        "PAIRCODER_PROJECT": "/path/to/project"
      }
    }
  }
}
```

### Auto-Hooks

When `paircoder_task_start` is called, server automatically:
1. Updates task status to `in_progress`
2. Starts timer via time tracking integration
3. Moves Trello card to "In Progress" list
4. Updates `state.md` with current focus

When `paircoder_task_complete` is called:
1. Updates task status to `done`
2. Stops timer, records elapsed time
3. Records token/cost metrics
4. Moves Trello card to "Done" list
5. Updates `state.md`
6. Checks for dependent tasks now unblocked
7. Suggests next task

## CLI Integration

New CLI command:

```bash
# Start MCP server
bpsai-pair mcp serve [--transport stdio|sse] [--port 3000]

# Test MCP tools locally
bpsai-pair mcp test <tool_name> --input '{"task_id": "TASK-045"}'

# List available tools
bpsai-pair mcp tools

# Generate Claude Desktop config
bpsai-pair mcp config --claude-desktop
```

## Error Handling

All tools return structured errors:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task TASK-999 not found in .paircoder/tasks/",
    "suggestion": "Run paircoder_task_list to see available tasks"
  }
}
```

Error codes:
- `TASK_NOT_FOUND` - Task ID doesn't exist
- `PLAN_NOT_FOUND` - Plan ID doesn't exist  
- `INVALID_STATE_TRANSITION` - Can't transition task to requested state
- `TRELLO_NOT_CONFIGURED` - Trello integration not set up
- `DEPENDENCY_BLOCKED` - Task has unmet dependencies
- `BUDGET_EXCEEDED` - Would exceed configured budget limit

## Security Considerations

1. **No credential exposure** - Trello tokens stored in config, not passed through tools
2. **Path validation** - All file operations scoped to `.paircoder/`
3. **Rate limiting** - Trello API calls rate-limited per config
4. **Audit logging** - All tool calls logged to `history/mcp.log`

## Future Extensions

1. **GitHub Integration** - Create PRs, link commits to tasks
2. **Slack Notifications** - Post updates to channels
3. **Multi-project** - Work across multiple .paircoder projects
4. **Agent Memory** - Persistent agent context between sessions
