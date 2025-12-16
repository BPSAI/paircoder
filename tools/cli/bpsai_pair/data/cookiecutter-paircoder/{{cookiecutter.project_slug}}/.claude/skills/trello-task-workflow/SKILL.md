---
name: trello-task-workflow
description: Work on tasks from Trello board. Use when user wants to start, complete, or check status of Trello tasks. Triggers on phrases like "work on task", "start TRELLO-", "finish task", "next task", "I'm blocked".
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Trello Task Workflow

Work on tasks managed in Trello, keeping the board in sync with your progress.

## When This Skill Activates

This skill is invoked when:
- User asks to work on a Trello task (e.g., "work on TRELLO-123")
- User asks for the next task to work on
- User reports being blocked
- User wants to complete/finish a task
- Keywords: trello, TRELLO-*, start task, finish task, blocked, next task

## Prerequisites

Before using this skill:
1. Connect to Trello: `bpsai-pair trello connect`
2. Set active board: `bpsai-pair trello use-board <board-id>`
3. Verify connection: `bpsai-pair trello status`

## Finding Your Next Task

### List Available Tasks
```bash
# Show tasks in Sprint and In Progress
bpsai-pair ttask list

# Show only AI-ready tasks (if your board uses "Agent Task" field)
bpsai-pair ttask list --agent

# Filter by status
bpsai-pair ttask list --status sprint
bpsai-pair ttask list --status in_progress
```

### View Task Details
```bash
bpsai-pair ttask show TRELLO-123
```

## Starting Work

### 1. Claim the Task
```bash
bpsai-pair ttask start TRELLO-123 --summary "Starting implementation"
```

This will:
- Move the card to "In Progress"
- Add a comment with timestamp and agent identifier
- Return the card URL for reference

### 2. Read the Requirements
After claiming:
1. Review the card description
2. Check any checklists
3. Note acceptance criteria
4. Identify dependencies

### 3. Begin Implementation
Use appropriate workflow:
- For new features: `design-plan-implement` skill
- For bug fixes: `tdd-implement` skill
- For refactoring: `tdd-implement` skill

## During Work

### Progress Updates
```bash
# Add progress comment
bpsai-pair ttask comment TRELLO-123 "Completed authentication module"
```

### Encountering Blockers
```bash
# Mark as blocked with reason
bpsai-pair ttask block TRELLO-123 --reason "Waiting for API credentials"
```

This will:
- Move card to "Blocked" list
- Add comment explaining the blocker
- Make the impediment visible to team

## Completing Work

### When Task is Done
```bash
# Complete the task (moves to "In Review")
bpsai-pair ttask done TRELLO-123 --summary "Implemented feature with tests"

# Or move directly to Done
bpsai-pair ttask done TRELLO-123 --summary "Complete" --list "Done"
```

### Completion Checklist

Before marking done:
- [ ] All acceptance criteria met
- [ ] Tests pass: `pytest`
- [ ] No lint errors: `ruff check .`
- [ ] Code committed with proper message
- [ ] Card checklists completed

## Card ID Formats

The following formats are accepted:
- `TRELLO-123` (recommended)
- `123` (short ID)
- Full Trello card ID

## Comment Format

All automated comments include an agent identifier:
```
[claude] started: Beginning work
[claude] progress: Completed authentication module
[claude] completed: Implemented feature with tests
[claude] blocked: Waiting for API credentials
```

## Quick Reference

### Common Commands
```bash
# Status
bpsai-pair trello status          # Check connection
bpsai-pair ttask list             # List active tasks

# Work on task
bpsai-pair ttask show TRELLO-123  # View details
bpsai-pair ttask start TRELLO-123 # Start work
bpsai-pair ttask comment TRELLO-123 "message"  # Progress update
bpsai-pair ttask done TRELLO-123 -s "Summary"  # Complete

# Issues
bpsai-pair ttask block TRELLO-123 -r "Reason"  # Report blocker
bpsai-pair ttask move TRELLO-123 -l "Sprint"   # Move to list
```

### Typical Flow
```
1. bpsai-pair ttask list --status sprint    # Find work
2. bpsai-pair ttask show TRELLO-123         # Review task
3. bpsai-pair ttask start TRELLO-123        # Claim task
4. [implement the feature/fix]              # Do the work
5. bpsai-pair ttask comment TRELLO-123 "Progress..."  # Update
6. bpsai-pair ttask done TRELLO-123 -s "Complete"     # Finish
```

## Configuration

Customize list names in `.paircoder/config.yaml`:

```yaml
trello:
  lists:
    sprint: "Sprint"
    in_progress: "In Progress"
    review: "In Review"
    done: "Done"
    blocked: "Blocked"
  agent_identity: "claude"
```

View/update with:
```bash
bpsai-pair trello config --show
bpsai-pair trello config --set-list "in_progress=Working"
bpsai-pair trello config --agent codex
```
