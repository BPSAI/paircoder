# Directory Note — tools/cli

**Purpose:** Contains the bpsai-pair package source code that gets published to PyPI

**Entry Points:** 
- `bpsai_pair/cli.py` - Main CLI application (Typer-based)
- `bpsai_pair/__main__.py` - Package entry point

**Key Components:**
- `bpsai_pair/` - Python package source
  - `cli.py` - CLI commands (init, feature, pack, context-sync)
  - `data/cookiecutter-paircoder/` - Template bundled with package
- `pyproject.toml` - Package metadata and dependencies
- `tests/` - Package unit tests
- `dist/`, `build/` - Build artifacts (git-ignored)

## Do / Don't

**Do:**
- Test all changes with `pytest` before committing
- Maintain backward compatibility for CLI commands
- Keep pure Python (no shell dependencies)
- Update version in pyproject.toml for releases

**Don't:**
- Mix development-specific files into the cookiecutter template
- Hard-code paths or repo-specific values
- Break existing CLI interfaces
- Commit dist/ or build/ directories

## Testing
```bash
cd tools/cli
pytest                    # Run tests
pip install -e .         # Install editable for testing
python -m build          # Build wheel
```

## Glossary
- **Cookiecutter template** - The scaffolding that users receive via `bpsai-pair init`
- **Entry point** - Console script defined in pyproject.toml that creates `bpsai-pair` command
- **Wheel** - Built package file (.whl) for distribution
