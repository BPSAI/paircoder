# RFC-005: Flows to Skills Migration

## Status: Draft
## Author: PairCoder Team
## Created: 2025-12-23

---

## Summary

This RFC proposes deprecating PairCoder's proprietary `.flow.md` format in favor of the cross-platform Agent Skills specification (`SKILL.md`). The Agent Skills format has achieved broad industry adoption and provides better interoperability across AI coding tools.

## Motivation

### Industry Convergence

The Agent Skills format (agentskills.io) is now supported by:
- Claude Code
- OpenAI Codex CLI
- Cursor
- VS Code (Copilot)
- GitHub
- Amp
- Goose
- Letta
- Continue.dev
- Windsurf

Maintaining a separate `.flow.md` format creates several problems:

1. **Dual Maintenance Burden**: Updates must be made to both flows and skills
2. **User Confusion**: Unclear when to use flows vs skills
3. **Portability Loss**: Flows cannot be shared with other AI tools
4. **Technical Debt**: Parallel codebases for similar functionality

### Current State Analysis

#### Flows Infrastructure

**Module Structure:**
```
tools/cli/bpsai_pair/flows/
├── __init__.py
├── models.py      # Flow, Step, StepStatus dataclasses
└── parser.py      # FlowParser with v1/v2 format support
```

**Flow Format (.flow.md):**
```yaml
---
name: flow-name
version: 1
description: >
  Flow description...
when_to_use:
  - trigger_pattern
roles:
  navigator: { primary: true }
  driver: { primary: false }
triggers:
  - feature_request
tags:
  - design
---

# Flow Title

## Phase 1 - Design
Instructions here...
```

**CLI Commands:**
- `bpsai-pair flow list` - List all flows
- `bpsai-pair flow show <name>` - Show flow details
- `bpsai-pair flow run <name>` - Execute a flow
- `bpsai-pair flow validate` - Validate flow files

**Configuration:**
```yaml
# .paircoder/config.yaml
workflow:
  flows_dir: ".paircoder/flows"
```

**Capabilities Integration:**
```yaml
# .paircoder/capabilities.yaml
flow_triggers:
  feature_request: design-plan-implement
  bugfix: implementing-with-tdd
  review: reviewing-code
```

#### Skills Infrastructure

**Module Structure:**
```
tools/cli/bpsai_pair/skills/
├── __init__.py
├── cli_commands.py   # Typer commands
├── exporter.py       # Cross-platform export
├── gap_detector.py   # Pattern detection
├── generator.py      # Auto-generation
├── installer.py      # Skill installation
├── suggestion.py     # Skill suggestions
└── validator.py      # Spec compliance
```

**Skill Format (SKILL.md):**
```yaml
---
name: skill-name
description: Third-person voice description. Guides...
---

# Skill Title

## Trigger
Use when...

## Workflow
1. Step one
2. Step two
```

**CLI Commands:**
- `bpsai-pair skill list` - List skills
- `bpsai-pair skill validate` - Validate against spec
- `bpsai-pair skill install` - Install from URL/path
- `bpsai-pair skill export` - Export to Cursor/Continue/Windsurf
- `bpsai-pair skill suggest` - Suggest new skills
- `bpsai-pair skill gaps` - Detect skill gaps
- `bpsai-pair skill generate` - Generate from gaps

## Detailed Design

### Migration Mapping

| Flow Concept | Skills Equivalent | Migration Notes |
|--------------|-------------------|-----------------|
| `.flow.md` file | `SKILL.md` file | Different frontmatter schema |
| `name:` field | `name:` field | Direct mapping |
| `description:` | `description:` | Must be third-person voice |
| `when_to_use:` | In description | Merge into description |
| `roles:` section | Not applicable | Skills are role-agnostic |
| `triggers:` | `description:` keywords | Model-invoked, not explicit |
| `tags:` | Not applicable | Use description for discovery |
| `steps:` (v1) | Markdown workflow | Free-form instructions |
| Markdown body | Markdown body | Direct mapping |
| `flow run <name>` | Model-invoked | Skills auto-discovered |
| `flows_dir` config | `.claude/skills/` | Standard location |
| `flow_triggers` | Description triggers | Natural language matching |

### Conversion Rules

1. **Name**: Keep as-is (already uses kebab-case)
2. **Description**:
   - Convert to third-person voice
   - Incorporate `when_to_use` triggers
   - Must be under 1024 characters
3. **Roles**: Remove entirely (skills are role-agnostic)
4. **Body**: Keep markdown content, remove step numbering if too rigid

### Example Conversion

**Before (flow.md):**
```yaml
---
name: implementing-with-tdd
version: 1
description: >
  Implement features using test-driven development.
when_to_use:
  - bugfix
  - feature_implementation
roles:
  driver: { primary: true }
triggers:
  - bugfix
  - tdd
---

# TDD Implementation

## Phase 1 - Red
Write failing tests first...
```

**After (SKILL.md):**
```yaml
---
name: implementing-with-tdd
description: Guides test-driven development workflow for bug fixes and feature implementation. Follows red-green-refactor cycle to ensure code quality.
---

# TDD Implementation

## Trigger
Use when implementing bug fixes or features where test coverage is important.

## Workflow

### 1. Red Phase
Write failing tests first...
```

### Breaking Changes

#### Removed Components

