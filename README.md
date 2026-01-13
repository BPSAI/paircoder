# PairCoder v2.9.0 — AI-Augmented Pair Programming Framework

PairCoder is a **repo-native toolkit** for pairing with AI coding agents (Claude, GPT, Codex, Gemini). It standardizes project memory in `.paircoder/`, provides structured workflows via skills, and ships a CLI with **127+ commands** to orchestrate the entire development lifecycle.

> **v2.9.0** — Enforcement Gates + Task State Machine + Audit Logging

## Key Features

| Feature | Description                                             |
|---------|---------------------------------------------------------|
| **Planning System** | Plans, sprints, tasks with YAML+MD format               |
| **Skills** | Claude Code native skills (.claude/skills/) with cross-platform export |
| **Orchestration** | Multi-agent coordination, model routing by complexity   |
| **Autonomous Workflow** | Auto-session for hands-off task execution               |
| **Presets** | 8 built-in presets (python-cli, bps, autonomous, etc.)  |
| **GitHub Integration** | Auto-PR creation, task-linked PRs, archive on merge     |
| **Trello Integration** | Board/card management, progress comments, webhooks      |
| **Standup Generation** | Daily summaries in markdown/slack/trello formats        |
| **Metrics** | Token tracking, cost estimation, budget enforcement     |
| **Time Tracking** | Built-in timer with Toggl integration                   |
| **MCP Server** | 13 tools for autonomous agent operation                 |
| **Auto-Hooks** | Automatic Trello sync and state updates on task changes |

## Quick Start

### Install

```bash
pip install bpsai-pair
bpsai-pair --version  # Should show 2.9.0
```

### Initialize a Project

```bash
# New project with preset
bpsai-pair init my-project --preset python-cli
cd my-project

# List available presets
bpsai-pair preset list

# Initialize with BPS Trello workflow
bpsai-pair init my-project --preset bps

# Existing project
cd your-project
bpsai-pair init .
```

### For MCP/Claude Desktop Integration

```bash
pip install 'bpsai-pair[mcp]'
bpsai-pair mcp tools  # List available tools
```

## Project Structure

```
my-project/
├── .paircoder/                    # PairCoder data
│   ├── config.yaml               # Project configuration
│   ├── capabilities.yaml         # LLM capability manifest
│   ├── context/                  # Project context files
│   │   ├── project.md           # Project overview
│   │   ├── workflow.md          # Workflow guidelines
│   │   └── state.md             # Current state
│   ├── plans/                    # Plan files (.plan.yaml)
│   ├── tasks/                    # Task files (.task.md)
│   └── history/                  # Archives, metrics
├── .claude/                       # Claude Code native
│   ├── skills/                   # Model-invoked skills
│   │   ├── design-plan-implement/
│   │   ├── tdd-implement/
│   │   ├── code-review/
│   │   ├── finish-branch/
│   │   ├── managing-task-lifecycle/
│   │   └── planning-with-trello/
│   └── agents/                   # Custom subagents
│       ├── planner.md
│       └── reviewer.md
├── AGENTS.md                      # Universal AI entry point
├── CLAUDE.md                      # Claude Code pointer
└── docs/                          # Documentation
```

## CLI Command Reference (127+ commands)

### Core Commands

| Command | Description |
|---------|-------------|
| `init [path] [--preset]` | Initialize repo with PairCoder structure |
| `feature <name>` | Create feature branch with context |
| `pack [--lite]` | Package context for AI agents |
| `context-sync` | Update the context loop |
| `status` | Show current context and recent changes |
| `validate` | Check repo structure and consistency |
| `ci` | Run local CI checks |

### Presets (4 commands)

| Command | Description |
|---------|-------------|
| `preset list` | List available presets |
| `preset show <name>` | Show preset details |
| `preset preview <name>` | Preview generated config |
| `init --preset <name>` | Initialize with preset |

**Available Presets:** python-cli, python-api, react, fullstack, library, minimal, autonomous, bps

### Planning (8 commands)

| Command | Description |
|---------|-------------|
| `plan new <slug>` | Create a new plan |
| `plan list` | List all plans |
| `plan show <id>` | Show plan details |
| `plan tasks <id>` | List tasks for a plan |
| `plan status [id]` | Show progress with task breakdown |
| `plan sync-trello <id>` | Sync tasks to Trello board |
| `plan add-task <id>` | Add a task to a plan |
| `plan estimate <id>` | Estimate plan token cost |

### Tasks (11 commands)

