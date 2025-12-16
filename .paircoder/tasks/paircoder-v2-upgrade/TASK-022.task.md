---
id: TASK-022
plan: plan-2025-01-paircoder-v2-upgrade
title: Convert flows to Claude Code skills (SKILL.md)
type: feature
priority: P0
complexity: 60
status: done
sprint: sprint-5
tags: [claude-code, skills, flows]
---

# Objective

Convert the four core PairCoder flows into Claude Code skills with SKILL.md
format. Skills are model-invoked (auto-discovered by description) vs flows
which are explicitly called.

# Background

Claude Code skills have specific requirements:
- Must be in `.claude/skills/{skill-name}/SKILL.md`
- YAML frontmatter with: name, description, allowed-tools (optional)
- Description is CRITICAL - it determines when Claude uses the skill
- Skills are auto-invoked based on description matching

# Flows to Convert

1. `design-plan-implement.flow.md` → `design-plan-implement/SKILL.md`
2. `tdd-implement.flow.md` → `tdd-implement/SKILL.md`
3. `code-review.flow.md` → `code-review/SKILL.md`
4. `finish-branch.flow.md` → `finish-branch/SKILL.md`

# Implementation Plan

For each flow:

1. Create skill directory in `.claude/skills/`
2. Convert flow content to SKILL.md format:
   - Add YAML frontmatter with name, description, allowed-tools
   - Keep workflow content as markdown body
   - Optimize description for trigger words

3. Description must include:
   - What the skill does
   - When to use it
   - Trigger keywords

# SKILL.md Format

```markdown
---
name: skill-name
description: What it does. When to use it. Trigger words.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Skill Title

## When This Skill Activates
...

## Instructions
...
```

# Acceptance Criteria

- [ ] design-plan-implement skill created with trigger words: design, plan, approach, feature
- [ ] tdd-implement skill created with trigger words: fix, bug, test, TDD, implement
- [ ] code-review skill created with trigger words: review, check, PR, evaluate
- [ ] finish-branch skill created with trigger words: finish, merge, complete, ship
- [ ] All skills have appropriate allowed-tools restrictions
- [ ] Skills tested with Claude Code (auto-invocation works)
- [ ] Skills added to cookiecutter template

# Verification

```bash
# Test each skill trigger
# Say "How should I approach adding authentication?"
# → Should trigger design-plan-implement

# Say "Fix the bug in the parser"
# → Should trigger tdd-implement

# Say "Review these changes"
# → Should trigger code-review

# Say "I'm done, let's merge"
# → Should trigger finish-branch
```

# Files to Create

- `.claude/skills/design-plan-implement/SKILL.md`
- `.claude/skills/tdd-implement/SKILL.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/finish-branch/SKILL.md`

# Notes

Original flows in `.paircoder/flows/` are PRESERVED for cross-agent compatibility.
Skills are Claude Code optimized versions.
