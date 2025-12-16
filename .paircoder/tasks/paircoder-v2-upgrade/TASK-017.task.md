---
id: TASK-017
plan: plan-2025-01-paircoder-v2-upgrade
title: Update USER_GUIDE.md for v2
type: docs
priority: P2
complexity: 30
status: pending
sprint: sprint-4
tags: [docs, user-guide, release]
---

# Objective

Rewrite the USER_GUIDE.md to document v2 features including the new directory structure, planning workflow, flows, and LLM integration.

# Implementation Plan

1. Update directory structure section for `.paircoder/`
2. Add Planning System section:
   - Creating plans
   - Managing tasks
   - Sprint workflow
3. Add Flows section:
   - Available flows
   - Running flows
   - Creating custom flows
4. Add LLM Integration section:
   - How capabilities.yaml works
   - Using with Claude Code
   - Using with other agents
5. Update CLI reference with new commands
6. Add migration notes for v1 users

# File Location

- `tools/cli/USER_GUIDE.md`

# Sections to Include

```markdown
# PairCoder User Guide

## Quick Start
## Installation
## Directory Structure (v2)
## Planning System
  - Creating Plans
  - Managing Tasks  
  - Sprints
## Flows
  - Built-in Flows
  - Running Flows
  - Custom Flows
## Working with AI Agents
  - Capabilities Manifest
  - Claude Code Integration
  - Other Agents
## CLI Reference
  - init
  - feature
  - plan (NEW)
  - task (NEW)
  - flow
  - pack
  - context-sync
  - status
  - validate
## Migration from v1
## Troubleshooting
```

# Acceptance Criteria

- [ ] All v2 features documented
- [ ] New CLI commands (plan, task) documented with examples
- [ ] Directory structure reflects `.paircoder/` layout
- [ ] Planning workflow explained with example
- [ ] LLM integration section explains capabilities.yaml
- [ ] Migration notes for v1 users
- [ ] No references to deprecated v1 structure

# Verification

```bash
# Check for v2 references
grep -c ".paircoder" tools/cli/USER_GUIDE.md  # Should be many
grep -c "plan new" tools/cli/USER_GUIDE.md    # Should exist
grep -c "task list" tools/cli/USER_GUIDE.md   # Should exist

# Check no v1 references in wrong places
grep "context/" tools/cli/USER_GUIDE.md       # Should be minimal/migration only
```

# Notes

The USER_GUIDE is the primary documentation users will read. It should be comprehensive but not overwhelming. Use clear examples and keep explanations concise.
