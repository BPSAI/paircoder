---
id: plan-2025-12-sprint-16-real-subagents
title: "Sprint 16: Real Sub-agents"
status: in_progress
created: 2025-12-17
sprints:
  - id: sprint-16
    name: "Real Sub-agents"
    status: in_progress
    goal: "bpsai-pair orchestrate task actually routes to appropriate agent and invokes it"
    tasks:
      - TASK-096
      - TASK-097
      - TASK-098
      - TASK-099
      - TASK-100
      - TASK-101
---

# Sprint 16: Real Sub-agents

## Goal

`bpsai-pair orchestrate task` actually routes to appropriate agent and invokes it.

## Current State

**What Exists:**
- 6 agent definitions in `.claude/agents/` (planner, reviewer, security, security-auditor)
- `HeadlessSession` class for invoking Claude Code (`orchestration/headless.py`)
- `Orchestrator` with routing logic and scoring algorithm (`orchestration/orchestrator.py`)
- `HandoffPackage` for context transfer between agents (`orchestration/handoff.py`)
- MCP tools for orchestration analysis and handoff

**What's Missing:**
- Unified `AgentInvoker` that loads agent prompts and invokes them
- Actual invocation wiring in `orchestrate task` command
- Agent-specific implementations that use the `.claude/agents/*.md` definitions
- Runtime agent selection based on task characteristics

## Tasks

| ID | Title | Complexity | Priority | Status |
|----|-------|------------|----------|--------|
| TASK-096 | Agent invocation framework | 45 | P0 | pending |
| TASK-097 | Planner agent implementation | 35 | P1 | pending |
| TASK-098 | Reviewer agent implementation | 35 | P1 | pending |
| TASK-099 | Security agent implementation | 40 | P0 | pending |
| TASK-100 | Agent handoff protocol | 40 | P1 | pending |
| TASK-101 | Agent selection logic | 30 | P0 | pending |

**Total Complexity:** 225 points

## Implementation Order

1. **TASK-096** (Agent Invocation Framework) - Foundation
2. **TASK-101** (Agent Selection Logic) - Routing
3. **TASK-097** (Planner Agent) - First agent
4. **TASK-098** (Reviewer Agent) - Second agent
5. **TASK-099** (Security Agent) - Critical agent
6. **TASK-100** (Agent Handoff Protocol) - Multi-agent coordination

## Success Criteria

- [ ] `bpsai-pair orchestrate task TASK-001` invokes correct agent
- [ ] Agent output captured and logged
- [ ] Handoff passes full context between agents
- [ ] Security agent can block unsafe operations
- [ ] All 6 existing agent definitions are usable

## Key Files

| File | Purpose |
|------|---------|
| `.claude/agents/*.md` | Agent definitions (already exist) |
| `orchestration/invoker.py` | New agent invocation framework |
| `orchestration/orchestrator.py` | Existing routing logic (extend) |
| `orchestration/handoff.py` | Existing handoff package (extend) |
| `orchestration/headless.py` | HeadlessSession (use as-is) |