| Command | Description |
|---------|-------------|
| `task list` | List all tasks |
| `task show <id>` | Show task details |
| `task update <id> --status` | Update task status (fires hooks) |
| `task next` | Get next recommended task |
| `task next --start` | Auto-start next task |
| `task auto-next` | Full auto-assignment with Trello |
| `task archive` | Archive completed tasks |
| `task restore <id>` | Restore from archive |
| `task list-archived` | List archived tasks |
| `task cleanup` | Clean old archives |
| `task changelog-preview` | Preview changelog entry |

### Skills (7 commands)

| Command | Description |
|---------|-------------|
| `skill list` | List all skills |
| `skill validate` | Validate skill format against spec |
| `skill export` | Export to Cursor/Continue/Windsurf |
| `skill install` | Install skill from URL/path |
| `skill suggest` | AI-powered skill suggestions |
| `skill gaps` | Detect missing skills from patterns |
| `skill generate` | Generate skill from detected gap |


### Orchestration (6 commands)

| Command | Description |
|---------|-------------|
| `orchestrate task <id>` | Route task to best agent |
| `orchestrate analyze <id>` | Show routing decision |
| `orchestrate handoff <id>` | Create handoff package |
| `orchestrate auto-run --task <id>` | Run single task workflow |
| `orchestrate auto-session` | Run autonomous session |
| `orchestrate workflow-status` | Show current workflow state |

### Intent Detection (3 commands)

| Command | Description |
|---------|-------------|
| `intent detect <text>` | Detect work intent from text |
| `intent should-plan <text>` | Check if planning needed |
| `intent suggest-flow <text>` | Suggest appropriate flow |

### GitHub Integration (7 commands)

| Command | Description |
|---------|-------------|
| `github status` | Check GitHub connection |
| `github create --task <id>` | Create PR for task |
| `github list` | List pull requests |
| `github merge <pr>` | Merge PR and update task |
| `github link <task>` | Link task to PR |
| `github auto-pr` | Auto-create PR from branch |
| `github archive-merged` | Archive tasks for merged PRs |

### Standup (2 commands)

| Command | Description |
|---------|-------------|
| `standup generate` | Generate daily summary |
| `standup post` | Post summary to Trello |

### Metrics (9 commands)

| Command | Description |
|---------|-------------|
| `metrics summary` | Show metrics for time period |
| `metrics task <id>` | Show metrics for a task |
| `metrics breakdown` | Cost breakdown by dimension |
| `metrics budget` | Show budget status |
| `metrics export` | Export metrics to file |
| `metrics velocity` | Show velocity metrics |
| `metrics burndown` | Show burndown chart data |
| `metrics accuracy` | Show estimation accuracy |
| `metrics tokens` | Show token usage |

### Budget (3 commands)

| Command | Description |
|---------|-------------|
| `budget estimate` | Estimate task token cost |
| `budget status` | Show current budget usage |
| `budget check` | Check if task fits budget |

### Timer (5 commands)

| Command | Description |
|---------|-------------|
| `timer start <task>` | Start timer for a task |
| `timer stop` | Stop current timer |
| `timer status` | Show current timer |
| `timer show <task>` | Show time entries |
| `timer summary` | Show time summary |

### Benchmarks (4 commands)

| Command | Description |
|---------|-------------|
| `benchmark run` | Run benchmark suite |
| `benchmark results` | View results |
| `benchmark compare` | Compare agents |
| `benchmark list` | List benchmarks |

### Cache (3 commands)

| Command | Description |
|---------|-------------|
| `cache stats` | Show cache statistics |
| `cache clear` | Clear context cache |
| `cache invalidate` | Invalidate specific file |

### Session (2 commands)

| Command | Description |
|---------|-------------|
| `session check` | Check session status |
| `session status` | Show detailed session info |

### Compaction (5 commands)

| Command | Description |
|---------|-------------|
| `compaction snapshot save` | Save context snapshot |
| `compaction snapshot list` | List snapshots |
| `compaction check` | Check for compaction |
| `compaction recover` | Recover from compaction |
| `compaction cleanup` | Clean old snapshots |

### Security (4 commands)

| Command | Description |
|---------|-------------|
| `security scan-secrets` | Scan for leaked secrets |
| `security pre-commit` | Run pre-commit checks |
| `security install-hook` | Install git hooks |
| `security scan-deps` | Scan dependency vulnerabilities |

### Migrate (2 commands)

| Command | Description |
|---------|-------------|
| `migrate` | Run pending migrations |
| `migrate status` | Show migration status |

### Upgrade (1 command)

