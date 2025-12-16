# TASK-035: Remove Obsolete prompts/ Directory

## Metadata
- **ID**: TASK-035
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-8
- **Priority**: P1
- **Complexity**: 15
- **Status**: done
- **Created**: 2025-12-15
- **Tags**: refactor, cleanup, deprecation
- **changelog_entry**: Removed obsolete prompts/ directory (replaced by flows/skills)

## Description

The `prompts/` directory at repository root contains YAML prompt templates that are now obsolete. These have been replaced by:

- `.paircoder/flows/` - Cross-agent workflow definitions (.flow.md)
- `.claude/skills/` - Claude Code native skills (SKILL.md)

The prompts/ directory should be removed to reduce confusion.

## Current Contents

```
prompts/
├── .gitkeep
├── deep_research.yml
├── implementation.yml
└── roadmap.yml
```

**Content Analysis:**

| File | Purpose | Replacement |
|------|---------|-------------|
| roadmap.yml | Generate roadmap from plan | `.paircoder/flows/design-plan-implement.flow.md` |
| deep_research.yml | Deep dive analysis | N/A - ad-hoc prompting |
| implementation.yml | Implementation guidance | `.paircoder/flows/tdd-implement.flow.md` |

## Pre-Removal Checklist

Before deleting, verify:

1. **No code references:**
   ```bash
   grep -r "prompts/" --include="*.py" --include="*.md" --include="*.yaml" .
   ```

2. **No imports:**
   ```bash
   grep -r "roadmap.yml\|implementation.yml\|deep_research.yml" .
   ```

3. **Documentation updated:**
   - README.md doesn't reference prompts/
   - USER_GUIDE.md doesn't reference prompts/
   - paircoder-docs.md doesn't reference prompts/ (or is deleted per TASK-034)

## Implementation Steps

### 1. Search for References

```bash
# Check for any references to prompts directory
grep -r "prompts/" . --include="*.py" --include="*.md" --include="*.yaml" --include="*.yml" | grep -v ".git"

# Check for specific file references
grep -r "roadmap.yml" . --include="*.py" --include="*.md" | grep -v ".git"
grep -r "implementation.yml" . --include="*.py" --include="*.md" | grep -v ".git"
grep -r "deep_research.yml" . --include="*.py" --include="*.md" | grep -v ".git"
```

### 2. Update Documentation

If any docs reference prompts/:
- Update to reference .paircoder/flows/ instead
- Or remove the reference entirely

**Known references to update:**
- `paircoder-docs.md` (if not already deleted by TASK-034)
- Root `README.md` (if still mentions prompts/)

### 3. Remove Directory

```bash
# Remove the entire prompts directory
rm -rf prompts/

# Verify removal
ls -la prompts/ 2>/dev/null || echo "Successfully removed"
```

### 4. Commit

```bash
git add -A
git commit -m "refactor: remove obsolete prompts/ directory

The prompts/ directory contained YAML prompt templates that have been
superseded by:
- .paircoder/flows/*.flow.md - Cross-agent workflow definitions
- .claude/skills/*/SKILL.md - Claude Code native skills

These new formats provide richer structure (YAML frontmatter + Markdown body)
and integrate with the v2 capability manifest system."
```

## Migration Notes for Users

If users were using the prompts/ files, they should:

1. **roadmap.yml** → Use `bpsai-pair flow run design-plan-implement`
2. **implementation.yml** → Use `bpsai-pair flow run tdd-implement`
3. **deep_research.yml** → Create custom flow or use ad-hoc prompting

The new flow system provides:
- Structured steps with gates
- Role assignments (Navigator/Driver/Reviewer)
- Trigger patterns for automatic suggestions
- Integration with capability manifest

## Acceptance Criteria

- [ ] No code references prompts/ directory
- [ ] prompts/ directory deleted
- [ ] No broken references in documentation
- [ ] Commit message documents the migration path

## Dependencies

- None (can run in parallel with other Sprint 8 tasks)
- Recommend after TASK-034 (docs consolidation) to avoid conflicts

## Files to Modify

**Delete:**
- `prompts/` (entire directory)

**Update (if needed):**
- `README.md` (remove prompts/ references)
- Any other docs that reference prompts/

## Notes

- This is a breaking change for anyone using the YAML prompts directly
- The functionality is preserved via flows, just in a different format
- Keep this task simple - just remove and document
