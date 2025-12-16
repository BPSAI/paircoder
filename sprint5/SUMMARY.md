# PairCoder v2.1 - Sprint 5 Deliverables Summary

**Date**: 2025-12-15  
**Package**: `sprint5-multiagent-architecture.tgz`

---

## What's in the Package

### 1. Architecture Document
`ARCHITECTURE-v2.1.md` - Comprehensive strategic document covering:
- Dual-layer architecture (AGENTS.md + Claude-specific)
- Directory structure for cross-agent compatibility
- Role mapping (PairCoder roles → Claude Code equivalents)
- Planning mode activation patterns
- Task lifecycle management
- Metrics and observability design
- Implementation roadmap (Sprints 5-7)

### 2. Template Files

#### `templates/AGENTS.md`
Universal entry point for all AGENTS.md-compatible agents:
- OpenAI Codex
- Google Jules
- Cursor
- VS Code
- GitHub Copilot
- Windsurf, Devin, and 60k+ more

Includes:
- Project setup commands
- Code conventions
- PairCoder integration instructions
- Workflow quick reference
- Points to `.paircoder/` for deeper features

#### `templates/CLAUDE.md`
Claude Code-specific pointer file:
- References project context files
- Lists available skills
- Lists slash commands
- Describes custom agents
- Quick start checklist

### 3. Claude Code Skills (converted from flows)

| Skill | Triggers On | Purpose |
|-------|-------------|---------|
| `design-plan-implement` | design, plan, approach, feature | New feature development |
| `tdd-implement` | fix, bug, test, TDD | Test-driven development |
| `code-review` | review, check, PR | Code review workflow |
| `finish-branch` | finish, merge, complete | Branch completion |

Skills are **model-invoked** - Claude auto-discovers them based on description.

### 4. Custom Subagents

| Agent | Role | Mode | Purpose |
|-------|------|------|---------|
| `planner.md` | Navigator | Read-only | Design and planning |
| `reviewer.md` | Reviewer | Read-only | Code review |

### 5. Sprint 5 Task Files

| ID | Title | Priority | Complexity |
|----|-------|----------|------------|
| TASK-020 | Universal AGENTS.md template | P0 | 40 |
| TASK-021 | CLAUDE.md pointer file | P0 | 25 |
| TASK-022 | Convert flows to skills | P0 | 60 |
| TASK-023 | Create custom subagents | P1 | 40 |
| TASK-024 | Implement hooks | P1 | 45 |

---

## Key Architectural Decisions

### 1. Dual-Layer Architecture
```
project-root/
├── AGENTS.md           # Universal (Codex, Cursor, VS Code, etc.)
├── CLAUDE.md           # Claude Code pointer
├── .paircoder/         # Cross-agent content
│   ├── flows/          # Workflow definitions
│   ├── plans/          # Plan YAML
│   └── tasks/          # Task files
└── .claude/            # Claude Code native
    ├── skills/         # Model-invoked skills
    ├── agents/         # Custom subagents
    └── settings.json   # Hooks configuration
```

### 2. Skills vs Flows
- **Flows** (`.paircoder/flows/`) - Cross-agent, explicit invocation
- **Skills** (`.claude/skills/`) - Claude Code only, model-invoked

Both are maintained. Skills are optimized conversions of flows.

### 3. Roles
- PairCoder roles (Navigator, Driver, Reviewer) map to Claude Code subagents
- Claude Code's built-in Plan/Explore agents complement (not replace) custom agents
- For non-Claude agents, roles are prompting modes in flows

### 4. Task Lifecycle
- Active tasks in `.paircoder/tasks/{plan}/`
- Archive completed tasks after merge
- Metrics logged to `.paircoder/history/metrics.jsonl`

---

## Next Steps for Claude Code

### To Integrate This Package:

1. **Extract to repository**:
   ```bash
   tar -xzf sprint5-multiagent-architecture.tgz
   ```

2. **Copy templates to cookiecutter**:
   ```bash
   cp sprint5/templates/AGENTS.md tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/
   cp sprint5/templates/CLAUDE.md tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/
   ```

3. **Copy skills to .claude/**:
   ```bash
   mkdir -p .claude/skills
   cp -r sprint5/skills/* .claude/skills/
   ```

4. **Copy agents to .claude/**:
   ```bash
   mkdir -p .claude/agents
   cp sprint5/agents/* .claude/agents/
   ```

5. **Copy tasks**:
   ```bash
   cp sprint5/tasks/* .paircoder/tasks/paircoder-v2-upgrade/
   ```

6. **Update state**:
   ```bash
   cp sprint5/state.md .paircoder/context/state.md
   ```

### Recommended Task Order:
1. TASK-022 (skills) - Test skill invocation first
2. TASK-020 (AGENTS.md) - Can parallel
3. TASK-023 (subagents) - After skills work
4. TASK-021 (CLAUDE.md) - After skills and agents
5. TASK-024 (hooks) - Final polish

---

## Open Questions for Discussion

1. **Plugin Distribution**
   - Should PairCoder be a Claude Code plugin (installable via `/plugin`)?
   - Or embedded in each repo (current approach)?

2. **Skill/Flow Sync**
   - How to keep `.claude/skills/` and `.paircoder/flows/` synchronized?
   - Auto-generate one from the other?

3. **Codex Cloud**
   - Support Codex Cloud tasks or focus on CLI only?

4. **MCP Integration**
   - Should PairCoder expose an MCP server for tool access?

---

## File Manifest

```
sprint5-multiagent-architecture.tgz
├── ARCHITECTURE-v2.1.md          # 12KB - Strategic document
├── state.md                       # 4KB  - Sprint 5 state
├── templates/
│   ├── AGENTS.md                  # 4KB  - Universal template
│   └── CLAUDE.md                  # 3KB  - Claude pointer
├── skills/
│   ├── design-plan-implement/SKILL.md  # 5KB
│   ├── tdd-implement/SKILL.md          # 5KB
│   ├── code-review/SKILL.md            # 5KB
│   └── finish-branch/SKILL.md          # 4KB
├── agents/
│   ├── planner.md                 # 2KB
│   └── reviewer.md                # 2KB
└── tasks/
    ├── TASK-020.task.md           # 2KB
    ├── TASK-021.task.md           # 2KB
    ├── TASK-022.task.md           # 3KB
    ├── TASK-023.task.md           # 2KB
    └── TASK-024.task.md           # 3KB
```

Total: ~50KB uncompressed
