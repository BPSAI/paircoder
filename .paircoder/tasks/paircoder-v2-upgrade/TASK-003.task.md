---
id: TASK-003
plan: plan-2025-01-paircoder-v2-upgrade
title: Update ADR 0002 - Add planning system
type: docs
priority: P0
complexity: 20
status: done
sprint: sprint-1
tags: [docs, adr, architecture]
---

# Objective

Correct ADR 0002 to include the planning system (Goals → Tasks → Sprints)
which was incorrectly listed under "What's Explicitly NOT Included".

# Implementation Plan

1. Remove "Planning OS / task hierarchy" from exclusions
2. Add Planning System section documenting:
   - Plan schema
   - Task schema
   - Sprint structure
3. Add LLM Capability Manifest to architecture
4. Update directory structure diagram
5. Add new CLI commands section
6. Update implementation phases

# Acceptance Criteria

- [ ] ADR 0002 no longer excludes planning
- [ ] Plan YAML schema documented
- [ ] Task YAML+MD schema documented
- [ ] Capability manifest documented
- [ ] Directory structure updated
- [ ] New CLI commands listed

# Verification

```bash
grep -v "Planning OS" docs/adr/0002-paircoder-v2.md  # Should not find old exclusion
grep "Planning System" docs/adr/0002-paircoder-v2.md  # Should find new section
grep "capabilities.yaml" docs/adr/0002-paircoder-v2.md  # Should find reference
```

# Notes

- This was a critical oversight in the original ADR
- The planning system is core to v2, not optional
- Revision date should be noted in the ADR
