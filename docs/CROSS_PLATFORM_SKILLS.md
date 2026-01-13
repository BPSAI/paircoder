# Cross-Platform Skills

This guide explains how to create skills that work across different AI coding tools and how to export skills from Claude Code to other platforms.

## Platform Compatibility Matrix

| Platform | Skill Discovery | Script Execution | Export Format |
|----------|----------------|------------------|---------------|
| Claude Code | Native | Native | N/A (native) |
| Cursor | Rules file | Manual | `.cursor/rules/*.md` |
| Continue.dev | Context file | Manual | `.continue/context/*.md` |
| Windsurf | Rules file | Manual | `.windsurfrules` |
| GitHub Copilot | N/A | N/A | Not supported |

## Creating Portable Skills

### What Makes a Skill Portable?

A portable skill is one that works across multiple AI coding tools. To maximize portability:

1. **Use only SKILL.md** - Avoid scripts in `scripts/` directory
2. **Avoid platform-specific commands** - Don't reference `bpsai-pair` commands
3. **Avoid Claude Code features** - Don't reference `/compact`, `/context`, etc.
4. **Use generic instructions** - Focus on what to do, not tool-specific how

### Portable Skill Structure

```
.claude/skills/my-skill/
├── SKILL.md          # Main skill document (portable)
└── reference/        # Optional supporting docs (portable)
```

Avoid:
```
.claude/skills/my-skill/
├── SKILL.md
├── reference/
└── scripts/          # NOT portable - won't work on other platforms
    └── run.py
```

### Writing Portable Content

**Good (Portable):**
```markdown
# Code Review

## Guidelines
- Check for security issues
- Verify error handling
- Ensure tests are updated
```

**Less Portable:**
```markdown
# Code Review

## Guidelines
Run `bpsai-pair skill run reviewing-code` to start.
Use `/compact` when context is full.
```

## Exporting Skills

### Export to Cursor

```bash
# Export single skill
bpsai-pair skill export my-skill --format cursor

# Export all skills
bpsai-pair skill export --all --format cursor
```

Creates: `.cursor/rules/my-skill.md`

Cursor reads markdown files from `.cursor/rules/` as project rules.

### Export to Continue.dev

```bash
# Export single skill
bpsai-pair skill export my-skill --format continue

# Export all skills
bpsai-pair skill export --all --format continue
```

Creates: `.continue/context/my-skill.md`

Continue.dev uses context files to provide additional instructions.

### Export to Windsurf

```bash
# Export single skill
bpsai-pair skill export my-skill --format windsurf

# Export all skills
bpsai-pair skill export --all --format windsurf
```

Appends to: `.windsurfrules`

Windsurf uses a single rules file with section markers.

### Dry Run Mode

Preview what would be created without actually creating files:

```bash
bpsai-pair skill export my-skill --format cursor --dry-run
```

## Portability Warnings

When exporting, you'll see warnings for skills that may not work on other platforms:

```
⚠ Skill has scripts/ directory - scripts won't work on other platforms
⚠ Skill references bpsai-pair commands - may not work on other platforms
⚠ Skill references Claude Code features - may not work on other platforms
```

## Export Format Details

### Cursor Format

- Strips YAML frontmatter
- Adds metadata comment with export info
- Creates individual `.md` file per skill

Example output:
```markdown
<!-- Exported from bpsai-pair skill: reviewing-code -->
<!-- Export date: 2025-12-23 -->

# Code Review

Instructions here...
```

### Continue.dev Format

- Strips YAML frontmatter
- Adds context header
- Creates individual `.md` file per skill

Example output:
```markdown
# Context: reviewing-code

<!-- Exported from bpsai-pair -->

# Code Review

Instructions here...
```

### Windsurf Format

- Strips YAML frontmatter
- Uses section markers for organization
- Appends to single `.windsurfrules` file
- Updates existing sections if skill was previously exported

Example output:
```markdown
## --- BEGIN SKILL: reviewing-code ---

# Code Review

Instructions here...

## --- END SKILL: reviewing-code ---
```

## Best Practices

### For Maximum Portability

1. Keep instructions generic and declarative
2. Focus on "what" not "how"
3. Avoid tool-specific terminology
4. Use standard markdown formatting
5. Don't rely on scripts for functionality

### Platform-Specific Features

If you need platform-specific features, consider creating separate skills:

```
.claude/skills/
├── reviewing-code/           # Core portable skill
│   └── SKILL.md
├── reviewing-code-claude/    # Claude Code specific
│   ├── SKILL.md
│   └── scripts/
│       └── run-review.py
```

## CLI Command Reference

```bash
# Export single skill
bpsai-pair skill export <name> --format <format>

# Export all skills
bpsai-pair skill export --all --format <format>

# Dry run (preview only)
bpsai-pair skill export <name> --format <format> --dry-run

# Supported formats
--format cursor      # Cursor AI
--format continue    # Continue.dev
--format windsurf    # Windsurf
```

## Future Work

- **Import detection**: Detect skills in other formats and offer to import
- **Registry support**: Install skills from `@org/skill-name` references
- **Sync mode**: Keep exported skills in sync with source
