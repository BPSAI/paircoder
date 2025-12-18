"""
Orchestration module for multi-agent coordination.

This module provides:
- HeadlessSession: Programmatic Claude Code invocation
- HandoffManager: Context packaging for agent transfers
- CodexAdapter: Codex CLI integration
- Orchestrator: Task routing and agent coordination
- AgentInvoker: Invoke specialized agents from .claude/agents/
"""

from .headless import HeadlessSession, HeadlessResponse
from .handoff import HandoffManager, HandoffPackage
from .codex import CodexAdapter
from .orchestrator import Orchestrator
from .invoker import AgentDefinition, AgentInvoker, InvocationResult, invoke_agent

__all__ = [
    "HeadlessSession",
    "HeadlessResponse",
    "HandoffManager",
    "HandoffPackage",
    "CodexAdapter",
    "Orchestrator",
    "AgentDefinition",
    "AgentInvoker",
    "InvocationResult",
    "invoke_agent",
]
