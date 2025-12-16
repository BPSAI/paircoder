---
name: trello-aware-planning
description: Create and organize tasks in Trello during planning. Use when user wants to plan features, break down work, or organize a sprint. Triggers on phrases like "plan feature", "break down", "create tasks", "organize sprint".
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Trello-Aware Planning

Plan features and create tasks directly in Trello, integrated with PairCoder's planning system.

## When This Skill Activates

This skill is invoked when:
- User asks to plan a new feature
- User wants to break down work into tasks
- User asks to organize or update the sprint
- User wants to create Trello cards for planned work
- Keywords: plan, feature, breakdown, tasks, sprint, organize, cards

## Prerequisites

Ensure Trello is configured:
```bash
bpsai-pair trello status
# Should show: Connected, Board configured
```

## Planning Workflow

### Phase 1: Design

Before creating cards, understand the work:

1. **Clarify Requirements**
   - What is the user trying to accomplish?
   - What are the acceptance criteria?
   - What are the non-goals?

2. **Identify Components**
   - What parts of the codebase are affected?
   - What new files/modules are needed?
   - What existing code needs modification?

3. **Consider Approaches**
   - What are the implementation options?
   - What are the tradeoffs?
   - Which approach is recommended?

### Phase 2: Task Breakdown

Break the work into discrete tasks:

#### Task Sizing Guidelines

| Size | Duration | Description |
|------|----------|-------------|
| Small | 15-30 min | Single function, simple change |
| Medium | 30-60 min | Module, multiple related changes |
| Large | 1-2 hours | Feature component, significant work |

**Avoid tasks larger than 2 hours** - break them down further.

#### Task Template

For each task, capture:
- **Title**: Clear, action-oriented (e.g., "Add user validation to signup form")
- **Description**: What needs to be done
- **Acceptance Criteria**: How to verify completion
- **Priority**: P0 (must), P1 (should), P2 (could)
- **Dependencies**: What must be done first

### Phase 3: Create in Trello

#### Option A: Manual Creation
Guide the user to create cards in Trello directly, providing:
1. Suggested card titles
2. Description content
3. Checklist items for acceptance criteria

#### Option B: File-Based Sync
Create task files that can be synced:

```bash
# Create plan file
bpsai-pair plan new feature-name --type feature --title "Feature Title"

# Add tasks to plan
bpsai-pair plan add-task feature-name --id TASK-001 --title "Task title"
```

Then user manually creates corresponding Trello cards.

### Phase 4: Sprint Organization

#### Prioritizing the Sprint

Help organize which tasks go into the sprint:

1. **Must Have (P0)**: Required for feature to work
2. **Should Have (P1)**: Important but can ship without
3. **Nice to Have (P2)**: Future enhancement

#### Sprint Capacity

Consider sprint capacity:
```
Sprint Days × Hours/Day × Team Size = Available Hours
Available Hours × 0.7 = Realistic Capacity (70% efficiency)
```

Recommend task selection based on:
- Priority ordering
- Dependency ordering
- Realistic capacity

### Phase 5: Review Board State

After planning, verify:

```bash
# List all board lists
bpsai-pair trello lists

# Show sprint tasks
bpsai-pair ttask list --status sprint

# Check for blocked items
bpsai-pair ttask list --status blocked
```

## Planning Templates

### Feature Planning Prompt

When user asks to plan a feature, gather:

1. **What**: Describe the feature in 2-3 sentences
2. **Why**: What problem does it solve?
3. **Who**: Who benefits from this feature?
4. **How**: High-level approach
5. **When**: Priority/timeline expectations

### Task Creation Prompt

For each task, confirm:

```markdown
**Title**: [Action verb] [component] [outcome]
**Description**:
[What needs to be done]
[Where in codebase]
[Any special considerations]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Priority**: P0/P1/P2
**Depends On**: None / TASK-XXX
```

## Best Practices

### DO
- Keep tasks small and focused
- Include clear acceptance criteria
- Set realistic priorities
- Consider dependencies
- Use consistent naming

### DON'T
- Create vague tasks ("fix stuff")
- Skip acceptance criteria
- Overload the sprint
- Ignore dependencies
- Create duplicate tasks

## Quick Reference

### Planning Commands
```bash
# Check board state
bpsai-pair trello lists
bpsai-pair ttask list --status backlog

# PairCoder planning (file-based)
bpsai-pair plan new feature-x --type feature --title "Feature X"
bpsai-pair plan add-task feature-x --id TASK-001 --title "Task 1"
bpsai-pair task list --plan feature-x
```

### Sprint Management
```bash
# Move tasks between lists
bpsai-pair ttask move TRELLO-123 --list "Sprint"
bpsai-pair ttask move TRELLO-124 --list "Backlog"

# Review sprint
bpsai-pair ttask list --status sprint
```

## Integration with PairCoder Flows

This skill works alongside other skills:

1. **trello-aware-planning** (this skill)
   - Create the plan and tasks

2. **trello-task-workflow**
   - Work on individual tasks

3. **tdd-implement**
   - Implement each task with TDD

4. **code-review**
   - Review completed work

5. **finish-branch**
   - Complete and merge
