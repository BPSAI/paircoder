"""
MCP Orchestration Tools

Implements orchestration tools:
- paircoder_orchestrate_analyze: Analyze task and get model recommendation
- paircoder_orchestrate_handoff: Create handoff package for agent transitions
"""

from pathlib import Path
from typing import Any, Optional


def find_paircoder_dir() -> Path:
    """Find the .paircoder directory."""
    current = Path.cwd()
    while current != current.parent:
        paircoder_dir = current / ".paircoder"
        if paircoder_dir.exists():
            return paircoder_dir
        current = current.parent
    raise FileNotFoundError("No .paircoder directory found")


def get_project_root() -> Path:
    """Get the project root (parent of .paircoder)."""
    return find_paircoder_dir().parent


def register_orchestration_tools(server: Any) -> None:
    """Register orchestration tools with the MCP server."""

    @server.tool()
    async def paircoder_orchestrate_analyze(
        task_id: str,
        context: Optional[str] = None,
        prefer_agent: Optional[str] = None,
    ) -> dict:
        """
        Analyze task complexity and recommend model/agent.

        Args:
            task_id: Task ID to analyze
            context: Additional context for analysis (optional)
            prefer_agent: Preferred agent override (optional)

        Returns:
            Analysis with complexity, recommended model, and reasoning
        """
        try:
            from ...orchestration import Orchestrator

            project_root = get_project_root()
            orchestrator = Orchestrator(project_root=project_root)

            # Analyze task
            task = orchestrator.analyze_task(task_id)

            # Get routing decision
            constraints = {}
            if prefer_agent:
                constraints["prefer"] = prefer_agent

            decision = orchestrator.select_agent(task, constraints)

            # Map complexity to band
            complexity_bands = {
                "low": "trivial",
                "medium": "moderate",
                "high": "complex",
            }

            # Estimate tokens and cost
            estimated_tokens = task.estimated_tokens
            agent_caps = orchestrator.agents.get(decision.agent)
            cost_per_token = (agent_caps.cost_per_1k_tokens / 1000) if agent_caps else 0.015

            return {
                "task_id": task_id,
                "task_type": task.task_type.value,
                "complexity_score": decision.score,
                "complexity_band": complexity_bands.get(task.complexity.value, "moderate"),
                "scope": task.scope.value,
                "recommended_agent": decision.agent,
                "reasoning": decision.reasoning,
                "requires_reasoning": task.requires_reasoning,
                "requires_iteration": task.requires_iteration,
                "estimated_tokens": estimated_tokens,
                "estimated_cost": f"${estimated_tokens * cost_per_token:.2f}",
            }
        except FileNotFoundError:
            return {"error": {"code": "NOT_FOUND", "message": "No .paircoder directory found"}}
        except Exception as e:
            return {"error": {"code": "ERROR", "message": str(e)}}

    @server.tool()
    async def paircoder_orchestrate_handoff(
        task_id: str,
        from_agent: Optional[str] = None,
        to_agent: Optional[str] = None,
        progress_summary: str = "",
        files_in_progress: Optional[list] = None,
        decisions_made: Optional[list] = None,
        open_questions: Optional[list] = None,
    ) -> dict:
        """
        Create handoff package for agent transition.

        Args:
            task_id: Task ID being handed off
            from_agent: Source agent (optional)
            to_agent: Target agent (optional, defaults to 'codex')
            progress_summary: Summary of work done
            files_in_progress: List of files being worked on
            decisions_made: Key decisions made during work
            open_questions: Unresolved questions

        Returns:
            Handoff package metadata
        """
        try:
            from ...orchestration import HandoffManager

            project_root = get_project_root()
            manager = HandoffManager(project_root=project_root)

            # Prepare file paths
            include_files = None
            if files_in_progress:
                include_files = [project_root / f for f in files_in_progress]

            # Build summary with decisions and questions
            full_summary = progress_summary
            if decisions_made:
                full_summary += "\n\n**Decisions Made:**\n"
                for decision in decisions_made:
                    full_summary += f"- {decision}\n"
            if open_questions:
                full_summary += "\n\n**Open Questions:**\n"
                for question in open_questions:
                    full_summary += f"- {question}\n"

            # Create handoff package
            package_path = manager.pack(
                task_id=task_id,
                source_agent=from_agent or "claude",
                target_agent=to_agent or "codex",
                include_files=include_files,
                conversation_summary=full_summary,
            )

            return {
                "status": "created",
                "task_id": task_id,
                "from_agent": from_agent or "claude",
                "to_agent": to_agent or "codex",
                "package_path": str(package_path),
                "files_included": files_in_progress or [],
                "summary_length": len(full_summary),
            }
        except FileNotFoundError:
            return {"error": {"code": "NOT_FOUND", "message": "No .paircoder directory found"}}
        except Exception as e:
            return {"error": {"code": "ERROR", "message": str(e)}}
