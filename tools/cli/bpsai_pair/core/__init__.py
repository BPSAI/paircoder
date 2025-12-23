"""Core infrastructure modules for bpsai-pair CLI.

This module consolidates shared utilities that were previously scattered
at the package root level:
- config: Configuration loading and management
- constants: Application constants
- hooks: Hook system for task lifecycle events
- ops: Git and file operations
- presets: Preset system for common configurations
- utils: General utilities (merged from utils, pyutils, jsonio)
"""

from . import config
from . import constants
from . import hooks
from . import ops
from . import presets
from . import utils

__all__ = [
    "config",
    "constants",
    "hooks",
    "ops",
    "presets",
    "utils",
]
