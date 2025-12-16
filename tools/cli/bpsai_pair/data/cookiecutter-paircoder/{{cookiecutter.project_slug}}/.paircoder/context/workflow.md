# Development Workflow

## Branch Strategy

- **Main branch:** `main` - Always deployable
- **Feature branches:** `feature/<name>` - New features
- **Fix branches:** `fix/<name>` - Bug fixes
- **Refactor branches:** `refactor/<name>` - Code improvements

## Development Process

### 1. Planning
- Create a plan with goals and tasks
- Break work into small, testable chunks
- Each task should be 2-20 minutes of work

### 2. Implementation
- One task at a time
- Write tests first (TDD)
- Keep commits focused and atomic

### 3. Review
- Run all tests before PR
- Self-review checklist
- Request peer review for significant changes

### 4. Merge
- Squash commits if needed
- Update documentation
- Close related issues

## Code Standards

### Testing
- Minimum coverage: {{ cookiecutter.coverage_target }}
- Unit tests for all business logic
- Integration tests for external dependencies

### Documentation
- Public APIs must have docstrings
- Complex logic should have comments
- Update README for user-facing changes

### Commits
- Use conventional commits: `type(scope): description`
- Types: feat, fix, refactor, test, docs, chore
- Keep commits focused and atomic

## CI/CD Gates

1. All tests pass
2. Coverage meets threshold
3. Linting passes
4. Security scan passes
5. Build succeeds

## CLI Commands

```bash
# Status
bpsai-pair status

# Planning
bpsai-pair plan new <slug> --type feature
bpsai-pair plan list
bpsai-pair plan show <id>

# Tasks
bpsai-pair task list
bpsai-pair task update <id> --status done

# Flows
bpsai-pair flow list
bpsai-pair flow run <name>

# Context
bpsai-pair context-sync --last "..." --next "..."
bpsai-pair pack
```

## Context Loop Discipline

After every significant action:
1. Update task status if applicable
2. Sync context with what was done and what's next
3. Note any blockers or risks

```bash
bpsai-pair context-sync \
    --last "What was completed" \
    --next "What's next" \
    --blockers "Any issues"
```
