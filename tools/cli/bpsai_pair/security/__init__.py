"""Security module for PairCoder.

This module provides security controls for autonomous execution:
- Command allowlist management
- Pre-execution security review
- Secret detection
- Dependency vulnerability scanning
"""

from .allowlist import (
    AllowlistManager,
    CommandDecision,
    CheckResult,
)

__all__ = [
    "AllowlistManager",
    "CommandDecision",
    "CheckResult",
]
