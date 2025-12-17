"""Security module for PairCoder.

This module provides security controls for autonomous execution:
- Command allowlist management
- Pre-execution security review
- Secret detection
- Dependency vulnerability scanning
- Docker sandbox isolation
- Git checkpoint/rollback
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
from .checkpoint import (
    GitCheckpoint,
    CheckpointError,
    NotAGitRepoError,
    CheckpointNotFoundError,
    NoCheckpointsError,
    format_checkpoint_list,
    format_rollback_preview,
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
    "GitCheckpoint",
    "CheckpointError",
    "NotAGitRepoError",
    "CheckpointNotFoundError",
    "NoCheckpointsError",
    "format_checkpoint_list",
    "format_rollback_preview",
]
