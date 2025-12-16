---
id: TASK-007
plan: plan-2025-01-paircoder-v2-upgrade
title: Implement plan YAML parser
type: feature
priority: P0
complexity: 40
status: done
sprint: sprint-2
tags: [parser, planning, core]
---

# Objective

Create a parser for plan files (`.plan.yaml`) that can load, validate, and save plans.

# Implementation Plan

1. Create `planning/models.py` with Plan, Sprint dataclasses
2. Create `planning/parser.py` with PlanParser class
3. Implement `list_plans()`, `parse()`, `parse_all()`, `get_plan_by_id()`
4. Implement `save()` for creating new plans
5. Add proper error handling for malformed YAML

# Files Created

- `tools/cli/bpsai_pair/planning/models.py` - Plan, Sprint, PlanStatus, PlanType
- `tools/cli/bpsai_pair/planning/parser.py` - PlanParser class

# Acceptance Criteria

- [x] Can parse `.plan.yaml` files
- [x] Plan dataclass with all fields (id, title, type, status, goals, sprints, tasks)
- [x] Sprint dataclass with task references
- [x] `to_dict()` and `from_dict()` methods for serialization
- [x] Error handling for invalid files

# Verification

```bash
cd tools/cli
python -c "from bpsai_pair.planning import PlanParser; print('OK')"
pytest tests/test_planning.py -v  # if tests exist
```

# Notes

Completed as part of Sprint 2. Parser supports the full plan schema from the upgrade plan.
