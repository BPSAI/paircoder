# PairCoder v2.1: Unified Multi-Agent Architecture

**Date**: 2025-12-15  
**Status**: Strategic Planning Document  
**Scope**: Claude Code, Codex CLI, Cursor, VS Code, and other AGENTS.md-compatible agents

---

## Executive Summary

PairCoder v2.1 introduces a **dual-layer architecture** that provides:

1. **AGENTS.md (Universal Layer)**: Cross-agent standard supported by 60k+ projects and all major coding agents
2. **Agent-Specific Optimizations**: Native features for Claude Code (skills, subagents, hooks) and others

This architecture ensures PairCoder works effectively with any AGENTS.md-compatible agent while enabling deeper integration with specific agents.

---

## Architecture Overview

```
project-root/
├── AGENTS.md                    # Universal agent instructions (cross-agent)
├── CLAUDE.md                    # Claude Code pointer (→ .claude/)
├── .paircoder/                  # Agent-agnostic PairCoder content
│   ├── config.yaml              # PairCoder configuration
│   ├── capabilities.yaml        # LLM-readable capability manifest
│   ├── context/                 # Project context files
│   │   ├── project.md           # Project overview
│   │   ├── workflow.md          # Development workflow
│   │   └── state.md             # Current state (active plan, sprint, blockers)
│   ├── flows/                   # Workflow definitions (cross-agent format)
│   │   ├── design-plan-implement.flow.md
│   │   ├── tdd-implement.flow.md
│   │   ├── code-review.flow.md
│   │   └── finish-branch.flow.md
│   ├── plans/                   # Plan YAML files
│   │   └── {plan-name}.plan.yaml
│   ├── tasks/                   # Active task files
│   │   └── {plan-slug}/
│   │       └── TASK-XXX.task.md
│   └── history/                 # Archives (completed work, metrics)
│       ├── archived-tasks/
│       └── metrics.jsonl
├── .claude/                     # Claude Code native (auto-discovered)
│   ├── skills/                  # Model-invoked skills
│   │   ├── design-plan-implement/
│   │   │   └── SKILL.md
│   │   └── tdd-implement/
│   │       └── SKILL.md
│   ├── agents/                  # Custom subagents
│   │   ├── planner.md
│   │   └── reviewer.md
│   ├── commands/                # Slash commands (/plan, /task, /status)
│   │   ├── plan.md
│   │   ├── task.md
│   │   └── status.md
│   └── settings.json            # Hooks configuration
└── tools/cli/                   # bpsai-pair CLI (orchestration layer)
```

---

## Layer 1: AGENTS.md (Universal)

### Purpose
AGENTS.md is the **entry point for all coding agents**. It provides:
- Project setup commands
- Code style guidelines
- Testing instructions
- Pointers to PairCoder's deeper capabilities

### Discovery Pattern (per Codex docs)
1. **Global scope**: `~/.codex/AGENTS.md` or `~/.codex/AGENTS.override.md`
2. **Project scope**: Walk from repo root to current directory
3. **Precedence**: Closest file wins; explicit prompts override all

### Key Principle
**AGENTS.md doesn't contain everything**—it points to `.paircoder/` for workflows and plans. This keeps AGENTS.md concise while enabling deep functionality.

### Template Structure
```markdown
# AGENTS.md

## Project Overview
Brief description of what this project does.

## Quick Setup
- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`

## Code Conventions
- Python 3.9+, type hints required
- Docstrings for public functions
- Tests in `tests/` mirroring `src/` structure

## Working with PairCoder
This project uses PairCoder for structured development workflows.

### Check Current State
Read `.paircoder/context/state.md` to understand:
- Active plan and sprint
- Current task assignments
- Any blockers

### Available Workflows
See `.paircoder/flows/` for workflow definitions:
- `design-plan-implement.flow.md` - For new features
- `tdd-implement.flow.md` - For test-driven development
- `code-review.flow.md` - For reviewing changes

### Task Management
Tasks are in `.paircoder/tasks/{plan-slug}/`:
- Read `TASK-XXX.task.md` for task details
- Update task status when starting/completing work

