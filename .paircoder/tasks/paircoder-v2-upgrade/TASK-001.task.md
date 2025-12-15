---
id: TASK-001
plan: plan-2025-01-paircoder-v2-upgrade
title: Create v2 directory structure in this repo
type: refactor
priority: P0
complexity: 30
status: done
sprint: sprint-1
tags: [structure, migration, foundation]
---

# Objective

Migrate this repo from current structure to v2 `.paircoder/` layout.

# Implementation Plan

1. Create `.paircoder/` directory structure
2. Create `config.yaml` with v2 schema
3. Create context files (`project.md`, `workflow.md`, `state.md`)
4. Create capability manifest (`capabilities.yaml`)
5. Create core flows
6. Create root pointer files (`AGENTS.md`, `CLAUDE.md`)
7. Create plans and tasks directories with initial content

# Acceptance Criteria

- [ ] `.paircoder/config.yaml` exists and is valid
- [ ] `.paircoder/capabilities.yaml` exists
- [ ] `.paircoder/context/project.md` exists
- [ ] `.paircoder/context/workflow.md` exists
- [ ] `.paircoder/context/state.md` exists
- [ ] `.paircoder/flows/` contains 4 core flows
- [ ] Root `AGENTS.md` points to `.paircoder/`
- [ ] Root `CLAUDE.md` points to `.paircoder/`

# Verification

```bash
ls -la .paircoder/
ls -la .paircoder/context/
ls -la .paircoder/flows/
cat AGENTS.md | head -5
cat CLAUDE.md | head -5
```

# Notes

- This task creates the foundation for all v2 features
- Old `context/` directory at root will be deprecated after verification
- Files created here will be committed to the repo
