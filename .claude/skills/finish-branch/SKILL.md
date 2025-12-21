---
name: finish-branch
description: Complete and finalize work on a branch for merge. Use when user wants to finish, ship, merge, complete, or wrap up current work. Triggers on words like finish, merge, complete, ship, wrap up, done, ready.
---

# Finish Branch

## Pre-Merge Checklist

### 1. Tests & Linting

```bash
pytest                    # All tests pass
ruff check .              # No lint errors
ruff format --check .     # Formatting OK
```

### 2. Review Changes

```bash
git diff main...HEAD --stat
git diff main...HEAD | grep -E "print\(|breakpoint|TODO|FIXME"
```

### 3. Clean Up
- Remove debug statements
- Remove commented-out code
- Remove unused imports

### 4. Update Task Status

Follow paircoder-task-lifecycle skill:
1. `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
2. `bpsai-pair task update TASK-XXX --status done`

### 5. Commit & Push

```bash
git add -A
git commit -m "[TASK-XXX] Description"
git push origin <branch>
```

## PR Template

```markdown
## Summary
Brief description.

## Changes
- Added X
- Modified Y
- Fixed Z

## Testing
- [ ] Unit tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] No debug statements
- [ ] Documentation updated
- [ ] Task status updated
```

## Post-Merge

```bash
git checkout main
git pull origin main
git branch -d <feature-branch>
```

## Quick Finish

```bash
pytest && ruff check . && git add -A && git commit -m "[TASK-XXX] Description" && git push
```
