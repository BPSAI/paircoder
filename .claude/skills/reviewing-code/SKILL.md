---
name: reviewing-code
description: Provides systematic code review workflow for identifying issues, verifying quality, and ensuring best practices. Analyzes changes for correctness, security, and maintainability. Activated by review requests, PR checks, or code evaluation needs.
---

# Code Review

## Quick Commands

```bash
# Run ALL checks at once (tests + linting)
bpsai-pair ci

# Validate project structure
bpsai-pair validate

# See what changed
git diff main...HEAD --stat
git diff main...HEAD
```

## Review Output Format

```markdown
## Code Review: [Description]

### Summary
Brief assessment.

### Must Fix
1. **[File:Line]** - Issue and fix

### Should Fix
1. **[File:Line]** - Suggestion

### Consider
1. **[File:Line]** - Optional improvement

### Positive Notes
- What was done well

### Verdict
- [ ] Approve
- [ ] Approve with comments
- [ ] Request changes
```

## Project-Specific Checks

- Type hints on public functions
- Docstrings on public interfaces
- No hardcoded values (use config)
- Tests for new functionality
- Mock external services (Trello, GitHub APIs)
- Follow existing patterns in codebase

## Quick Checks

```bash
# Find debug statements
git diff main...HEAD | grep -E "print\(|breakpoint|pdb"

# Find TODOs in changes
git diff main...HEAD --name-only | xargs grep -n "TODO\|FIXME"

# Check for secrets
git diff main...HEAD | grep -iE "password|secret|api.?key|token"
```