## Testing
- Run `pytest` before committing
- All tests must pass before PR
- Add tests for new functionality
```

---

## Layer 2: Claude Code Native (.claude/)

### Why a Separate Layer?

Claude Code has unique capabilities that other agents don't:

| Capability | Claude Code | Codex CLI | Cursor |
|------------|-------------|-----------|--------|
| Model-invoked skills | ✅ SKILL.md | ❌ | ❌ |
| Custom subagents | ✅ agents/*.md | ❌ | ❌ |
| Hooks (pre/post tool) | ✅ settings.json | ❌ | ❌ |
| Slash commands | ✅ commands/*.md | ✅ /commands | ✅ |
| Session resumption | ✅ --resume | ✅ | ❌ |
| Headless mode | ✅ -p | ✅ --exec | ❌ |

### CLAUDE.md Purpose

CLAUDE.md acts as a **pointer file** that tells Claude Code:
1. Where to find project context
2. That PairCoder skills are available
3. How to use the `.claude/` directory

```markdown
# CLAUDE.md

This project uses PairCoder v2 for structured development.

## Project Context
Read these files to understand the project:
- `.paircoder/context/project.md` - Project overview
- `.paircoder/context/workflow.md` - How we work
- `.paircoder/context/state.md` - Current state

## Available Skills
Claude Code will auto-discover skills in `.claude/skills/`:
- `design-plan-implement` - For feature development
- `tdd-implement` - For test-driven development
- `code-review` - For reviewing code
- `finish-branch` - For completing work

## Commands
- `/plan` - View or create plans
- `/task` - Manage tasks
- `/status` - Show current state

## When Starting Work
1. Read `.paircoder/context/state.md`
2. Use `/task next` to see the highest priority task
3. Follow the appropriate workflow from skills
```

### Skills vs Flows

| Aspect | Skills (.claude/skills/) | Flows (.paircoder/flows/) |
|--------|--------------------------|---------------------------|
| Discovery | Model-invoked (auto) | File-based (explicit) |
| Format | SKILL.md with frontmatter | .flow.md with frontmatter |
| Audience | Claude Code only | All agents |
| Trigger | Description matching | User/orchestrator invokes |

**Strategy**: Maintain both formats. Skills are optimized conversions of flows for Claude Code.

---

## Layer 3: Orchestration (bpsai-pair CLI)

### Role
The CLI provides:
1. **Context packing**: `bpsai-pair pack` → Generate context for any agent
2. **Task management**: `bpsai-pair task next` → Priority-based task selection
3. **Plan management**: `bpsai-pair plan show` → View plan details
4. **State synchronization**: `bpsai-pair sync` → Update state across agents
5. **Lifecycle management**: `bpsai-pair archive` → Archive completed tasks

### Headless Integration

```bash
# Claude Code headless execution
claude -p "Implement TASK-020" \
  --allowedTools "Bash,Read,Edit,Write" \
  --permission-mode acceptEdits \
  --output-format json

# Codex CLI execution
codex exec --full-auto "Implement TASK-020"

# Multi-agent orchestration
bpsai-pair pack --for-agent codex --task TASK-020 > handoff.json
codex exec --stdin < handoff.json
```

---

## Migration Strategy

### From PairCoder v1 to v2.1

1. **Phase 1**: Update AGENTS.md to point to `.paircoder/`
2. **Phase 2**: Create `.claude/` directory with skills
3. **Phase 3**: Run `bpsai-pair migrate` to move old context files
4. **Phase 4**: Validate with both Claude Code and Codex

### Backward Compatibility

- Old `context/` directory → Symlink to `.paircoder/context/`
- Old `capabilities.yaml` location → Copy to `.paircoder/`
- `AGENTS.md` fallbacks → Configure in Codex config

---

## Task Lifecycle Management

### Active Tasks
```
.paircoder/tasks/{plan-slug}/TASK-XXX.task.md
```

### Archive Strategy
```bash
# After task completion and PR merge
bpsai-pair archive --task TASK-XXX

