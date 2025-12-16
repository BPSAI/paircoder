---
id: TASK-016
plan: plan-2025-01-paircoder-v2-upgrade
title: Update cookiecutter template for v2
type: refactor
priority: P1
complexity: 50
status: pending
sprint: sprint-4
tags: [template, cookiecutter, release]
---

# Objective

Update the cookiecutter template at `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` to deliver the v2 structure when users run `bpsai-pair init`.

# Implementation Plan

1. Restructure template to use `.paircoder/` directory
2. Add default `config.yaml` with v2 schema
3. Add `capabilities.yaml` manifest (simplified for new projects)
4. Add context files: `project.md`, `workflow.md`, `state.md`
5. Add default flows: `design-plan-implement.flow.md`, `tdd-implement.flow.md`
6. Update root `AGENTS.md` and `CLAUDE.md` as pointers
7. Remove old `context/` structure from template
8. Update `cookiecutter.json` with any new variables

# Current Template Location

```
tools/cli/bpsai_pair/data/cookiecutter-paircoder/
└── {{cookiecutter.project_slug}}/
    ├── .paircoder/           # ADD: v2 structure
    │   ├── config.yaml
    │   ├── capabilities.yaml
    │   ├── context/
    │   │   ├── project.md
    │   │   ├── workflow.md
    │   │   └── state.md
    │   └── flows/
    │       ├── design-plan-implement.flow.md
    │       └── tdd-implement.flow.md
    ├── AGENTS.md             # UPDATE: point to .paircoder/
    ├── CLAUDE.md             # UPDATE: point to .paircoder/
    └── [other governance files]
```

# Files to Modify

- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/*` (create)
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/AGENTS.md` (update)
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CLAUDE.md` (update)
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/cookiecutter.json` (if needed)

# Acceptance Criteria

- [ ] `bpsai-pair init` creates `.paircoder/` directory
- [ ] Config file is at `.paircoder/config.yaml` with version: "2.0"
- [ ] Capabilities manifest included
- [ ] Context files created with template content
- [ ] At least 2 default flows included
- [ ] Root AGENTS.md points to `.paircoder/`
- [ ] Old `context/` at root is NOT created
- [ ] Smoke test: init in fresh directory works

# Verification

```bash
# Create fresh test directory
mkdir /tmp/test-init && cd /tmp/test-init
git init

# Run init
bpsai-pair init

# Verify structure
ls -la .paircoder/
cat .paircoder/config.yaml | grep version
ls .paircoder/flows/
cat AGENTS.md | head -5
```

# Notes

This is the most complex Sprint 4 task. The template changes what ALL new users receive, so it must be thoroughly tested. Consider the following:

1. Keep template simple - users can add complexity later
2. Default capabilities.yaml should be minimal but functional
3. Default flows should be the most commonly needed ones
4. state.md should start empty (no active plan)
