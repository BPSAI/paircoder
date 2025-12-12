# Repo Audit Checklist — v2 Upgrade

**Purpose:** Quick reference for AI agents and developers navigating this repository during v2 development.

## Where Things Live

| Path | What It Is | Notes |
|------|------------|-------|
| `tools/cli/bpsai_pair/` | Package source code | Published to PyPI as `bpsai-pair` |
| `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` | **Template boundary** | What users receive via `bpsai-pair init` |
| `tools/cli/tests/` | Package unit tests | pytest-based |
| `context/` | Project memory | Root repo's own context (reference implementation) |
| `docs/adr/` | Architecture Decision Records | ADR 0002 covers v2 architecture |
| `prompts/` | Prompt templates | YAML-based prompt specs |
| `.github/workflows/` | CI pipelines | Python lint/test + project_tree sync |

## Template Boundary (Critical)

The template lives at `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`.

**Inside the template** = what end users get when they run `bpsai-pair init`:
```
cookiecutter-paircoder/{{cookiecutter.project_slug}}/
├── CLAUDE.md              # Generic root pointer
├── AGENTS.md              # Generic pairing guide
├── context/               # Empty context structure
├── templates/             # ADR & directory_note templates
├── tests/                 # Example test stubs
├── prompts/               # Sample prompt templates
└── src/                   # User application code
```

**Outside the template** = development-only files in this repo:
- `tools/cli/tests/` — Package tests (not shipped)
- `tools/cli/pyproject.toml` — Build metadata (not shipped)
- Root-level `context/`, `docs/`, `prompts/` — Reference implementation

**Rule:** Changes to the template affect all future users. Changes outside the template affect only this repo.

## Commands Devs Run Locally

### Testing the CLI Package

```bash
# Run unit tests
cd tools/cli && pytest

# Run tests with verbose output
cd tools/cli && pytest -v

# Run specific test file
cd tools/cli && pytest tests/test_cli.py

# Install package in editable mode (for testing)
cd tools/cli && pip install -e .
```

### Using the CLI

```bash
# Show available commands
bpsai-pair --help

# Check version
bpsai-pair --version

# Validate repo structure
bpsai-pair validate

# Show current project status
bpsai-pair status

# Preview what gets packed for agents
bpsai-pair pack --list
```

### Building & Linting

```bash
# Build wheel for distribution
cd tools/cli && python -m build

# Lint with ruff
cd tools/cli && ruff check .

# Format check
cd tools/cli && ruff format --check .

# Type check
cd tools/cli && mypy bpsai_pair/
```

### Context Loop Updates

```bash
# Update after completing work
bpsai-pair context-sync --last "What you did" --next "What's next" --blockers "Any issues"
```

## Test Fixtures Available

In `tools/cli/tests/conftest.py`:
- `temp_repo` — Temporary git repo for testing
- `initialized_repo` — Temp repo with `bpsai-pair init` already run

## CI/CD Checks

The following must pass before merge:
1. `ruff check .` — No lint errors
2. `ruff format --check .` — Code formatted
3. `mypy bpsai_pair/` — Type checks pass
4. `pytest` — All tests pass
5. `pip-audit` — No known vulnerabilities

## v2 Architecture Reference

See `docs/adr/0002-paircoder-v2-architecture.md` for:
- New modules: `providers/`, `orchestrator/`, `flows/`
- Multi-provider support (Anthropic, OpenAI, Google)
- Budget and routing configuration
- New CLI commands (`flow`, `provider`, `budget`)

**Note:** v2 features are additive—v1 repos continue working unchanged.

## Quick Checklist for Changes

Before committing:
- [ ] Tests pass: `cd tools/cli && pytest`
- [ ] Lint passes: `cd tools/cli && ruff check .`
- [ ] If modifying template: verified changes are appropriate for end users
- [ ] If adding CLI command: added to `--help` and tested manually
- [ ] Updated context loop if making significant progress
