---
id: TASK-021
plan: plan-2025-01-paircoder-v2-upgrade
title: Create CLAUDE.md pointer file template
type: feature
priority: P0
complexity: 25
status: pending
sprint: sprint-5
tags: [docs, claude-code, foundation]
---

# Objective

Create a CLAUDE.md template that acts as a pointer file for Claude Code,
directing it to PairCoder's `.claude/` directory structure and `.paircoder/`
context files.

# Background

Claude Code reads CLAUDE.md at project root. Unlike AGENTS.md (which is
universal), CLAUDE.md can contain Claude-specific instructions:
- References to `.claude/skills/` for model-invoked skills
- References to `.claude/agents/` for custom subagents
- Slash command availability
- Hooks configuration

# Implementation Plan

1. Create CLAUDE.md template with:
   - Project context file references
   - Available skills list
   - Available slash commands
   - Custom agents reference
   - Quick start checklist

2. Template should be:
   - Concise (pointer, not comprehensive)
   - Reference `.paircoder/` for project context
   - Reference `.claude/` for Claude-specific features

3. Add to cookiecutter template

# Acceptance Criteria

- [ ] CLAUDE.md template created
- [ ] Points to `.paircoder/context/` files
- [ ] Lists available skills
- [ ] Lists available slash commands
- [ ] Includes quick start checklist
- [ ] Integrated into cookiecutter template

# Verification

```bash
# Claude Code should read and understand
# Verify by asking "What skills are available?"
```

# Files to Create/Modify

- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CLAUDE.md`

# Dependencies

- TASK-022 (skills must exist to reference them)

# Notes

CLAUDE.md works alongside AGENTS.md - they're complementary, not competing.
