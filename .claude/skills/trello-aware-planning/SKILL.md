---
name: trello-aware-planning
description: |
  Create and organize tasks in Trello during planning sessions.
  Use when designing features, breaking down work, or organizing
  sprints. Creates cards with proper structure for AI processing.
triggers:
  - plan feature
  - break down work
  - create tasks
  - organize sprint
  - design approach
  - what tasks do we need
  - let's plan
model_invoked: true
roles:
  navigator:
    primary: true
    description: Strategic planning and task organization
  driver:
    primary: false
    description: Execute task creation commands
---

# Trello-Aware Planning

This skill helps you plan features and create well-structured Trello tasks that both humans and AI agents can work on effectively.

## When to Use This Skill

- Starting a new feature
- Breaking down a large task into smaller pieces
- Organizing work for a sprint
- Creating tasks from a design discussion
- Converting requirements into actionable work items

## Prerequisites

Ensure Trello is connected and a board is configured:

```bash
bpsai-pair trello status
bpsai-pair config show | grep -A 5 trello
```

## Planning Workflow

### Step 1: Understand the Goal

Before creating tasks, clarify:
1. What is the end-user outcome?
2. What are the acceptance criteria?
3. What are the dependencies?
4. What's the priority?

### Step 2: Break Down the Work

Good task breakdown follows these principles:

| Principle | Good Example | Bad Example |
|-----------|--------------|-------------|
| **Small** | "Add email validation to signup form" | "Build authentication system" |
| **Specific** | "Create POST /api/users endpoint" | "Work on API" |
| **Testable** | "Unit tests for JWT refresh logic" | "Add tests" |
| **Independent** | Can be completed without waiting | Blocked by 5 other tasks |

### Step 3: Create Tasks

#### Basic Task Creation

```bash
bpsai-pair task create \
  --title "Add email validation to signup form" \
  --description "Validate email format on client and server side. Show inline errors." \
  --priority P1 \
  --list Sprint
```

#### AI-Ready Task (Marked for Agent Processing)

```bash
bpsai-pair task create \
  --title "Implement JWT refresh token endpoint" \
  --description "Create POST /api/auth/refresh endpoint that validates refresh token and issues new access token" \
  --priority P0 \
  --list Sprint \
  --agent-task \
  --labels "backend,auth"
```

The `--agent-task` flag checks the "Agent Task" custom field, making it visible to both Codex and Claude agents.

#### Task with Full Structure

```bash
bpsai-pair task create \
  --title "Add rate limiting to API" \
  --description "Implement rate limiting using Redis. 100 requests per minute per user." \
  --priority P1 \
  --list Sprint \
  --agent-task \
  --labels "backend,security" \
  --checklist "Acceptance Criteria" \
    "Rate limit of 100 req/min enforced" \
    "429 response when exceeded" \
    "X-RateLimit headers included" \
    "Unit tests for rate limiter" \
    "Integration test with Redis"
```

### Step 4: Set Dependencies

If tasks must be completed in order:

```bash
# Task B depends on Task A
bpsai-pair task add-dependency TRELLO-456 --depends-on TRELLO-123
```

This adds an item to the "card dependencies" checklist. The dependent task is blocked until the dependency is checked off.

### Step 5: Organize Sprint

Move tasks to appropriate lists:

```bash
# Ready for this sprint
bpsai-pair task move TRELLO-123 --list "Sprint"

# Not ready yet (backlog)
bpsai-pair task move TRELLO-456 --list "Backlog"

# Needs more definition
bpsai-pair task move TRELLO-789 --list "Icebox"
```

## Task Templates

### Feature Task

```bash
bpsai-pair task create \
  --title "[Feature] User profile page" \
  --description "Create user profile page showing avatar, bio, and recent activity" \
  --priority P1 \
  --list Sprint \
  --agent-task \
  --labels "frontend,feature" \
  --checklist "Acceptance Criteria" \
    "Shows user avatar and name" \
    "Displays editable bio field" \
    "Lists 10 most recent activities" \
    "Responsive on mobile" \
    "Loading skeleton while fetching"
```

### Bug Fix Task

```bash
bpsai-pair task create \
  --title "[Bug] Login fails with special characters in password" \
  --description "Users with passwords containing & or # cannot log in. Error: 'Invalid credentials'" \
  --priority P0 \
  --list Sprint \
  --agent-task \
  --labels "bug,auth,urgent" \
  --checklist "Verification" \
    "Can login with password containing &" \
    "Can login with password containing #" \
    "Can login with password containing %" \
    "Regression test added"
```

### Refactor Task

```bash
bpsai-pair task create \
  --title "[Refactor] Extract API client to shared module" \
  --description "Move API client code from components to shared/api-client.ts for reuse" \
  --priority P2 \
  --list Backlog \
  --labels "refactor,tech-debt" \
  --checklist "Scope" \
    "Create shared/api-client.ts" \
    "Migrate UserService calls" \
    "Migrate AuthService calls" \
    "Update imports in components" \
    "No behavior changes (refactor only)"
```

### Research/Spike Task

