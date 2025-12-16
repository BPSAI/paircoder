---
id: TASK-018
plan: plan-2025-01-paircoder-v2-upgrade
title: Update README.md for v2
type: docs
priority: P2
complexity: 20
status: pending
sprint: sprint-4
tags: [docs, readme, release]
---

# Objective

Update the main README.md files with v2 features overview, new commands, and updated quick start instructions.

# Implementation Plan

1. Update root `README.md`:
   - Update feature highlights for v2
   - Update quick start section
   - Add v2 badge or version indicator

2. Update `tools/cli/README.md`:
   - Update installation instructions
   - Update CLI command overview
   - Add new commands (plan, task)
   - Update directory structure

# Files to Modify

- `README.md` (root)
- `tools/cli/README.md`

# Key Updates

## Root README.md

```markdown
## Features

- **Planning System** - Goals → Tasks → Sprints workflow
- **Flows** - Declarative workflows for common tasks
- **LLM Integration** - Works with Claude Code, Codex CLI, and others
- **Context Management** - Structured project memory
- **Agent Packs** - Portable context for handoff
```

## tools/cli/README.md

```markdown
## Commands

- `bpsai-pair init` - Initialize project with v2 scaffolding
- `bpsai-pair plan` - Manage plans and goals
- `bpsai-pair task` - Manage tasks
- `bpsai-pair flow` - Run workflows
- `bpsai-pair pack` - Create agent context package
- `bpsai-pair status` - Show project status
```

# Acceptance Criteria

- [ ] v2 features highlighted in root README
- [ ] Quick start uses v2 structure
- [ ] CLI README shows all commands including plan/task
- [ ] No misleading v1 references
- [ ] Version badge updated (if applicable)

# Verification

```bash
# Check root README
grep "Planning" README.md
grep "Flows" README.md

# Check CLI README  
grep "plan" tools/cli/README.md
grep "task" tools/cli/README.md
```

# Notes

READMEs are often the first thing users see. Keep them concise but informative. Link to USER_GUIDE for detailed documentation.
