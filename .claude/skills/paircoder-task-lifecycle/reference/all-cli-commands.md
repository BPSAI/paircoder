# PairCoder CLI Complete Reference

## Overview

PairCoder CLI (`bpsai-pair`) manages tasks, plans, Trello integration, and development workflow.

## Command Groups

| Group | Purpose |
|-------|---------|
| `task` | Manage local task files |
| `ttask` | Manage Trello cards directly |
| `plan` | Manage plans and sprints |
| `trello` | Trello board configuration |
| `feature` | Create feature branches |
| `pack` | Create context packs for agents |
| `context-sync` | Sync development context |
| `standup` | Generate standup summaries |
| `init` | Initialize project structure |

---

## Task Commands (Local)

These commands operate on local `.task.md` files and trigger hooks (Trello sync, timers, state updates).

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
bpsai-pair task next --start          # Pick and start immediately
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

### bpsai-pair task cleanup

Clean up old archived tasks.

```bash
bpsai-pair task cleanup
bpsai-pair task cleanup --older-than 30  # Days
```

### bpsai-pair task changelog-preview

Preview changelog entry for completed tasks.

```bash
bpsai-pair task changelog-preview
bpsai-pair task changelog-preview --since 2025-12-01
```

---

## Trello Task Commands (ttask)

These commands operate directly on Trello cards. Use when working with Trello as the source of truth.

### bpsai-pair ttask list

List Trello cards with filters.

```bash
bpsai-pair ttask list
bpsai-pair ttask list --list "In Progress"
bpsai-pair ttask list --agent              # Cards marked for AI processing
bpsai-pair ttask list --status sprint      # Cards in Sprint list
```

### bpsai-pair ttask show CARD-ID

Show Trello card details including custom fields.

```bash
bpsai-pair ttask show TRELLO-abc123
bpsai-pair ttask show TASK-082            # If linked to local task
```

### bpsai-pair ttask start CARD-ID

Start work on a Trello card.

```bash
bpsai-pair ttask start TRELLO-abc123
```

**What happens:**
- Card moves from "Sprint" → "In Progress"
- Comment added: "🚀 Started by {agent}"
- Local state updated

### bpsai-pair ttask done CARD-ID

Mark a Trello card as done.

```bash
bpsai-pair ttask done TRELLO-abc123
bpsai-pair ttask done TRELLO-abc123 --summary "Implemented feature X with tests"
```

**What happens:**
- Card moves to "In Review" or "Done"
- Comment added with completion summary

### bpsai-pair ttask block CARD-ID

Mark a Trello card as blocked.

```bash
bpsai-pair ttask block TRELLO-abc123 --reason "Waiting for API credentials"
```

**What happens:**
- Card moves to "Blocked" list
- Comment added with block reason

### bpsai-pair ttask comment CARD-ID "MESSAGE"

Add a comment to a Trello card.

```bash
bpsai-pair ttask comment TRELLO-abc123 "Halfway done with custom fields"
bpsai-pair ttask comment TASK-082 "Completed API endpoints, starting frontend"
```

### bpsai-pair ttask move CARD-ID LIST-NAME

Move a Trello card to a specific list.

```bash
bpsai-pair ttask move TRELLO-abc123 "Review/Testing"
bpsai-pair ttask move TRELLO-abc123 "Deployed/Done"
```

---

## When to Use `task` vs `ttask`

| Scenario | Command |
|----------|---------|
| Working with local task files | `task` |
| Need hooks to fire (timer, state.md) | `task update` |
| Working directly with Trello cards | `ttask` |
| Adding progress comments to cards | `ttask comment` |
| Card doesn't have local task file | `ttask` |
| Card has linked local task | Either works |

**Recommended workflow:**
- Use `task update` for status changes (fires all hooks)
- Use `ttask comment` for progress notes
- Use `ttask` commands when Trello is your only source

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

### bpsai-pair plan status PLAN-ID

Get plan status with task breakdown.

```bash
bpsai-pair plan status plan-2025-12-sprint-14-trello-deep
```

### bpsai-pair plan new

Create a new plan.

```bash
bpsai-pair plan new my-feature --type feature --title "My Feature"
```

### bpsai-pair plan add-task PLAN-ID

Add a task to an existing plan.

```bash
bpsai-pair plan add-task plan-2025-12-sprint-14-trello-deep
```

### bpsai-pair plan sync-trello PLAN-ID

Sync plan tasks to Trello board.

```bash
bpsai-pair plan sync-trello plan-2025-12-sprint-14-trello-deep
bpsai-pair plan sync-trello plan-2025-12-sprint-14-trello-deep --dry-run
```

**What it does:**
- Creates cards for tasks that don't exist
- Updates cards for tasks that changed
- Sets custom fields (Project, Stack, Effort, Status)
- Applies labels
- Creates checklists from acceptance criteria

---

## Trello Commands

### bpsai-pair trello status

Check Trello connection and board status.

```bash
bpsai-pair trello status
```

### bpsai-pair trello connect

