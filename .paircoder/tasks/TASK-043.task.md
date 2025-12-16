---
id: TASK-043
title: Add Trello skills to cookiecutter template
plan: plan-2025-01-paircoder-v2-upgrade
type: feature
priority: P1
complexity: 25
status: pending
sprint: sprint-10
tags:
  - trello
  - skills
  - template
---

# Objective

Add the `trello-task-workflow` and `trello-aware-planning` skills to the cookiecutter template so new projects get Trello integration skills out of the box.

# Implementation Plan

## 1. Create Skill Directories in Template

Create the skill directories in the cookiecutter template:

```
tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/
└── .claude/
    └── skills/
        ├── trello-task-workflow/
        │   └── SKILL.md
        └── trello-aware-planning/
            └── SKILL.md
```

## 2. Add trello-task-workflow Skill

Copy the skill file to:
`tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/skills/trello-task-workflow/SKILL.md`

(Use the SKILL-trello-task-workflow.md content already created)

## 3. Add trello-aware-planning Skill

Copy the skill file to:
`tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/skills/trello-aware-planning/SKILL.md`

(Use the SKILL-trello-aware-planning.md content already created)

## 4. Update capabilities.yaml

Update `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/capabilities.yaml`:

```yaml
# Add to skills section
skills:
  # ... existing skills ...
  
  trello-task-workflow:
    description: "Work on tasks from Trello board"
    triggers:
      - work on task
      - start task
      - next task
      - finish task
      - I'm blocked
    requires:
      - trello_connected
    
  trello-aware-planning:
    description: "Create and organize tasks in Trello"
    triggers:
      - plan feature
      - break down work
      - create tasks
      - organize sprint
    requires:
      - trello_connected

# Add capability flag
capabilities:
  # ... existing capabilities ...
  trello_connected: false  # Set true after `bpsai-pair trello connect`
```

## 5. Update CLAUDE.md Template

Update `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CLAUDE.md` to mention Trello skills:

Add section:

```markdown
## Trello Integration (Optional)

If this project uses Trello for task management:

1. Connect: `bpsai-pair trello connect`
2. Set board: `bpsai-pair trello use-board <id>`
3. Use skills:
   - `trello-task-workflow` - Work on tasks
   - `trello-aware-planning` - Create tasks during planning

### Quick Commands

```bash
bpsai-pair ttask list --agent        # Show AI-ready tasks
bpsai-pair ttask start TRELLO-123    # Claim a task
bpsai-pair ttask done TRELLO-123 -s "Done"  # Complete task
```
```

## 6. Verify Template Structure

After adding, the complete `.claude/skills/` structure should be:

```
.claude/skills/
├── code-review/
│   └── SKILL.md
├── design-plan-implement/
│   └── SKILL.md
├── finish-branch/
│   └── SKILL.md
├── tdd-implement/
│   └── SKILL.md
├── trello-aware-planning/      # NEW
│   └── SKILL.md
└── trello-task-workflow/       # NEW
    └── SKILL.md
```

# Files to Create/Modify

| Action | File |
|--------|------|
| Create | `.../.claude/skills/trello-task-workflow/SKILL.md` |
| Create | `.../.claude/skills/trello-aware-planning/SKILL.md` |
| Modify | `.../.paircoder/capabilities.yaml` |
| Modify | `.../CLAUDE.md` |

# Acceptance Criteria

- [ ] Both skill directories exist in cookiecutter template
- [ ] Skills have proper YAML frontmatter with triggers
- [ ] capabilities.yaml lists the new skills
- [ ] capabilities.yaml includes `trello_connected` capability
- [ ] CLAUDE.md documents Trello integration
- [ ] `bpsai-pair init` creates project with all 6 skills
- [ ] Skills are model-invoked (Claude auto-discovers them)

# Verification

```bash
# Create test project
cd /tmp
bpsai-pair init test-trello-skills
cd test-trello-skills

# Verify skills exist
ls -la .claude/skills/
# Should show 6 directories including trello-*

# Verify skill content
cat .claude/skills/trello-task-workflow/SKILL.md | head -20
# Should show YAML frontmatter with triggers

# Verify capabilities
cat .paircoder/capabilities.yaml | grep -A 5 trello
# Should show both skills listed
```