```bash
bpsai-pair task create \
  --title "[Spike] Evaluate WebSocket vs SSE for real-time updates" \
  --description "Research and prototype both approaches. Document pros/cons for our use case." \
  --priority P1 \
  --list Sprint \
  --labels "research,architecture" \
  --checklist "Deliverables" \
    "Prototype with WebSocket" \
    "Prototype with SSE" \
    "Performance comparison" \
    "Complexity comparison" \
    "Recommendation document"
```

## Planning Session Flow

### 1. Review Current State

```bash
# What's in progress?
bpsai-pair task list --status in_progress

# What's blocked?
bpsai-pair task list --status blocked

# What's in the sprint?
bpsai-pair task list --list "Sprint"
```

### 2. Discuss New Work

Use the Navigator role to:
- Clarify requirements
- Identify risks
- Estimate complexity
- Determine dependencies

### 3. Create Tasks

For each work item identified:
1. Write clear title (action verb + object)
2. Add description with context
3. Set appropriate priority
4. Add acceptance criteria checklist
5. Mark as agent-task if suitable for AI
6. Add labels for categorization

### 4. Organize Board

```bash
# Prioritize sprint
bpsai-pair task list --list "Sprint" --sort priority

# Check for orphaned tasks
bpsai-pair task list --list "Backlog" --no-labels
```

### 5. Verify Dependencies

```bash
# Show tasks with dependencies
bpsai-pair task list --has-dependencies

# Check for circular dependencies
bpsai-pair task validate-dependencies
```

## Best Practices

### Task Sizing

| Size | Time Estimate | Example |
|------|---------------|---------|
| XS | < 1 hour | "Fix typo in error message" |
| S | 1-2 hours | "Add input validation" |
| M | 2-4 hours | "Create new API endpoint" |
| L | 4-8 hours | "Implement feature module" |
| XL | > 8 hours | **Break down further!** |

### Priority Guidelines

| Priority | Meaning | Example |
|----------|---------|---------|
| P0 | Critical/Blocking | Security fix, broken core feature |
| P1 | High/Important | Sprint commitment, key feature |
| P2 | Normal | Nice to have, improvements |
| P3 | Low | Tech debt, future enhancement |

### Agent-Suitable Tasks

Mark tasks as agent-ready (`--agent-task`) when:
- ✅ Clear, specific requirements
- ✅ Bounded scope (not open-ended)
- ✅ Can be verified with tests
- ✅ No external dependencies (API keys, etc.)
- ✅ Standard patterns (CRUD, validation, etc.)

Do NOT mark as agent-ready when:
- ❌ Requires human judgment (UX decisions)
- ❌ Needs external access (production DB)
- ❌ Ambiguous requirements
- ❌ Cross-team coordination needed

### Labels Convention

Use consistent labels across the board:

```
Type:     feature, bug, refactor, docs, test, spike
Area:     frontend, backend, api, database, infra
Priority: urgent, high, medium, low
Status:   needs-review, needs-design, ready
```

## Integration with Other Skills

After planning:

1. **trello-task-workflow**: Pick up and execute tasks
2. **design-plan-implement**: Deep dive on complex features
3. **tdd-implement**: Execute bug fix tasks
4. **code-review**: Review completed work

## Example Planning Session

**User:** "Let's plan the user authentication feature"

**Claude (Navigator role):**

1. First, let me understand the scope:
   - What auth methods? (email/password, OAuth, magic link?)
   - What's the user model?
   - Any existing code to integrate with?

2. Breaking down into tasks:

```bash
# Core auth
bpsai-pair task create --title "Create User model and migration" \
  --priority P0 --agent-task --labels "backend,auth"

bpsai-pair task create --title "Implement password hashing with bcrypt" \
  --priority P0 --agent-task --labels "backend,auth,security"

bpsai-pair task create --title "Create POST /api/auth/register endpoint" \
  --priority P0 --agent-task --labels "backend,auth,api"

bpsai-pair task create --title "Create POST /api/auth/login endpoint" \
  --priority P0 --agent-task --labels "backend,auth,api"

# JWT handling
bpsai-pair task create --title "Implement JWT token generation" \
  --priority P0 --agent-task --labels "backend,auth"

bpsai-pair task create --title "Create auth middleware for protected routes" \
  --priority P0 --agent-task --labels "backend,auth"

# Frontend
bpsai-pair task create --title "Create login form component" \
  --priority P1 --labels "frontend,auth"

bpsai-pair task create --title "Create registration form component" \
  --priority P1 --labels "frontend,auth"

# Set dependencies
bpsai-pair task add-dependency TRELLO-103 --depends-on TRELLO-101  # Login depends on User model
bpsai-pair task add-dependency TRELLO-104 --depends-on TRELLO-103  # JWT depends on Login
```

3. Sprint organization:

```bash
# Move P0 tasks to Sprint
bpsai-pair task move TRELLO-101 --list "Sprint"
bpsai-pair task move TRELLO-102 --list "Sprint"
# ... etc
```

4. Verify the plan:

```bash
bpsai-pair task list --list "Sprint" --sort priority
```

Ready to start implementation!
