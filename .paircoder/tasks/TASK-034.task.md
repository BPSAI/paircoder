# TASK-034: Consolidate Documentation to Root

## Metadata
- **ID**: TASK-034
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-8
- **Priority**: P0
- **Complexity**: 35
- **Status**: done
- **Created**: 2025-12-15
- **Tags**: docs, refactor, cleanup
- **changelog_entry**: Consolidated documentation to repository root

## Description

Merge and consolidate duplicate documentation files. Currently there are conflicting/duplicate files between repository root and tools/cli/ directory, causing confusion for both users and AI agents.

**Key Insight:** USER_GUIDE.md is documentation *about PairCoder* (the tool), NOT documentation that goes into user projects via cookiecutter. The cookiecutter template generates project-specific context files, not PairCoder documentation.

## Current State (Problem)

| File | Root | tools/cli/ | Issue |
|------|------|------------|-------|
| CHANGELOG.md | v0.2.5 (Aug 2025) | v2.0.0 (Dec 2025) | Root is stale |
| README.md | Outdated v1 style | Current v2 commands | Root is stale |
| USER_GUIDE.md | ❌ Missing | ✅ Complete | Should be in docs/ |
| paircoder-docs.md | ✅ Exists | ❌ N/A | May be redundant |

## Target State (Solution)

| File | Location | Purpose |
|------|----------|---------|
| CHANGELOG.md | Root | PairCoder version history (v0.1.0→v2.2.0) |
| README.md | Root | Quick start, overview of PairCoder |
| docs/USER_GUIDE.md | docs/ | Full PairCoder documentation |
| tools/cli/README.md | tools/cli/ | Minimal dev-only pointer |

**Deleted:**
- tools/cli/CHANGELOG.md (merged to root)
- tools/cli/USER_GUIDE.md (moved to docs/)
- paircoder-docs.md (merged into USER_GUIDE)

**NOT in cookiecutter template:**
- USER_GUIDE.md - this is about PairCoder, not user projects
- CHANGELOG.md - this is PairCoder history, not user projects

## Implementation Steps

### 1. CHANGELOG.md Consolidation

```bash
# Root has old history (v0.1.0 → v0.2.5)
# tools/cli/ has new history (v0.2.5 → v2.0.0)
# Need to merge chronologically

# Strategy:
# 1. Start with tools/cli/CHANGELOG.md (newest)
# 2. Append root CHANGELOG.md entries that aren't duplicated
# 3. Save to root
# 4. Delete tools/cli/CHANGELOG.md
```

**Merge Result Structure:**
```markdown
# Changelog

## [2.0.0] - 2025-12-15
... (from tools/cli/)

## [0.2.5] - 2025-09-01
... (from root)

## [0.2.4] - 2025-09-01
... (from root)
... continue with older versions
```

### 2. README.md Consolidation

```bash
# Root README is outdated (v1 style, /context/ paths)
# tools/cli/README.md has current v2 commands

# Strategy:
# 1. Use tools/cli/README.md as base
# 2. Add project overview from root README
# 3. Ensure both package install AND development paths documented
# 4. Save to root
# 5. Reduce tools/cli/README.md to minimal pointer
```

**Root README should include:**
- Project overview and purpose
- Quick install: `pip install bpsai-pair`
- Development install: `pip install -e tools/cli`
- v2 command reference
- Project structure explanation
- Link to docs/USER_GUIDE.md for full docs

**tools/cli/README.md becomes:**
```markdown
# bpsai-pair CLI Package

See [main README](../../README.md) for documentation.

## Development

\`\`\`bash
pip install -e .
pytest
\`\`\`
```

### 3. USER_GUIDE.md Move

```bash
# Create docs/ directory if needed, move USER_GUIDE to docs/
mkdir -p docs
mv tools/cli/USER_GUIDE.md ./docs/USER_GUIDE.md

# Update any internal links that reference relative paths
```

### 4. paircoder-docs.md Evaluation

Compare paircoder-docs.md (root) with USER_GUIDE.md (tools/cli/):
- If substantially similar: delete paircoder-docs.md
- If unique content: merge into USER_GUIDE.md then delete

Based on review: paircoder-docs.md appears to be older/redundant. Delete after confirming USER_GUIDE.md has equivalent content.

## Verification Commands

```bash
# After consolidation, verify:

# 1. Root has main docs
ls -la README.md CHANGELOG.md

# 2. USER_GUIDE in docs/
ls -la docs/USER_GUIDE.md

# 3. tools/cli/ has minimal README only
ls -la tools/cli/README.md
cat tools/cli/README.md  # Should be short pointer

# 4. No duplicate CHANGELOGs
test ! -f tools/cli/CHANGELOG.md && echo "OK: No duplicate CHANGELOG"

# 5. paircoder-docs.md removed
test ! -f paircoder-docs.md && echo "OK: Old docs removed"
```

## Acceptance Criteria

- [ ] Single CHANGELOG.md at root with v0.1.0 through v2.1.0 history
- [ ] Root README.md has v2 commands and structure
- [ ] USER_GUIDE.md at docs/USER_GUIDE.md
- [ ] tools/cli/README.md is minimal (dev-only)
- [ ] tools/cli/CHANGELOG.md deleted
- [ ] tools/cli/USER_GUIDE.md deleted (moved to docs/)
- [ ] paircoder-docs.md deleted (redundant)
- [ ] All internal links updated
- [ ] No broken references in codebase

## Dependencies

- TASK-033 (archive first so changelog has v2.1.0 entry)

## Files to Modify

**Create/Update:**
- `CHANGELOG.md` (merge both versions)
- `README.md` (merge both versions)
- `docs/USER_GUIDE.md` (move from tools/cli/)
- `tools/cli/README.md` (minimize)

**Delete:**
- `tools/cli/CHANGELOG.md`
- `tools/cli/USER_GUIDE.md`
- `paircoder-docs.md`

## Git Strategy

```bash
# Create docs/ and use git mv to preserve history where possible
mkdir -p docs
git mv tools/cli/USER_GUIDE.md docs/USER_GUIDE.md

# For merges, commit with clear message
git commit -m "docs: consolidate CHANGELOG.md to root

Merged tools/cli/CHANGELOG.md (v0.2.5-v2.0.0) with root CHANGELOG.md (v0.1.0-v0.2.5).
Single source of truth now at repository root."
```

## Notes

- Preserving git history is nice but not critical for docs
- Focus on correct final state over perfect git history
- Update AGENTS.md if it references old paths
- Update .paircoder/context/project.md if it references old paths
- Cookiecutter template does NOT include USER_GUIDE.md (it's about PairCoder, not user projects)