# Result:
.paircoder/history/archived-tasks/{plan-slug}/TASK-XXX.task.md.gz
```

### Retention Policy
- Active tasks: Keep in `.paircoder/tasks/`
- Completed (merged): Archive after 7 days
- Metrics: Append to `metrics.jsonl` for cost/time tracking

---

## Role Mapping

### Claude Code Native Roles

| PairCoder Role | Claude Code Equivalent | Implementation |
|----------------|------------------------|----------------|
| Navigator | Plan subagent | Built-in, permissionMode: plan |
| Driver | General subagent | Built-in, full capability |
| Reviewer | Custom reviewer agent | `.claude/agents/reviewer.md` |

### Cross-Agent Roles

For Codex and other agents, roles are **prompting modes** defined in flows:
```markdown
## Navigator Mode
When in Navigator mode, focus on:
- Understanding requirements
- Designing solutions
- Creating plans
Do NOT write implementation code in this mode.
```

---

## Planning Mode Activation

### Claude Code
```bash
# Explicit via headless
claude -p "Plan the authentication feature" --permission-mode plan

# Via skill (auto-detected based on description)
# User says: "How should we approach adding OAuth support?"
# Claude auto-invokes design-plan-implement skill
```

### Codex CLI
```bash
# Via prompt
codex exec "Create a plan for implementing OAuth. Do not write code yet."

# Via AGENTS.md instruction
# "When asked to plan, use Navigator mode from .paircoder/flows/"
```

### Automatic Planning Detection

Both agents can be instructed to auto-detect planning needs:

```markdown
# In SKILL.md or AGENTS.md

## Auto-Planning Trigger
When a request involves:
- Multiple files or components
- Unclear requirements
- Estimated work > 30 minutes
- Words like "design", "plan", "approach", "strategy"

AUTOMATICALLY switch to planning mode before implementation.
```

---

## Metrics and Observability

### Token Tracking
```jsonl
// .paircoder/history/metrics.jsonl
{"timestamp":"2025-12-15T10:00:00Z","task":"TASK-020","agent":"claude-code","tokens_in":5000,"tokens_out":2000,"cost_usd":0.021,"duration_s":45}
{"timestamp":"2025-12-15T10:01:00Z","task":"TASK-020","agent":"codex","tokens_in":3000,"tokens_out":1500,"cost_usd":0.015,"duration_s":30}
```

### Time Tracking Integration
```yaml
# .paircoder/config.yaml
time_tracking:
  enabled: true
  provider: toggl  # or clockify, harvest
  auto_start: true
  task_pattern: "TASK-{id}: {title}"
```

---

## Implementation Phases

### Sprint 5: Claude Code Alignment (Current)
- [ ] TASK-020: Create AGENTS.md universal template
- [ ] TASK-021: Create CLAUDE.md pointer file
- [ ] TASK-022: Convert flows to `.claude/skills/*/SKILL.md`
- [ ] TASK-023: Create custom subagents (planner, reviewer)
- [ ] TASK-024: Implement hooks for auto context-sync

### Sprint 6: Cross-Agent Support
- [ ] TASK-025: Codex CLI adapter (parse .flow.md)
- [ ] TASK-026: Agent handoff protocol (pack for transfer)
- [ ] TASK-027: Headless mode orchestration scripts
- [ ] TASK-028: Multi-agent session management

### Sprint 7: Lifecycle & Observability
- [ ] TASK-029: Task archive command and retention policy
- [ ] TASK-030: Token/cost tracking implementation
- [ ] TASK-031: Time tracking integration
- [ ] TASK-032: Benchmarking framework

---

## Open Questions

1. **Plugin Distribution**: Should PairCoder be a Claude Code plugin or embedded in repos?
2. **Skill Sync**: How do we keep skills and flows in sync automatically?
3. **Codex Cloud**: Should we support Codex Cloud tasks or focus on CLI?
4. **MCP Integration**: Should PairCoder expose an MCP server for tool access?

---

## References

- [AGENTS.md Standard](https://agents.md/)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)
- [Codex CLI AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md/)
- [OpenAI Cookbook: Codex + Agents SDK](https://cookbook.openai.com/examples/codex/codex_mcp_agents_sdk/)
