# TASK-036: Fix Cookiecutter Template Path

## Metadata
- **ID**: TASK-036
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-8
- **Priority**: P1
- **Complexity**: 35
- **Status**: done
- **Created**: 2025-12-15
- **Tags**: template, refactor, bugfix
- **changelog_entry**: Fixed nested cookiecutter template path and updated for v2.2 structure

## Description

There is a nested duplicate cookiecutter template at an incorrect path:
```
tools/cli/tools/cli/bpsai_pair/data/cookiecutter-paircoder/
```

This should be:
```
tools/cli/bpsai_pair/data/cookiecutter-paircoder/
```

Additionally, ensure the template produces the correct v2.2 structure.

## Current State (Problem)

```
tools/cli/
├── bpsai_pair/
│   └── data/
│       └── cookiecutter-paircoder/     # Correct location (may exist)
└── tools/
    └── cli/
        └── bpsai_pair/
            └── data/
                └── cookiecutter-paircoder/  # WRONG - nested duplicate
```

## Target State (Solution)

```
tools/cli/
├── bpsai_pair/
│   ├── data/
│   │   └── cookiecutter-paircoder/
│   │       ├── cookiecutter.json
│   │       └── {{cookiecutter.project_slug}}/
│   │           ├── .paircoder/
│   │           ├── .claude/
│   │           ├── AGENTS.md
│   │           ├── CLAUDE.md
│   │           └── ...
│   └── init_bundled_cli.py            # Uses correct path
└── (NO tools/cli/ subdirectory)
```

## Implementation Steps

### 1. Identify Current State

```bash
# Check for nested duplicate
ls -la tools/cli/tools/cli/bpsai_pair/data/cookiecutter-paircoder/ 2>/dev/null

# Check correct location
ls -la tools/cli/bpsai_pair/data/cookiecutter-paircoder/ 2>/dev/null

# Find all cookiecutter-paircoder directories
find . -name "cookiecutter-paircoder" -type d
```

### 2. Compare Contents

```bash
# If both exist, compare to see which is more complete
diff -rq tools/cli/bpsai_pair/data/cookiecutter-paircoder/ \
         tools/cli/tools/cli/bpsai_pair/data/cookiecutter-paircoder/ 2>/dev/null
```

### 3. Consolidate to Correct Location

**If nested has newer content:**
```bash
# Backup correct location
mv tools/cli/bpsai_pair/data/cookiecutter-paircoder/ \
   tools/cli/bpsai_pair/data/cookiecutter-paircoder.bak/

# Move nested to correct location
mv tools/cli/tools/cli/bpsai_pair/data/cookiecutter-paircoder/ \
   tools/cli/bpsai_pair/data/cookiecutter-paircoder/

# Remove empty nested directories
rm -rf tools/cli/tools/
```

**If correct location has newer content:**
```bash
# Just remove nested duplicate
rm -rf tools/cli/tools/
```

### 4. Verify Template Structure

The template should produce v2.2 structure:

```bash
# Check template contains required directories
ls tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/

# Expected:
# .paircoder/
# .claude/
# AGENTS.md
# CLAUDE.md
# (other standard files)
```

### 5. Verify Template Contents

```bash
# Check .paircoder structure
ls -R tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/

# Check .claude structure  
ls -R tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.claude/

# Check flows exist
ls tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/flows/
```

### 6. Test Template Generation

```bash
# Create temp directory
cd /tmp
mkdir test-template && cd test-template

# Test init
bpsai-pair init

# Or test cookiecutter directly
cookiecutter /path/to/tools/cli/bpsai_pair/data/cookiecutter-paircoder/

# Verify structure
ls -la
ls -la .paircoder/
ls -la .claude/
```

### 7. Update init_bundled_cli.py (if needed)

Check that the CLI finds the template at the correct path:

```python
# In tools/cli/bpsai_pair/init_bundled_cli.py
# Should use:
template_dir = Path(__file__).parent / "data" / "cookiecutter-paircoder"
```

### 8. Remove prompts/ from Template (if present)

The template should NOT include `prompts/` directory since it's deprecated:

```bash
# Check if template has prompts/
ls tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/prompts/ 2>/dev/null

# If exists, remove it
rm -rf tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/prompts/
```

## Template v2.2 Checklist

The template should include:

- [ ] `.paircoder/config.yaml`
- [ ] `.paircoder/capabilities.yaml`
- [ ] `.paircoder/context/project.md`
- [ ] `.paircoder/context/workflow.md`
- [ ] `.paircoder/context/state.md`
- [ ] `.paircoder/flows/design-plan-implement.flow.md`
- [ ] `.paircoder/flows/tdd-implement.flow.md`
- [ ] `.paircoder/flows/review.flow.md`
- [ ] `.paircoder/flows/finish-branch.flow.md`
- [ ] `.claude/skills/` (4 skills)
- [ ] `.claude/agents/` (2 agents)
- [ ] `.claude/settings.json`
- [ ] `AGENTS.md`
- [ ] `CLAUDE.md`
- [ ] `.gitignore`
- [ ] `.agentpackignore`

The template should NOT include:
- [ ] `prompts/` directory (deprecated)
- [ ] Old `context/` directory at root (v1 structure)

## Acceptance Criteria

- [ ] No nested `tools/cli/tools/cli/` path exists
- [ ] Template at correct path: `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`
- [ ] `bpsai-pair init` produces correct v2.2 structure
- [ ] Template includes all v2.2 files
- [ ] Template does NOT include deprecated prompts/
- [ ] Smoke test passes on fresh directory

## Dependencies

- None (can run independently)

## Files to Modify

**Delete:**
- `tools/cli/tools/` (entire nested duplicate)

**Verify/Update:**
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` (correct location)
- `tools/cli/bpsai_pair/init_bundled_cli.py` (if path reference wrong)

## Notes

- This is likely a git artifact from a botched merge or copy
- The nested path may have been created by running commands from wrong directory
- Test thoroughly after fix - template is user-facing
