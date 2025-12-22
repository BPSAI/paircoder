"""Template CLI commands for PairCoder.

Provides commands for cookiecutter template management including
drift detection, listing, and auto-sync.

Extracted from planning/cli_commands.py as part of EPIC-003 Phase 2.
"""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()

app = typer.Typer(
    help="Cookiecutter template management commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)


# Placeholder - commands will be extracted from planning/cli_commands.py in T23.5
# Expected commands:
# - template check: Check cookiecutter template drift
# - template list: List template files
# - template fix: Auto-sync template from source (via --fix flag)
