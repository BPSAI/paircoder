# Current State

## Active Plan
**Plan**: plan-2025-01-paircoder-v2-upgrade  
**Sprint**: sprint-5 (Claude Code Alignment)  
**Started**: 2025-12-15  

## Strategic Context

Sprint 5 focuses on aligning PairCoder with Claude Code's native capabilities
while maintaining cross-agent compatibility through the AGENTS.md standard.

### Key Discoveries (from documentation review)
1. **AGENTS.md is a universal standard** - Supported by 60k+ projects, Codex, Cursor, VS Code, etc.
2. **Claude Code has unique capabilities** - Skills (model-invoked), subagents, hooks
3. **Dual-layer architecture needed** - Universal AGENTS.md + Claude-specific .claude/

### Architecture Decision
- **AGENTS.md** → Universal entry point for all agents
- **CLAUDE.md** → Pointer to Claude-specific features
- **.paircoder/** → Cross-agent content (flows, plans, tasks)
- **.claude/** → Claude Code native (skills, agents, hooks)

## Sprint Progress

### Sprint 5 Tasks

| ID | Title | Priority | Status | Complexity |
|----|-------|----------|--------|------------|
| TASK-020 | Create universal AGENTS.md template | P0 | pending | 40 |
| TASK-021 | Create CLAUDE.md pointer file | P0 | pending | 25 |
| TASK-022 | Convert flows to skills (SKILL.md) | P0 | pending | 60 |
| TASK-023 | Create custom subagents | P1 | pending | 40 |
| TASK-024 | Implement hooks for auto context-sync | P1 | pending | 45 |

**Total Complexity**: 210 points

### Recommended Order
1. TASK-022 (skills) - Foundation for other tasks
2. TASK-020 (AGENTS.md) - Can be done in parallel
3. TASK-023 (subagents) - Depends on skills
4. TASK-021 (CLAUDE.md) - References skills and agents
5. TASK-024 (hooks) - Can be done last

## Completed Sprints

| Sprint | Focus | Tasks | Status |
|--------|-------|-------|--------|
| Sprint 1 | Foundation | 6/6 | ✅ Done |
| Sprint 2 | Planning Module | 5/5 | ✅ Done |
| Sprint 3 | Flow Integration | 5/5 | ✅ Done |
| Sprint 4 | Deferred | 0/4 | ⏸️ Paused |

Sprint 4 (template/docs/release) was paused pending architectural alignment.

## Files Prepared for Sprint 5

Located in `/home/claude/sprint5/`:

```
sprint5/
├── ARCHITECTURE-v2.1.md       # Strategic architecture document
├── templates/
│   ├── AGENTS.md              # Universal template (draft)
│   └── CLAUDE.md              # Claude pointer file (draft)
├── skills/
│   ├── design-plan-implement/
│   │   └── SKILL.md           # Converted from flow
│   ├── tdd-implement/
│   │   └── SKILL.md
│   ├── code-review/
│   │   └── SKILL.md
│   └── finish-branch/
│       └── SKILL.md
├── agents/
│   ├── planner.md             # Navigator role equivalent
│   └── reviewer.md            # Reviewer role equivalent
└── tasks/
    ├── TASK-020.task.md
    ├── TASK-021.task.md
    ├── TASK-022.task.md
    ├── TASK-023.task.md
    └── TASK-024.task.md
```

## Next Actions

1. **Review sprint5/ deliverables** - Verify templates and skills meet requirements
2. **Begin TASK-022** - Copy skills to `.claude/skills/` in target repo
3. **Test skill invocation** - Verify Claude Code auto-discovers skills
4. **Iterate based on testing** - Refine descriptions if skills don't trigger

## Blockers

None currently.

## Open Questions

1. **Plugin vs Embedded**: Should PairCoder be a Claude Code plugin?
2. **Skill Sync**: How to keep skills and flows synchronized?
3. **Codex Cloud**: Support cloud tasks or focus on CLI?

## Cross-Agent Reference

| Agent | Config File | Discovery |
|-------|-------------|-----------|
| Claude Code | CLAUDE.md, .claude/ | Auto-discovery |
| OpenAI Codex | AGENTS.md | Path walk from root |
| Cursor | AGENTS.md | Project root |
| VS Code | AGENTS.md | Project root |
| GitHub Copilot | AGENTS.md | Project root |

## Commands Available

```bash
# CLI commands (if bpsai-pair installed)
bpsai-pair status          # Show current state
bpsai-pair task next       # Get highest priority task
bpsai-pair task show XXX   # View task details
bpsai-pair flow list       # List available flows
bpsai-pair pack            # Create context package
```
