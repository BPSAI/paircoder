---
id: TASK-023
plan: plan-2025-01-paircoder-v2-upgrade
title: Create custom subagents (planner, reviewer)
type: feature
priority: P1
complexity: 40
status: done
sprint: sprint-5
tags: [claude-code, subagents, roles]
---

# Objective

Create custom Claude Code subagents that map to PairCoder's Navigator and
Reviewer roles. These provide specialized, focused agents for planning and
review tasks.

# Background

Claude Code subagents:
- Run in separate context windows
- Can have restricted tool access
- Can be configured with permissionMode (plan = read-only)
- Are invoked explicitly or via Claude's automatic delegation

# Subagents to Create

## 1. Planner Agent (Navigator Role)
- **Purpose**: Design and planning without code changes
- **Tools**: Read, Grep, Glob, Bash (read-only commands)
- **permissionMode**: plan
- **Skills**: design-plan-implement

## 2. Reviewer Agent (Reviewer Role)
- **Purpose**: Code review without making changes
- **Tools**: Read, Grep, Glob, Bash (read-only commands)
- **permissionMode**: plan
- **Skills**: code-review

# Implementation Plan

1. Create agent files in `.claude/agents/`:
   - `planner.md` - Planning and design specialist
   - `reviewer.md` - Code review specialist

2. Agent file format:
```markdown
---
name: agent-name
description: When to use this agent
tools: Tool1, Tool2
model: sonnet
permissionMode: plan
skills: skill1, skill2
---

# Agent instructions
...
```

3. Test agent invocation:
   - Explicit: "Use the planner agent to design this feature"
   - Automatic: Claude delegates based on task type

# Acceptance Criteria

- [ ] planner.md agent created
- [ ] reviewer.md agent created
- [ ] Both agents use permissionMode: plan (read-only)
- [ ] Agents reference appropriate skills
- [ ] Agents tested with explicit invocation
- [ ] Added to cookiecutter template

# Verification

```bash
# Test planner agent
# Say "Use the planner agent to design the authentication system"
# Should invoke planner in read-only mode

# Test reviewer agent
# Say "Use the reviewer agent to check my changes"
# Should invoke reviewer in read-only mode
```

# Files to Create

- `.claude/agents/planner.md`
- `.claude/agents/reviewer.md`

# Dependencies

- TASK-022 (skills must exist for agent reference)

# Notes

We're NOT replacing Claude Code's built-in Plan/Explore agents.
These are complementary specialized agents for PairCoder workflows.
