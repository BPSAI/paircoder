---
name: trello-task-workflow
description: |
  Work on tasks from Trello board. Automatically claims tasks, 
  updates status, and logs activity back to Trello. Use when
  starting work, completing tasks, or checking what to work on next.
triggers:
  - work on task
  - start task
  - what should I work on
  - next task
  - pick up task
  - claim task
  - finish task
  - complete task
  - mark done
  - I'm blocked
model_invoked: true
roles:
  driver:
    primary: true
    description: Execute task implementation
  navigator:
    primary: false
    description: Help understand task requirements
---

# Trello Task Workflow

This skill integrates with your project's Trello board for task management, enabling seamless coordination between AI agents and human developers.

## Prerequisites

Check if Trello integration is enabled:

```bash
# Check connection status
bpsai-pair trello status

# If not connected
bpsai-pair trello connect
```

Check your project's task backend:

```bash
# View current config
cat .paircoder/config.yaml | grep -A 10 "tasks:"
```

If `tasks.backend` is not `trello`, this skill operates in read-only mode (can view but not update Trello).

## Finding Your Next Task

### Option 1: Get Next Available Task

```bash
# Show tasks marked for AI processing, sorted by priority
bpsai-pair task list --agent --status sprint
```

This shows cards with:
- "Agent Task" checkbox checked
- In the "Sprint" list
- Sorted by Priority (Highest first)
- Excluding blocked tasks (unchecked dependencies)

### Option 2: View All Active Tasks

```bash
# Show everything in progress
bpsai-pair task list --status in_progress

# Show sprint backlog
bpsai-pair task list --list "Sprint"
```

### Option 3: Show Specific Task

```bash
bpsai-pair task show TRELLO-123
```

## Starting Work

When you begin a task:

```bash
bpsai-pair task start TRELLO-123
```

**What happens:**
1. Card moves from "Sprint" → "In Progress"
2. Comment added: "🧠 [claude] started: Beginning work"
3. Local state updated for `bpsai-pair status`

**Important:** Only start one task at a time. Complete or block before starting another.

## During Implementation

### Reference Task in Commits

Always include the task ID in commit messages:

```bash
git commit -m "feat(auth): add JWT validation (TRELLO-123)"
```

### Update Progress (Optional)

For long-running tasks, add progress updates:

```bash
bpsai-pair task comment TRELLO-123 "Completed API endpoints, starting frontend integration"
```

### Check Task Requirements

If you need to review the task details:

```bash
bpsai-pair task show TRELLO-123
```

Look for:
- **Description**: Full requirements
- **Checklists**: Acceptance criteria, implementation steps
- **Labels**: Category, priority, type

## Completing Work

When implementation is done:

```bash
bpsai-pair task done TRELLO-123 --summary "Implemented JWT auth with refresh tokens, added unit tests"
```

**What happens:**
1. Card moves to "In Review" (or "Done" if no review needed)
2. Comment added with completion summary
3. Activity logged for dashboard visibility

### Include Meaningful Summary

Good summaries help reviewers:
- ✅ "Added user authentication with JWT, bcrypt password hashing, and 15 unit tests"
- ❌ "Done"

## Handling Blockers

If you can't proceed:

```bash
bpsai-pair task block TRELLO-123 --reason "Waiting for API credentials from DevOps"
```

**What happens:**
1. Card moves to "Blocked" list
2. Comment added with block reason
3. Task becomes visible in "blocked" status queries

### Common Block Reasons

- Missing credentials or API keys
- Dependency on another task
- Unclear requirements (needs clarification)
- External service unavailable
- Waiting for code review

## Workflow Summary

```
┌─────────┐    start     ┌─────────────┐    done    ┌───────────┐
│ Sprint  │ ──────────►  │ In Progress │ ────────►  │ In Review │
└─────────┘              └─────────────┘            └───────────┘
                               │
                               │ block
                               ▼
                         ┌─────────┐
                         │ Blocked │
                         └─────────┘
```

## Best Practices

### 1. One Task at a Time
Focus on completing one task before picking up another. This keeps the board accurate.

### 2. Check Dependencies First
Before starting, verify no blockers:

```bash
bpsai-pair task show TRELLO-123 | grep -A 5 "dependencies"
```

### 3. Update Status Promptly
Move cards as soon as status changes. Stale boards confuse the team.

### 4. Meaningful Comments
Add comments for significant milestones, not every small change.

### 5. Link to PRs
When creating a PR, include the Trello link:

```markdown
## Related
- Trello: https://trello.com/c/abc123
```

## Troubleshooting

### "Not connected to Trello"

```bash
bpsai-pair trello connect
# Follow prompts for API key and token
```

### "Board not configured"

```bash
bpsai-pair trello boards                    # List available boards
bpsai-pair trello use-board <board-id>      # Set board for project
```

### "Task not found"

The task ID format is `TRELLO-<short_id>`. Find the short ID:
- From URL: `trello.com/c/abc123` → `TRELLO-abc123`
- From card: Look at the card number in Trello

### "Permission denied"

Your Trello token may lack permissions. Regenerate with `read,write,account` scopes:
1. Go to https://trello.com/app-key
2. Generate new token
3. Run `bpsai-pair trello connect` with new credentials

## Integration with Other Skills

This skill works alongside:

- **design-plan-implement**: Creates tasks during planning phase
- **tdd-implement**: Use for bug fix tasks
- **code-review**: Use when reviewing PR linked to task
- **finish-branch**: Automatically marks task done when branch merges
