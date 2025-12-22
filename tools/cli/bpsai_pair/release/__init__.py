"""Release engineering module for PairCoder.

This module provides CLI commands for release management:
- release plan: Create release plan
- release checklist: Show release checklist
- release prep: Run release preparation checks

Template commands will be added in T23.5:
- template check: Check cookiecutter template drift
- template list: List template files
- template fix: Auto-sync template from source

Part of EPIC-003 Phase 2: CLI Architecture Refactor.
"""

from .commands import app as release_app

__all__ = ["release_app"]
