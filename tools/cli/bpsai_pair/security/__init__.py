"""Security module for PairCoder.

This module provides security controls for autonomous execution:
- Command allowlist management
- Pre-execution security review
- Secret detection
- Dependency vulnerability scanning
- Docker sandbox isolation
"""

from .allowlist import (
    AllowlistManager,
    CommandDecision,
    CheckResult,
)
from .review import (
    ReviewResult,
    SecurityReviewHook,
    CodeChangeReviewer,
)
from .sandbox import (
    SandboxConfig,
    SandboxRunner,
    SandboxResult,
    FileChange,
    MountConfig,
)

__all__ = [
    "AllowlistManager",
    "CommandDecision",
    "CheckResult",
    "ReviewResult",
    "SecurityReviewHook",
    "CodeChangeReviewer",
    "SandboxConfig",
    "SandboxRunner",
    "SandboxResult",
    "FileChange",
    "MountConfig",
]
