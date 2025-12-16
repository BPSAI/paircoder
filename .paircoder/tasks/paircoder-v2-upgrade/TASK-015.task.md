---
id: TASK-015
plan: plan-2025-01-paircoder-v2-upgrade
title: Update flow parser for .flow.md format
type: refactor
priority: P1
complexity: 40
status: done
sprint: sprint-2
tags: [parser, flows, refactor]
---

# Objective

Extend the flow parser to support the new `.flow.md` format (YAML frontmatter + Markdown body) while maintaining backward compatibility with legacy `.flow.yml` files.

# Implementation Plan

1. Create `flows/parser_v2.py` with new Flow, FlowRole, FlowStep dataclasses
2. Implement `parse_frontmatter()` for YAML extraction
3. Create FlowParser class supporting both formats
4. Implement deduplication (prefer `.flow.md` over `.flow.yml`)
5. Update CLI to use v2 parser for flow commands
6. Update tests for new format

# Files Created/Modified

- `tools/cli/bpsai_pair/flows/parser_v2.py` - New v2 parser
- `tools/cli/bpsai_pair/cli.py` - Updated flow commands to use v2 parser
- `tools/cli/tests/test_flow_cli.py` - Updated tests for .flow.md format

# Acceptance Criteria

- [x] Can parse `.flow.md` files with YAML frontmatter
- [x] Can parse legacy `.flow.yml` files
- [x] Deduplicates by name (prefers .flow.md)
- [x] Flow dataclass includes: name, version, description, when_to_use, roles, triggers, tags, body
- [x] `bpsai-pair flow list` shows both formats with format badge [MD]/[YML]
- [x] `bpsai-pair flow show` displays full body content
- [x] Existing tests pass

# Verification

```bash
bpsai-pair flow list
bpsai-pair flow show design-plan-implement
pytest tests/test_flow_cli.py -v
```

# Notes

This task was pulled forward from Sprint 3 to Sprint 2 because it was blocking proper flow discovery. The old parser only recognized `.flow.yml` files, causing the CLI to show only 1 flow instead of 4.
