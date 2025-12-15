# PairCoder Development Workflow

## Branch Strategy

| Branch Type | Naming | Purpose |
|-------------|--------|---------|
| `main` | — | Stable, release-ready code |
| `feature/*` | `feature/short-description` | New features |
| `fix/*` | `fix/issue-or-description` | Bug fixes |
| `refactor/*` | `refactor/what` | Code improvements |
| `docs/*` | `docs/what` | Documentation only |

## Development Cycle

### 1. Starting Work

```bash
# Create feature branch
git checkout -b feature/my-feature main

# Or use PairCoder CLI
bpsai-pair feature my-feature --type feature
```

### 2. Planning (for substantial work)

For features or refactors that take more than ~30 minutes:

1. **Create a plan** in `.paircoder/plans/`
2. **Break into tasks** (2-20 minutes each)
3. **Follow the flow**: `design-plan-implement`

```bash
bpsai-pair plan new my-feature --type feature --flow design-plan-implement
```

### 3. Implementation

Follow TDD where practical:

1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat

Use the `tdd-implement` flow for guidance.

### 4. Verification

Before marking work complete:

```bash
# Run tests
cd tools/cli && pytest

# Check types (if configured)
mypy bpsai_pair/

# Lint
ruff check bpsai_pair/
```

### 5. Review

Self-review or request review:

```bash
bpsai-pair flow run review
```

### 6. Completion

```bash
# Update state
bpsai-pair context-sync --last "Completed X" --next "Ready to merge"

# Or run finish flow
bpsai-pair flow run finish-branch
```

## Commit Messages

Format: `<type>(<scope>): <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change that neither fixes nor adds
- `docs`: Documentation only
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(planning): add plan parser
fix(cli): handle missing config gracefully
docs(adr): update v2 architecture
refactor(flows): extract common validation
```

## Code Style

- **Python**: Follow PEP 8, use type hints
- **YAML**: 2-space indent, quoted strings for ambiguous values
- **Markdown**: ATX headers (`#`), fenced code blocks

## Testing Requirements

| Change Type | Test Requirement |
|-------------|------------------|
| New feature | Unit tests required |
| Bug fix | Regression test required |
| Refactor | Existing tests must pass |
| Config/docs | No tests required |

## Context Updates

Keep `.paircoder/context/state.md` updated:

- When starting a new task
- When completing a task
- When encountering blockers
- At end of session

## Working with AI Agents

When using Claude Code, Codex CLI, or similar:

1. Point them to `.paircoder/capabilities.yaml`
2. Let them read `context/project.md` and `context/state.md`
3. They should suggest appropriate flows based on your request
4. Update state after they complete work

## Definition of Done

A task is complete when:

- [ ] Code compiles/runs without errors
- [ ] Tests pass (if applicable)
- [ ] State updated in `state.md`
- [ ] Committed with proper message
