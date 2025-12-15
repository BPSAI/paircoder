---
id: TASK-002
plan: plan-2025-01-paircoder-v2-upgrade
title: Create LLM capability manifest
type: feature
priority: P0
complexity: 40
status: done
sprint: sprint-1
tags: [llm, integration, capabilities]
---

# Objective

Create `.paircoder/capabilities.yaml` that tells LLMs what they can do,
when to use each capability, and how to invoke them.

# Implementation Plan

1. Define capability structure (id, name, description, when_to_use, how_to_invoke)
2. Document all planning capabilities (create_plan, view_plan, update_task_status)
3. Document all flow capabilities (run_flow, list_flows)
4. Document context capabilities (sync_context, pack_context)
5. Document feature branch capabilities
6. Add flow triggers with pattern matching
7. Define role descriptions (navigator, driver, reviewer)
8. Add notes for LLM guidance

# Acceptance Criteria

- [ ] `capabilities.yaml` is valid YAML
- [ ] All CLI commands documented with how_to_invoke
- [ ] All capabilities have when_to_use patterns
- [ ] Flow triggers defined with pattern lists
- [ ] Roles defined with descriptions
- [ ] Notes section guides LLM behavior

# Verification

```bash
python -c "import yaml; yaml.safe_load(open('.paircoder/capabilities.yaml'))"
grep -c "when_to_use" .paircoder/capabilities.yaml  # Should be multiple
grep "navigator" .paircoder/capabilities.yaml
```

# Notes

- This is the key to Claude Code integration
- LLMs should read this file to understand what they can do
- Patterns in when_to_use help LLMs recognize when to suggest capabilities