Connect to Trello with API credentials.

```bash
bpsai-pair trello connect
```

### bpsai-pair trello boards

List available Trello boards.

```bash
bpsai-pair trello boards
```

### bpsai-pair trello use-board BOARD-ID

Set the board for this project.

```bash
bpsai-pair trello use-board 694176ebf4b9d27c6e7a0e73
```

### bpsai-pair trello lists

List all lists on the current board.

```bash
bpsai-pair trello lists
```

### bpsai-pair trello config

Show Trello configuration.

```bash
bpsai-pair trello config
```

### bpsai-pair trello progress

Generate progress reports.

```bash
bpsai-pair trello progress
bpsai-pair trello progress --type weekly
```

### bpsai-pair trello webhook serve

Start webhook server to listen for Trello events.

```bash
bpsai-pair trello webhook serve
bpsai-pair trello webhook serve --port 8080
```

### bpsai-pair trello webhook status

Check webhook status.

```bash
bpsai-pair trello webhook status
```

---

## Other Commands

### bpsai-pair status

Show overall project status.

```bash
bpsai-pair status
```

### bpsai-pair feature NAME

Create a feature branch with context.

```bash
bpsai-pair feature my-feature --type feature --primary "Main goal"
```

### bpsai-pair pack

Create a context pack for agent sessions.

```bash
bpsai-pair pack
bpsai-pair pack --lite                    # Minimal pack for Codex
bpsai-pair pack --out my_pack.tgz
```

### bpsai-pair standup

Generate a standup summary.

```bash
bpsai-pair standup
bpsai-pair standup generate               # Generate summary
bpsai-pair standup post                   # Post to Slack/Trello
bpsai-pair standup --since yesterday
```

### bpsai-pair init

Initialize PairCoder in a project.

```bash
bpsai-pair init
bpsai-pair init --preset bps              # Use BPS preset
```

### bpsai-pair validate

Validate project configuration.

```bash
bpsai-pair validate
```

---

## Orchestration Commands

### bpsai-pair orchestrate analyze TASK-ID

Analyze task complexity for model routing.

```bash
bpsai-pair orchestrate analyze TASK-082
```

### bpsai-pair orchestrate handoff

Create handoff package between agents.

```bash
bpsai-pair orchestrate handoff TASK-082 --from planner --to driver
```

### bpsai-pair orchestrate auto-session

Run autonomous work session.

```bash
bpsai-pair orchestrate auto-session
bpsai-pair orchestrate auto-session --max-tasks 3
```

---

## GitHub Commands

### bpsai-pair github status

Check GitHub integration status.

```bash
bpsai-pair github status
```

### bpsai-pair github create

Create a pull request.

```bash
bpsai-pair github create --title "TASK-082: Feature X"
```

### bpsai-pair github auto-pr

Auto-create PR from current branch (detects TASK-xxx).

```bash
bpsai-pair github auto-pr
```

### bpsai-pair github archive-merged

Archive tasks for merged PRs.

```bash
bpsai-pair github archive-merged
```

---

## Metrics Commands

### bpsai-pair metrics summary

Show metrics summary.

```bash
bpsai-pair metrics summary
bpsai-pair metrics summary --scope sprint --scope-id sprint-14
```

### bpsai-pair metrics task TASK-ID

Show metrics for a specific task.

```bash
bpsai-pair metrics task TASK-082
```

### bpsai-pair metrics export

Export metrics to CSV.

```bash
bpsai-pair metrics export --output metrics.csv
```

---

## Timer Commands

### bpsai-pair timer start TASK-ID

Start timer for a task.

```bash
bpsai-pair timer start TASK-082
```

### bpsai-pair timer stop

Stop the current timer.

```bash
bpsai-pair timer stop
bpsai-pair timer stop --summary "Completed implementation"
```

### bpsai-pair timer status

Show current timer status.

```bash
bpsai-pair timer status
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
    pending: "Intake/Backlog"
    in_progress: "In Progress"
    review: "Review/Testing"
    done: "Deployed/Done"
    blocked: "Issues/Tech Debt"

hooks:
  enabled: true
  on_task_start:
    - start_timer
    - sync_trello
    - update_state
  on_task_complete:
    - stop_timer
    - record_metrics
    - sync_trello
    - update_state
    - check_unblocked
  on_task_block:
    - sync_trello
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

### During Work (Progress Updates)

```bash
bpsai-pair ttask comment TASK-XXX "Completed API, starting tests"
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
bpsai-pair plan new sprint-15 --type feature --title "Security & Sandboxing"
# Add tasks to plan...
bpsai-pair plan sync-trello plan-2025-12-sprint-15-security
bpsai-pair trello status    # Verify cards created
```

### Working Directly with Trello

```bash
bpsai-pair ttask list --agent             # Show AI-assigned cards
bpsai-pair ttask start TRELLO-abc123      # Start card
# ... do work ...
bpsai-pair ttask done TRELLO-abc123 --summary "Feature complete"
```
