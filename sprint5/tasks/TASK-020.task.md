---
id: TASK-020
plan: plan-2025-01-paircoder-v2-upgrade
title: Create universal AGENTS.md template
type: feature
priority: P0
complexity: 40
status: pending
sprint: sprint-5
tags: [docs, cross-agent, foundation]
---

# Objective

Create an AGENTS.md template that works as the universal entry point for all
AGENTS.md-compatible coding agents (Codex, Cursor, VS Code, Jules, etc.).

# Background

AGENTS.md is an open standard supported by 60k+ projects and used by:
- OpenAI Codex CLI
- Google Jules
- Cursor
- VS Code
- Windsurf
- GitHub Copilot
- And many more

Our AGENTS.md should point agents to `.paircoder/` for structured workflows
while remaining concise and useful as a standalone file.

# Implementation Plan

1. Create AGENTS.md template with:
   - Project overview section
   - Quick setup commands
   - Code conventions
   - PairCoder integration instructions
   - Workflow quick reference
   - Important files reference

2. Ensure template is:
   - Agent-agnostic (no Claude-specific content)
   - Concise (under 32KB for Codex compatibility)
   - Self-contained for basic tasks
   - Points to `.paircoder/` for advanced features

3. Add to cookiecutter template

# Acceptance Criteria

- [ ] AGENTS.md template created
- [ ] Template works with Codex CLI (verified with `/init` comparison)
- [ ] Template points to `.paircoder/` directory structure
- [ ] Workflow quick reference included
- [ ] Under 32KB total size
- [ ] Integrated into cookiecutter template

# Verification

```bash
# Test with Codex CLI
codex --ask-for-approval never "Summarize the current instructions."
# Should reference both AGENTS.md and .paircoder/ files
```

# Files to Create/Modify

- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/AGENTS.md`

# Notes

Reference the AGENTS.md standard: https://agents.md/