| Command | Description |
|---------|-------------|
| `upgrade` | Upgrade PairCoder version |

### Trello Setup

To connect your project to a Trello board:

```bash
# 1. Get API credentials from https://trello.com/power-ups/admin
#    - Click "New" to create a Power-Up
#    - Copy the API Key
#    - Click "Generate Token" and authorize

# 2. Set environment variables
export TRELLO_API_KEY=your_api_key
export TRELLO_TOKEN=your_token

# 3. Connect and set board
bpsai-pair trello connect
bpsai-pair trello boards              # List available boards
bpsai-pair trello use-board <board-id>  # Set active board

# 4. Verify connection
bpsai-pair trello status
```

The board ID can be found in your Trello board URL: `https://trello.com/b/<BOARD_ID>/board-name`

### Trello (10 commands)

| Command | Description |
|---------|-------------|
| `trello connect` | Connect to Trello |
| `trello status` | Check connection |
| `trello disconnect` | Remove credentials |
| `trello boards` | List available boards |
| `trello use-board <id>` | Set active board |
| `trello lists` | Show board lists |
| `trello config` | View/modify config |
| `trello progress <task>` | Post progress comment |
| `trello webhook serve` | Start webhook server |
| `trello webhook status` | Check webhook status |

### Trello Tasks (7 commands)

| Command | Description |
|---------|-------------|
| `ttask list` | List tasks from board |
| `ttask show <id>` | Show task details |
| `ttask start <id>` | Start working on task |
| `ttask done <id>` | Complete task |
| `ttask block <id>` | Mark as blocked |
| `ttask comment <id>` | Add comment |
| `ttask move <id>` | Move to different list |

### MCP Server (3 commands)

| Command | Description |
|---------|-------------|
| `mcp serve` | Start MCP server (stdio) |
| `mcp tools` | List available tools |
| `mcp test <tool>` | Test tool locally |

### Audit (3 commands)

| Command | Description |
|---------|-------------|
| `audit bypasses` | Show recent workflow bypasses |
| `audit summary` | Show bypass summary by type |
| `audit clear` | Clear bypass log (dev only) |

### State (5 commands)

| Command | Description |
|---------|-------------|
| `state show <task>` | Show task state and transitions |
| `state list` | List all tracked states |
| `state history [task]` | View state transition history |
| `state reset <task>` | Reset task to NOT_STARTED |
| `state advance <task> <state>` | Manually advance task state |

## MCP Integration

PairCoder provides an MCP (Model Context Protocol) server with **13 tools** for autonomous agent operation:

| Tool | Description |
|------|-------------|
| `paircoder_task_list` | List tasks with filters |
| `paircoder_task_next` | Get next recommended task |
| `paircoder_task_start` | Start a task |
| `paircoder_task_complete` | Complete a task |
| `paircoder_context_read` | Read project context |
| `paircoder_plan_status` | Get plan progress |
| `paircoder_plan_list` | List available plans |
| `paircoder_orchestrate_analyze` | Analyze task complexity |
| `paircoder_orchestrate_handoff` | Create handoff package |
| `paircoder_metrics_record` | Record token usage |
| `paircoder_metrics_summary` | Get metrics summary |
| `paircoder_trello_sync_plan` | Sync plan to Trello |
| `paircoder_trello_update_card` | Update Trello card |

See [MCP Setup Guide](docs/MCP_SETUP.md) for Claude Desktop configuration.

## Auto-Hooks

Configure automatic actions on task state changes in `.paircoder/config.yaml`:

```yaml
hooks:
  enabled: true
  on_task_start:
    - check_token_budget
    - start_timer
    - sync_trello
    - update_state
  on_task_complete:
    - stop_timer
    - record_metrics
    - sync_trello
    - update_state
    - check_unblocked
```

## Windows & Cross-Platform

PairCoder is fully Python-backed (no Bash required):

```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Install and use
pip install bpsai-pair
bpsai-pair --help
```

## Development

```bash
cd tools/cli
pip install -e .
pytest -v  # 2050+ tests
```

## Documentation

- [User Guide](.paircoder/docs/USER_GUIDE.md) — Full documentation
- [MCP Setup](docs/MCP_SETUP.md) — Claude Desktop integration
- [Feature Matrix](.paircoder/docs/FEATURE_MATRIX.md) — Complete feature inventory
- [Cross-Platform Skills](docs/CROSS_PLATFORM_SKILLS.md) — Skill export to other tools
- [Migration Guide](docs/MIGRATION.md) — Flows to skills migration
- [Changelog](CHANGELOG.md) — Version history

## License

MIT
