"""
Orchestration module for multi-agent coordination.

This module provides:
- HeadlessSession: Programmatic Claude Code invocation
- HandoffManager: Context packaging for agent transfers
- CodexAdapter: Codex CLI integration
- Orchestrator: Task routing and agent coordination
- AgentInvoker: Invoke specialized agents from .claude/agents/
- PlannerAgent: Design and planning specialist agent
"""

from .headless import HeadlessSession, HeadlessResponse
from .handoff import HandoffManager, HandoffPackage
from .codex import CodexAdapter
from .orchestrator import Orchestrator
from .invoker import AgentDefinition, AgentInvoker, InvocationResult, invoke_agent
from .planner import PlannerAgent, PlanOutput, PlanPhase, invoke_planner, should_trigger_planner

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
    "PlannerAgent",
    "PlanOutput",
    "PlanPhase",
    "invoke_planner",
    "should_trigger_planner",
]
