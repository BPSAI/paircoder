---
id: TASK-008
plan: plan-2025-01-paircoder-v2-upgrade
title: Implement task YAML+MD parser
type: feature
priority: P0
complexity: 35
status: done
sprint: sprint-2
tags: [parser, planning, tasks]
---

# Objective

Create a parser for task files (`.task.md`) that use YAML frontmatter + Markdown body format.

# Implementation Plan

1. Add Task dataclass to `planning/models.py`
2. Implement `parse_frontmatter()` function for YAML frontmatter extraction
3. Create TaskParser class in `planning/parser.py`
4. Implement `list_tasks()`, `parse()`, `parse_all()`, `get_task_by_id()`
5. Implement `save()` for creating new tasks
6. Implement `update_status()` for status changes

# Files Modified

- `tools/cli/bpsai_pair/planning/models.py` - Added Task, TaskStatus
- `tools/cli/bpsai_pair/planning/parser.py` - Added TaskParser, parse_frontmatter()

# Acceptance Criteria

- [x] Can parse `.task.md` files with YAML frontmatter
- [x] Task dataclass with all fields (id, plan, title, status, priority, complexity, etc.)
- [x] Body content preserved as markdown
- [x] Can filter tasks by plan slug
- [x] Can update task status in-place

# Verification

```bash
cd tools/cli
python -c "from bpsai_pair.planning import TaskParser; print('OK')"
```

# Notes

The frontmatter regex pattern handles the `---` delimiters properly. Body content after the closing `---` is preserved for display in task details.
