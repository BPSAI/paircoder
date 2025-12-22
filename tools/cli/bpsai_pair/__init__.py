"""bpsai_pair package"""
from importlib.metadata import version

__version__ = version("bpsai-pair")

# Core modules
from . import cli
from . import config
from . import utils

# Feature modules (public API)
from . import planning
from . import tasks
from . import flows
from . import trello
from . import github
from . import metrics
from . import orchestration
from . import mcp
from . import context
from . import presets

__all__ = [
    "__version__",
    # Core
    "cli",
    "config",
    "utils",
    # Features
    "planning",
    "tasks",
    "flows",
    "trello",
    "github",
    "metrics",
    "orchestration",
    "mcp",
    "context",
    "presets",
]
