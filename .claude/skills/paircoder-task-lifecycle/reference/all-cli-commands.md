# PairCoder CLI Complete Reference

## Overview

PairCoder CLI (`bpsai-pair`) manages tasks, plans, Trello integration, and development workflow.

## Command Groups

| Group | Purpose |
|-------|---------|
| `task` | Manage individual tasks |
| `plan` | Manage plans and sprints |
| `trello` | Trello board integration |
| `feature` | Create feature branches |
| `pack` | Create context packs for agents |
| `context-sync` | Sync development context |
| `standup` | Generate standup summaries |
| `init` | Initialize project structure |

---

## Task Commands

### bpsai-pair task list

List all tasks with status, priority, and complexity.

```bash
bpsai-pair task list
bpsai-pair task list --plan PLAN-ID    # Filter by plan
bpsai-pair task list --status pending  # Filter by status
```

### bpsai-pair task show TASK-ID

Show detailed information about a specific task.

```bash
bpsai-pair task show TASK-082
```

### bpsai-pair task update TASK-ID --status STATUS

**CRITICAL:** This is the primary command for task lifecycle management.

```bash
# Start working on a task
bpsai-pair task update TASK-082 --status in_progress

# Mark task as blocked
bpsai-pair task update TASK-082 --status blocked

# Complete a task
bpsai-pair task update TASK-082 --status done
```

**Side Effects:**
- Updates task file YAML frontmatter
- Fires hooks (Trello card move, timer, etc.)
- Updates state.md if configured

### bpsai-pair task next

Show the next recommended task to work on (by priority and dependencies).

```bash
bpsai-pair task next
bpsai-pair task next --plan PLAN-ID
```

### bpsai-pair task auto-next

Automatically assign and start the next pending task.

```bash
bpsai-pair task auto-next
```

### bpsai-pair task archive TASK-ID

Archive a completed task.

```bash
bpsai-pair task archive TASK-082
```

### bpsai-pair task restore TASK-ID

Restore an archived task.

```bash
bpsai-pair task restore TASK-082
```

### bpsai-pair task list-archived

List all archived tasks.

```bash
bpsai-pair task list-archived
```

### bpsai-pair task changelog-preview

Preview changelog entry for completed tasks.

```bash
bpsai-pair task changelog-preview
bpsai-pair task changelog-preview --since 2025-12-01
```

---

## Plan Commands

### bpsai-pair plan list

List all plans with task counts.

```bash
bpsai-pair plan list
```

### bpsai-pair plan show PLAN-ID

Show detailed plan information including sprints and tasks.

```bash
bpsai-pair plan show plan-2025-12-sprint-14-trello-deep
```

### bpsai-pair plan sync-trello PLAN-ID

Sync plan tasks to Trello board.

```bash
bpsai-pair plan sync-trello plan-2025-12-sprint-14-trello-deep
```

**What it does:**
- Creates cards for tasks that don't exist
- Updates cards for tasks that changed
- Moves cards to correct lists based on status
- Applies labels and custom fields (when configured)

### bpsai-pair plan create

Create a new plan interactively.

```bash
bpsai-pair plan create
bpsai-pair plan create --title "My Feature" --type feature
```

---

## Trello Commands

### bpsai-pair trello status

Check Trello connection and board status.

```bash
bpsai-pair trello status
```

**Shows:**
- Connection status
- Board name and ID
- List counts
- Card counts per list

### bpsai-pair trello refresh

Force refresh of Trello data.

```bash
bpsai-pair trello refresh
```

### bpsai-pair trello configure

Configure Trello integration.

```bash
bpsai-pair trello configure
bpsai-pair trello configure --board-id BOARD_ID
```

---

## Other Commands

### bpsai-pair status

Show overall project status.

```bash
bpsai-pair status
```

**Shows:**
- Current branch
- Working tree status
- Current phase
- Overall goal
- Last/next actions
- Blockers

### bpsai-pair feature NAME

Create a feature branch with context.

```bash
bpsai-pair feature my-feature --type feature --primary "Main goal"
```

### bpsai-pair pack

Create a context pack for agent sessions.

```bash
bpsai-pair pack
bpsai-pair pack --out my_pack.tgz
```

### bpsai-pair standup

Generate a standup summary.

```bash
bpsai-pair standup
bpsai-pair standup --since yesterday
```

### bpsai-pair init

Initialize PairCoder in a project.

```bash
bpsai-pair init
bpsai-pair init --preset bps  # Use BPS preset
```

---

## Configuration

### Config File Location

`.paircoder/config.yaml`

### Key Settings

```yaml
trello:
  enabled: true
  board_id: "your-board-id"
  api_key: "${TRELLO_API_KEY}"
  token: "${TRELLO_TOKEN}"
  
  list_mapping:
    pending: "Backlog"
    in_progress: "In Progress"
    review: "Review"
    done: "Deployed / Done"
    blocked: "Issues / Blocked"

hooks:
  on_task_update:
    - trello_sync
    - update_state

github:
  enabled: true
  auto_pr: true
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `TRELLO_API_KEY` | Trello API key |
| `TRELLO_TOKEN` | Trello OAuth token |
| `GITHUB_TOKEN` | GitHub personal access token |
| `PAIRCODER_CONFIG` | Override config file path |

---

## Common Workflows

### Start of Day

```bash
bpsai-pair status           # Check current state
bpsai-pair task list        # See pending tasks
bpsai-pair task next        # Find what to work on
bpsai-pair task update TASK-XXX --status in_progress
```

### End of Task

```bash
pytest -v                   # Run tests
git add -A
git commit -m "feat: TASK-XXX - description"
bpsai-pair task update TASK-XXX --status done
bpsai-pair task next        # See what's next
```

### End of Day

```bash
bpsai-pair standup          # Generate summary
git push                    # Push changes
```

### Sprint Planning

```bash
bpsai-pair plan create
bpsai-pair plan sync-trello PLAN-ID
bpsai-pair trello status    # Verify cards created
```