1. **CLI Commands:**
   - `bpsai-pair flow list` → Use `bpsai-pair skill list`
   - `bpsai-pair flow show` → Use `bpsai-pair skill show` (or read SKILL.md)
   - `bpsai-pair flow run` → Model invokes skills automatically
   - `bpsai-pair flow validate` → Use `bpsai-pair skill validate`

2. **Configuration:**
   - `workflow.flows_dir` config option removed
   - `capabilities.yaml` `flow_triggers` section removed

3. **File Locations:**
   - `.paircoder/flows/` → `.claude/skills/`
   - `*.flow.md` → `*/SKILL.md`

#### Behavioral Changes

1. **Invocation**: Flows were explicitly run; skills are model-invoked
2. **Roles**: Flow roles (navigator/driver) don't map to skills
3. **Triggers**: Explicit trigger lists → natural language in description

### Deprecation Timeline

```
v2.9.x  (Current)
├── Skills fully functional
├── Flows still work without warnings
└── Migration tooling available

v2.10.x (Next Minor)
├── Deprecation warnings on all flow commands
├── `flow list` suggests migration
├── `flow run` warns before executing
└── Config warning for `flows_dir`

v2.11.x (Breaking)
├── Flow commands removed entirely
├── `flows_dir` config ignored with warning
├── `flow_triggers` in capabilities.yaml ignored
└── Only skills supported
```

### Conversion Utility

```bash
# Convert single flow
bpsai-pair migrate flow-to-skill <flow-name>

# Convert all flows in project
bpsai-pair migrate flows --all

# Preview conversion without writing
bpsai-pair migrate flow-to-skill <flow-name> --dry-run

# Show migration status
bpsai-pair migrate status
```

**Utility Behavior:**

1. Parse existing `.flow.md` file
2. Extract frontmatter and body
3. Transform to SKILL.md format:
   - Convert description to third-person
   - Incorporate `when_to_use` into description
   - Remove roles section
   - Restructure body with Trigger section
4. Validate against skill spec
5. Write to `.claude/skills/<name>/SKILL.md`
6. Optionally delete source flow file

### Impact Analysis

**PairCoder's Own Flows:**

| Flow | Location | Conversion Complexity |
|------|----------|----------------------|
| implementing-with-tdd | `.paircoder/flows/` | Low - already skill-like |
| designing-and-implementing | `.paircoder/flows/` | Medium - has roles |
| reviewing-code | `.paircoder/flows/` | Low - simple structure |
| finishing-branches | `.paircoder/flows/` | Low - simple structure |

**Existing Skills (already migrated):**

| Skill | Location | Status |
|-------|----------|--------|
| implementing-with-tdd | `.claude/skills/` | Active |
| designing-and-implementing | `.claude/skills/` | Active |
| reviewing-code | `.claude/skills/` | Active |
| finishing-branches | `.claude/skills/` | Active |
| creating-skills | `.claude/skills/` | Active |
| planning-with-trello | `.claude/skills/` | Active |
| managing-task-lifecycle | `.claude/skills/` | Active |
| testing-fixes | `.claude/skills/` | Active |

**Configuration Impact:**
- `capabilities.yaml`: Remove `flow_triggers` section (~15 lines)
- `config.yaml`: Remove `flows_dir` option (~1 line)

## Drawbacks

1. **Breaking Change**: Existing projects with flows must migrate
2. **Loss of Roles**: Flow roles concept doesn't map to skills
3. **Trigger Precision**: Explicit triggers → fuzzy matching
4. **Learning Curve**: Users must understand new format

## Alternatives Considered

### 1. Keep Both Systems

**Pros:** No migration needed, backward compatible
**Cons:** Perpetual maintenance burden, user confusion

**Decision:** Rejected - long-term cost exceeds short-term migration pain

### 2. Auto-Convert at Runtime

**Pros:** Seamless transition for users
**Cons:** Performance overhead, hidden complexity, debugging difficulty

**Decision:** Rejected - explicit migration is clearer

### 3. Hybrid Format

**Pros:** One format supporting both use cases
**Cons:** Spec divergence from industry standard

**Decision:** Rejected - interoperability more important

## Adoption Strategy

### Phase 1: Preparation (v2.9.x)

1. Document migration in MIGRATION.md
2. Implement `migrate` command
3. Add migration guide to docs
4. Convert PairCoder's own flows to skills

### Phase 2: Deprecation (v2.10.x)

1. Add deprecation warnings to flow commands
2. Log warnings for `flows_dir` config
3. Update CLI help to recommend skills
4. Announce deprecation in release notes

### Phase 3: Removal (v2.11.x)

1. Remove flow commands from CLI
2. Remove flows module from codebase
3. Update cookiecutter template
4. Final migration reminder in upgrade guide

## Open Questions

1. **Compatibility Mode?** Should we support a `--legacy-flows` flag for extended transition?
   - Recommendation: No - clean break is simpler

2. **Role Preservation?** Should we create role-specific skills from role-based flows?
   - Recommendation: No - let users manually split if needed

3. **Trigger Mapping?** Should we maintain a `flow_triggers` → skill mapping during transition?
   - Recommendation: Yes - for v2.10.x deprecation period only

## References

- [Agent Skills Specification](https://agentskills.io)
- [Claude Code Skills Documentation](https://docs.anthropic.com/claude-code/skills)
- [PairCoder Skills Documentation](docs/CROSS_PLATFORM_SKILLS.md)
- [T25.25: Flow Commands Deprecation Warnings](.paircoder/tasks/T25.25.task.md)
