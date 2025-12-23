# PairCoder Migration Guide

This document covers migration paths for deprecated features.

## Flows to Skills Migration

> **Status:** Flows deprecated in v2.10.x, removed in v2.11.x

PairCoder's `.flow.md` format is being replaced by the cross-platform Agent Skills format (`SKILL.md`). See [RFC-005](rfcs/RFC-005-flows-to-skills.md) for full details.

### Quick Migration

```bash
# Convert all flows to skills
bpsai-pair migrate flows --all

# Convert single flow
bpsai-pair migrate flow-to-skill <flow-name>

# Preview without writing
bpsai-pair migrate flow-to-skill <flow-name> --dry-run
```

### Manual Migration

1. **Create skill directory:**
   ```bash
   mkdir -p .claude/skills/<flow-name>
   ```

2. **Convert frontmatter:**

   **Before (flow.md):**
   ```yaml
   ---
   name: my-workflow
   description: Helps with task X
   roles:
     driver: { primary: true }
   triggers:
     - task_x
   ---
   ```

   **After (SKILL.md):**
   ```yaml
   ---
   name: my-workflow
   description: Guides task X workflow. Helps developers complete task X efficiently.
   ---
   ```

3. **Key changes:**
   - Remove `roles:` section (skills are role-agnostic)
   - Remove `triggers:` (use description for model discovery)
   - Convert description to third-person voice
   - Add trigger context to description

4. **Validate:**
   ```bash
   bpsai-pair skill validate <skill-name>
   ```

### Configuration Updates

Remove deprecated configuration:

```yaml
# .paircoder/config.yaml
workflow:
  # flows_dir: ".paircoder/flows"  # REMOVE THIS
```

```yaml
# .paircoder/capabilities.yaml
# REMOVE flow_triggers section:
# flow_triggers:
#   feature_request: design-plan-implement
```

### Timeline

| Version | Status |
|---------|--------|
| v2.9.x | Skills fully functional, flows still work |
| v2.10.x | Deprecation warnings on flow commands |
| v2.11.x | Flow commands removed |

### Getting Help

- [RFC-005: Flows to Skills](rfcs/RFC-005-flows-to-skills.md)
- [Cross-Platform Skills Guide](CROSS_PLATFORM_SKILLS.md)
- [Skills Specification](https://agentskills.io)
