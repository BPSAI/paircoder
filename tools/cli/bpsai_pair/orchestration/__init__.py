"""
Orchestration module for multi-agent coordination.

This module provides:
- HeadlessSession: Programmatic Claude Code invocation
- HandoffManager: Context packaging for agent transfers
- CodexAdapter: Codex CLI integration
- Orchestrator: Task routing and agent coordination
"""

from .headless import HeadlessSession, HeadlessResponse
from .handoff import HandoffManager, HandoffPackage
from .codex import CodexAdapter
from .orchestrator import Orchestrator

__all__ = [
    "HeadlessSession",
    "HeadlessResponse",
    "HandoffManager",
    "HandoffPackage",
    "CodexAdapter",
    "Orchestrator",
]
