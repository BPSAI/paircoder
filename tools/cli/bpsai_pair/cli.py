from __future__ import annotations

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


def print_json(data: dict) -> None:
    """Print JSON to stdout without Rich formatting."""
    sys.stdout.write(json.dumps(data, indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()

# Try relative imports first, fall back to absolute
try:
    from . import __version__
    from . import init_bundled_cli
    from . import ops
    from .config import Config
    from .flows import FlowParser, FlowValidationError
    from .flows.parser_v2 import FlowParser as FlowParserV2
    from .planning.cli_commands import plan_app, task_app, intent_app, standup_app
    from .orchestration import Orchestrator, HeadlessSession, HandoffManager
    from .orchestration import AgentSelector, SelectionCriteria, select_agent_for_task
    from .metrics import MetricsCollector, MetricsReporter, BudgetEnforcer, BudgetConfig, VelocityTracker
    from .integrations import TimeTrackingManager, TimeTrackingConfig
    from .benchmarks import BenchmarkRunner, BenchmarkConfig, BenchmarkReporter
    from .context import ContextCache, ContextLoader
    from .trello.commands import app as trello_app
    from .trello.task_commands import app as trello_task_app
    from .presets import get_preset, list_presets, get_preset_names, PresetManager
    from .github.commands import app as github_app
except ImportError:
    # For development/testing when running as script
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bpsai_pair import __version__
    from bpsai_pair import init_bundled_cli
    from bpsai_pair import ops
    from bpsai_pair.config import Config
    from bpsai_pair.flows import FlowParser, FlowValidationError
    from bpsai_pair.flows.parser_v2 import FlowParser as FlowParserV2
    from bpsai_pair.planning.cli_commands import plan_app, task_app, intent_app, standup_app
    from bpsai_pair.orchestration import Orchestrator, HeadlessSession, HandoffManager
    from bpsai_pair.orchestration import AgentSelector, SelectionCriteria, select_agent_for_task
    from bpsai_pair.metrics import MetricsCollector, MetricsReporter, BudgetEnforcer, BudgetConfig, VelocityTracker
    from bpsai_pair.integrations import TimeTrackingManager, TimeTrackingConfig
    from bpsai_pair.benchmarks import BenchmarkRunner, BenchmarkConfig, BenchmarkReporter
    from bpsai_pair.context import ContextCache, ContextLoader
    from bpsai_pair.trello.commands import app as trello_app
    from bpsai_pair.trello.task_commands import app as trello_task_app
    from bpsai_pair.presets import get_preset, list_presets, get_preset_names, PresetManager
    from bpsai_pair.github.commands import app as github_app

# Initialize Rich console
console = Console()

# Environment variable support
MAIN_BRANCH = os.getenv("PAIRCODER_MAIN_BRANCH", "main")
CONTEXT_DIR = os.getenv("PAIRCODER_CONTEXT_DIR", ".paircoder/context")
FLOWS_DIR = os.getenv("PAIRCODER_FLOWS_DIR", ".paircoder/flows")

app = typer.Typer(
    add_completion=False,
    help="bpsai-pair: AI pair-coding workflow CLI",
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Flow sub-app for managing flows (Paircoder-native skills)
flow_app = typer.Typer(
    help="Manage flows (Paircoder-native skills)",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(flow_app, name="flow")

# Plan and Task sub-apps for v2 planning system
app.add_typer(plan_app, name="plan")
app.add_typer(task_app, name="task")
app.add_typer(intent_app, name="intent")
app.add_typer(standup_app, name="standup")

# Orchestration sub-app for multi-agent coordination
orchestrate_app = typer.Typer(
    help="Multi-agent orchestration commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(orchestrate_app, name="orchestrate")

# Metrics sub-app for token tracking and cost estimation
metrics_app = typer.Typer(
    help="Token tracking and cost estimation",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(metrics_app, name="metrics")

# Preset sub-app for managing configuration presets
preset_app = typer.Typer(
    help="Manage configuration presets",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(preset_app, name="preset")


@preset_app.command("list")
def preset_list(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """List available configuration presets."""
    presets = list_presets()

    if json_out:
        print_json([{
            "name": p.name,
            "description": p.description,
            "project_type": p.project_type,
            "coverage_target": p.coverage_target,
            "flows": p.enabled_flows,
        } for p in presets])
    else:
        table = Table(title="Available Presets")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description")
        table.add_column("Coverage", justify="right")

        for p in presets:
            table.add_row(
                p.name,
                p.project_type,
                p.description,
                f"{p.coverage_target}%"
            )

        console.print(table)
        console.print("\n[dim]Use: bpsai-pair init --preset <name> --name <project> --goal <goal>[/dim]")


@preset_app.command("show")
def preset_show(
    name: str = typer.Argument(..., help="Preset name"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show details for a specific preset."""
    preset = get_preset(name)

    if not preset:
        console.print(f"[red]✗ Unknown preset: {name}[/red]")
        console.print(f"[dim]Available: {', '.join(get_preset_names())}[/dim]")
        raise typer.Exit(1)

    if json_out:
        print_json({
            "name": preset.name,
            "description": preset.description,
            "project_type": preset.project_type,
            "coverage_target": preset.coverage_target,
            "default_branch_type": preset.default_branch_type,
            "main_branch": preset.main_branch,
            "python_formatter": preset.python_formatter,
            "node_formatter": preset.node_formatter,
            "flows": preset.enabled_flows,
            "pack_excludes": preset.pack_excludes,
            "model_routing": preset.model_routing,
        })
    else:
        console.print(f"[bold cyan]{preset.name}[/bold cyan]")
        console.print(f"[dim]{preset.description}[/dim]\n")

        console.print("[bold]Project Settings[/bold]")
        console.print(f"  Type: {preset.project_type}")
        console.print(f"  Coverage target: {preset.coverage_target}%")

        console.print("\n[bold]Workflow Settings[/bold]")
        console.print(f"  Branch type: {preset.default_branch_type}")
        console.print(f"  Main branch: {preset.main_branch}")

        console.print("\n[bold]Formatters[/bold]")
        console.print(f"  Python: {preset.python_formatter}")
        console.print(f"  Node: {preset.node_formatter}")

        console.print("\n[bold]Enabled Flows[/bold]")
        for flow in preset.enabled_flows:
            console.print(f"  - {flow}")

        console.print(f"\n[bold]Pack Excludes[/bold] ({len(preset.pack_excludes)} patterns)")
        for exclude in preset.pack_excludes[:5]:
            console.print(f"  - {exclude}")
        if len(preset.pack_excludes) > 5:
            console.print(f"  ... and {len(preset.pack_excludes) - 5} more")

        if preset.model_routing:
            console.print("\n[bold]Model Routing[/bold]")
            console.print("  [green]✓[/green] Complexity-based routing enabled")


@preset_app.command("preview")
def preset_preview(
    name: str = typer.Argument(..., help="Preset name"),
    project_name: str = typer.Option("My Project", "--name", "-n", help="Project name"),
    goal: str = typer.Option("Build awesome software", "--goal", "-g", help="Primary goal"),
):
    """Preview the config.yaml that would be generated."""
    preset = get_preset(name)

    if not preset:
        console.print(f"[red]✗ Unknown preset: {name}[/red]")
        console.print(f"[dim]Available: {', '.join(get_preset_names())}[/dim]")
        raise typer.Exit(1)

    yaml_output = preset.to_yaml(project_name, goal)
    console.print("[bold]Generated config.yaml:[/bold]\n")
    console.print(yaml_output)


# Timer sub-app for time tracking
timer_app = typer.Typer(
    help="Time tracking integration",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(timer_app, name="timer")

# Benchmark sub-app for performance testing
benchmark_app = typer.Typer(
    help="AI agent benchmarking framework",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(benchmark_app, name="benchmark")

# Cache sub-app for context caching
cache_app = typer.Typer(
    help="Context caching for efficient context management",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(cache_app, name="cache")

# MCP sub-app for Model Context Protocol server
mcp_app = typer.Typer(
    help="MCP (Model Context Protocol) server commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(mcp_app, name="mcp")

# Trello integration sub-apps
try:
    app.add_typer(trello_app, name="trello")
    app.add_typer(trello_task_app, name="ttask")
except NameError:
    # Trello module not available (py-trello not installed)
    pass

# GitHub integration sub-app
try:
    app.add_typer(github_app, name="github")
except NameError:
    # GitHub module not available
    pass

def _flows_root(root: Path) -> Path:
    return root / ".paircoder" / "flows"


# --- Orchestration Commands ---

@orchestrate_app.command("task")
def orchestrate_task(
    task_id: str = typer.Argument(..., help="Task ID to orchestrate"),
    prefer: Optional[str] = typer.Option(None, "--prefer", help="Preferred agent"),
    max_cost: Optional[float] = typer.Option(None, "--max-cost", help="Maximum cost in USD"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show decision without executing"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Orchestrate a task to the best agent."""
    root = repo_root()
    orchestrator = Orchestrator(project_root=root)

    constraints = {}
    if prefer:
        constraints["prefer"] = prefer
    if max_cost:
        constraints["max_cost"] = max_cost

    assignment = orchestrator.assign_task(task_id, constraints)

    if not dry_run:
        assignment = orchestrator.execute(assignment, dry_run=False)

    if json_out:
        print_json({
            "task_id": assignment.task_id,
            "agent": assignment.agent,
            "status": assignment.status,
            "score": assignment.score,
            "reasoning": assignment.reasoning,
        })
    else:
        console.print(f"[bold]Task:[/bold] {assignment.task_id}")
        console.print(f"[bold]Agent:[/bold] {assignment.agent}")
        console.print(f"[bold]Score:[/bold] {assignment.score:.2f}")
        console.print(f"[bold]Status:[/bold] {assignment.status}")
        if assignment.reasoning:
            console.print(f"[bold]Reasoning:[/bold] {assignment.reasoning}")


@orchestrate_app.command("analyze")
def orchestrate_analyze(
    task_id: str = typer.Argument(..., help="Task ID to analyze"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Analyze a task and show routing decision."""
    root = repo_root()
    orchestrator = Orchestrator(project_root=root)

    task = orchestrator.analyze_task(task_id)
    decision = orchestrator.select_agent(task)

    # Also get specialized agent recommendation
    task_title, task_tags = _load_task_metadata(root, task_id)
    specialized_match = select_agent_for_task(
        task_type=task.task_type.value,
        task_title=task_title or task.description[:100],
        task_tags=task_tags,
        complexity={"low": 25, "medium": 50, "high": 75}.get(task.complexity.value, 50),
        agents_dir=root / ".claude" / "agents",
        working_dir=root,
    )

    if json_out:
        print_json({
            "task_id": task.task_id,
            "type": task.task_type.value,
            "complexity": task.complexity.value,
            "recommended_agent": decision.agent,
            "score": decision.score,
            "reasoning": decision.reasoning,
            "specialized_agent": {
                "agent": specialized_match.agent_name,
                "score": specialized_match.score,
                "reasons": specialized_match.reasons,
                "permission_mode": specialized_match.permission_mode,
            },
        })
    else:
        console.print(f"[bold]Task:[/bold] {task.task_id}")
        console.print(f"[bold]Type:[/bold] {task.task_type.value}")
        console.print(f"[bold]Complexity:[/bold] {task.complexity.value}")
        console.print(f"[bold]Recommended Agent:[/bold] {decision.agent}")
        console.print(f"[bold]Score:[/bold] {decision.score:.2f}")
        if decision.reasoning:
            console.print(f"[bold]Reasoning:[/bold]")
            for reason in decision.reasoning:
                console.print(f"  • {reason}")

        # Show specialized agent recommendation
        if specialized_match.agent_name != "claude-code":
            console.print()
            console.print(f"[bold cyan]Specialized Agent:[/bold cyan] {specialized_match.agent_name}")
            console.print(f"[bold cyan]Score:[/bold cyan] {specialized_match.score:.2f}")
            console.print(f"[bold cyan]Mode:[/bold cyan] {specialized_match.permission_mode}")
            if specialized_match.reasons:
                console.print(f"[bold cyan]Reasons:[/bold cyan]")
                for reason in specialized_match.reasons:
                    console.print(f"  • {reason}")


def _load_task_metadata(root: Path, task_id: str) -> tuple[str, list[str]]:
    """Load task title and tags from task file."""
    import yaml as yaml_mod

    task_file = root / ".paircoder" / "tasks" / f"{task_id}.task.md"
    if not task_file.exists():
        return "", []

    try:
        content = task_file.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml_mod.safe_load(parts[1])
                title = frontmatter.get("title", "")
                tags = frontmatter.get("tags", [])
                return title, tags if isinstance(tags, list) else []
    except Exception:
        pass

    return "", []


@orchestrate_app.command("select-agent")
def orchestrate_select_agent(
    task_id: str = typer.Argument(..., help="Task ID to analyze"),
    prefer: Optional[str] = typer.Option(None, "--prefer", help="Preferred agent"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Select the best specialized agent for a task.

    Uses the AgentSelector to route tasks to specialized agents:
    - planner: For design/planning tasks
    - reviewer: For code review/PR tasks
    - security: For security/auth-related tasks
    - claude-code: Default for general tasks
    """
    root = repo_root()

    # Load task metadata
    task_title, task_tags = _load_task_metadata(root, task_id)

    # Get task characteristics for complexity
    orchestrator = Orchestrator(project_root=root)
    task = orchestrator.analyze_task(task_id)

    # Create selector and select agent
    selector = AgentSelector(
        agents_dir=root / ".claude" / "agents",
        working_dir=root,
    )

    criteria = SelectionCriteria(
        task_type=task.task_type.value,
        task_title=task_title or task.description[:100],
        task_tags=task_tags,
        complexity={"low": 25, "medium": 50, "high": 75}.get(task.complexity.value, 50),
        preferred_agent=prefer,
    )

    match = selector.select(criteria)
    all_matches = selector.get_all_matches(criteria)

    if json_out:
        print_json({
            "task_id": task_id,
            "selected_agent": match.agent_name,
            "score": match.score,
            "reasons": match.reasons,
            "permission_mode": match.permission_mode,
            "all_matches": [m.to_dict() for m in all_matches],
        })
    else:
        console.print(f"[bold]Task:[/bold] {task_id}")
        if task_title:
            console.print(f"[bold]Title:[/bold] {task_title}")
        if task_tags:
            console.print(f"[bold]Tags:[/bold] {', '.join(task_tags)}")
        console.print()
        console.print(f"[bold green]Selected Agent:[/bold green] {match.agent_name}")
        console.print(f"[bold]Score:[/bold] {match.score:.2f}")
        console.print(f"[bold]Permission Mode:[/bold] {match.permission_mode}")
        if match.reasons:
            console.print(f"[bold]Reasons:[/bold]")
            for reason in match.reasons:
                console.print(f"  • {reason}")

        # Show other candidates if available
        if len(all_matches) > 1:
            console.print()
            console.print("[bold]Other Candidates:[/bold]")
            for m in all_matches[1:4]:  # Show top 3 alternatives
                console.print(f"  • {m.agent_name}: {m.score:.2f}")


@orchestrate_app.command("handoff")
def orchestrate_handoff(
    task_id: str = typer.Argument(..., help="Task ID for handoff"),
    target: str = typer.Option("codex", "--to", help="Target agent"),
    summary: str = typer.Option("", "--summary", help="Conversation summary"),
    output: Optional[str] = typer.Option(None, "--out", help="Output file path"),
):
    """Create a handoff package for another agent."""
    root = repo_root()
    manager = HandoffManager(project_root=root)

    output_path = Path(output) if output else None
    package_path = manager.pack(
        task_id=task_id,
        target_agent=target,
        conversation_summary=summary,
        output_path=output_path,
    )

    console.print(f"[green]✓[/green] Created handoff package: {package_path}")


@orchestrate_app.command("auto-run")
def orchestrate_auto_run(
    task_id: Optional[str] = typer.Argument(None, help="Task ID (auto-selects if not provided)"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID for task selection"),
    create_pr: bool = typer.Option(True, "--pr/--no-pr", help="Create PR on completion"),
    run_tests: bool = typer.Option(True, "--test/--no-test", help="Run tests before PR"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run autonomous workflow for a single task."""
    from .orchestration.autonomous import AutonomousWorkflow, WorkflowConfig

    root = repo_root()
    paircoder_dir = root / ".paircoder"

    config = WorkflowConfig(
        auto_select_tasks=task_id is None,
        auto_create_pr=create_pr,
        run_tests_before_pr=run_tests,
    )

    workflow = AutonomousWorkflow(paircoder_dir, config)

    success = workflow.run_task_workflow(task_id=task_id, plan_id=plan_id)

    if json_out:
        print_json(workflow.get_status())
    else:
        status = workflow.get_status()
        if success:
            console.print("[green]Workflow completed successfully[/green]")
        else:
            console.print("[red]Workflow failed or no tasks available[/red]")

        console.print(f"  Phase: {status['workflow_state']['phase']}")
        console.print(f"  Events: {status['workflow_state']['events_count']}")
        if status['workflow_state']['error']:
            console.print(f"  Error: {status['workflow_state']['error']}")


@orchestrate_app.command("auto-session")
def orchestrate_auto_session(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID for task selection"),
    max_tasks: int = typer.Option(5, "--max", "-m", help="Maximum tasks to process"),
    create_pr: bool = typer.Option(True, "--pr/--no-pr", help="Create PRs"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run autonomous session processing multiple tasks."""
    from .orchestration.autonomous import AutonomousWorkflow, WorkflowConfig

    root = repo_root()
    paircoder_dir = root / ".paircoder"

    config = WorkflowConfig(
        auto_select_tasks=True,
        auto_create_pr=create_pr,
        max_tasks_per_session=max_tasks,
    )

    workflow = AutonomousWorkflow(paircoder_dir, config)
    completed = workflow.run_session(plan_id=plan_id, max_tasks=max_tasks)

    if json_out:
        print_json({"completed_tasks": completed, "count": len(completed)})
    else:
        console.print(f"[green]Session completed: {len(completed)} tasks done[/green]")
        for task_id in completed:
            console.print(f"  - {task_id}")


@orchestrate_app.command("workflow-status")
def orchestrate_workflow_status(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show current autonomous workflow status."""
    from .orchestration.autonomous import AutonomousWorkflow

    root = repo_root()
    paircoder_dir = root / ".paircoder"

    workflow = AutonomousWorkflow(paircoder_dir)
    status = workflow.get_status()

    if json_out:
        print_json(status)
    else:
        console.print("[bold]Workflow Status[/bold]")
        console.print(f"  Phase: {status['workflow_state']['phase']}")
        console.print(f"  Current Task: {status['workflow_state']['current_task_id'] or 'None'}")
        console.print(f"  Current Flow: {status['workflow_state']['current_flow'] or 'None'}")
        console.print(f"  PR Number: {status['workflow_state']['pr_number'] or 'None'}")

        console.print("\n[bold]Configuration[/bold]")
        for key, value in status['config'].items():
            console.print(f"  {key}: {value}")


# --- Metrics Commands ---

def _get_metrics_collector() -> MetricsCollector:
    """Get a metrics collector instance."""
    root = repo_root()
    history_dir = root / ".paircoder" / "history"
    return MetricsCollector(history_dir)


@metrics_app.command("summary")
def metrics_summary(
    period: str = typer.Option("daily", "--period", "-p", help="Period: daily, weekly, monthly"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show metrics summary for a time period."""
    collector = _get_metrics_collector()
    reporter = MetricsReporter(collector)

    summary = reporter.get_summary(period)

    if json_out:
        print_json(summary.to_dict())
    else:
        console.print(reporter.format_summary_report(summary))


@metrics_app.command("task")
def metrics_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show metrics for a specific task."""
    collector = _get_metrics_collector()
    reporter = MetricsReporter(collector)

    metrics = reporter.get_task_metrics(task_id)

    if json_out:
        print_json(metrics)
    else:
        console.print(f"[bold]Task Metrics: {task_id}[/bold]")
        console.print(f"Events: {metrics['events']} ({metrics['successful']} success, {metrics['failed']} failed)")
        console.print(f"Tokens: {metrics['tokens']['total']:,} ({metrics['tokens']['input']:,} in / {metrics['tokens']['output']:,} out)")
        console.print(f"Cost: ${metrics['cost_usd']:.4f}")
        console.print(f"Duration: {metrics['duration_ms'] / 1000:.1f}s")


@metrics_app.command("breakdown")
def metrics_breakdown(
    by: str = typer.Option("agent", "--by", "-b", help="Breakdown by: agent, task, model"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show cost breakdown by dimension."""
    collector = _get_metrics_collector()
    reporter = MetricsReporter(collector)

    breakdown = reporter.get_breakdown(by)

    if json_out:
        print_json(breakdown)
    else:
        total_cost = sum(v["cost_usd"] for v in breakdown.values())
        table = Table(title=f"Cost Breakdown by {by.title()}")
        table.add_column(by.title(), style="cyan")
        table.add_column("Events", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("%", justify="right")

        for key, stats in sorted(breakdown.items(), key=lambda x: x[1]["cost_usd"], reverse=True):
            pct = (stats["cost_usd"] / total_cost * 100) if total_cost > 0 else 0
            table.add_row(
                key,
                str(stats["events"]),
                f"{stats['tokens']['total']:,}",
                f"${stats['cost_usd']:.4f}",
                f"{pct:.1f}%",
            )

        console.print(table)


@metrics_app.command("budget")
def metrics_budget(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show budget status."""
    collector = _get_metrics_collector()
    enforcer = BudgetEnforcer(collector)

    status = enforcer.check_budget()

    if json_out:
        print_json({
            "daily": {
                "spent": status.daily_spent,
                "limit": status.daily_limit,
                "remaining": status.daily_remaining,
                "percent": status.daily_percent,
            },
            "monthly": {
                "spent": status.monthly_spent,
                "limit": status.monthly_limit,
                "remaining": status.monthly_remaining,
                "percent": status.monthly_percent,
            },
            "alert": {
                "triggered": status.alert_triggered,
                "message": status.alert_message,
            },
        })
    else:
        console.print("[bold]Budget Status[/bold]")
        console.print("")
        console.print(f"Daily:   ${status.daily_spent:.2f} / ${status.daily_limit:.2f} ({status.daily_percent:.1f}%)")
        console.print(f"         Remaining: ${status.daily_remaining:.2f}")
        console.print("")
        console.print(f"Monthly: ${status.monthly_spent:.2f} / ${status.monthly_limit:.2f} ({status.monthly_percent:.1f}%)")
        console.print(f"         Remaining: ${status.monthly_remaining:.2f}")

        if status.alert_triggered:
            console.print("")
            console.print(f"[yellow]⚠ {status.alert_message}[/yellow]")


@metrics_app.command("export")
def metrics_export(
    output: str = typer.Option("metrics.csv", "--output", "-o", help="Output file path"),
    format_type: str = typer.Option("csv", "--format", "-f", help="Export format: csv"),
):
    """Export metrics to file."""
    collector = _get_metrics_collector()
    reporter = MetricsReporter(collector)

    if format_type.lower() == "csv":
        csv_content = reporter.export_csv()
        Path(output).write_text(csv_content)
        console.print(f"[green]✓[/green] Exported metrics to {output}")
    else:
        console.print(f"[red]Unsupported format: {format_type}[/red]")
        raise typer.Exit(1)


def _get_velocity_tracker() -> VelocityTracker:
    """Get a velocity tracker instance."""
    root = repo_root()
    history_dir = root / ".paircoder" / "history"
    return VelocityTracker(history_dir)


@metrics_app.command("velocity")
def metrics_velocity(
    weeks: int = typer.Option(4, "--weeks", "-w", help="Number of weeks for rolling average"),
    sprints: int = typer.Option(3, "--sprints", "-s", help="Number of sprints for average"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show velocity metrics for project planning."""
    root = repo_root()
    tracker = _get_velocity_tracker()

    # Get current sprint from state.md if available
    from .planning.state import StateManager
    state_manager = StateManager(root / ".paircoder")
    current_sprint = state_manager.state.active_sprint_id or ""

    stats = tracker.get_velocity_stats(
        current_sprint=current_sprint,
        weeks_for_average=weeks,
        sprints_for_average=sprints,
    )

    if json_out:
        print_json(stats.to_dict())
    else:
        console.print("[bold]Velocity Metrics[/bold]")
        console.print("")

        console.print(f"Points completed this week:     {stats.points_this_week}")
        if current_sprint:
            console.print(f"Points completed this sprint:   {stats.points_this_sprint} ({current_sprint})")
        else:
            console.print(f"Points completed this sprint:   {stats.points_this_sprint}")
        console.print("")

        console.print(f"Average weekly velocity ({weeks} weeks): {stats.avg_weekly_velocity:.1f}")
        console.print(f"Average sprint velocity ({sprints} sprints): {stats.avg_sprint_velocity:.1f}")
        console.print("")

        # Show weekly breakdown
        breakdown = tracker.get_weekly_breakdown(weeks=weeks)
        if breakdown and any(b["points"] > 0 for b in breakdown):
            console.print("[bold]Weekly Breakdown:[/bold]")
            table = Table()
            table.add_column("Week Start", style="cyan")
            table.add_column("Points", justify="right")

            for entry in breakdown:
                table.add_row(entry["week_start"], str(entry["points"]))

            console.print(table)
            console.print("")

        # Show sprint breakdown
        sprint_breakdown = tracker.get_sprint_breakdown()
        if sprint_breakdown:
            console.print("[bold]Sprint Breakdown:[/bold]")
            table = Table()
            table.add_column("Sprint", style="cyan")
            table.add_column("Points", justify="right")

            for sprint_id in sorted(sprint_breakdown.keys(), reverse=True):
                table.add_row(sprint_id, str(sprint_breakdown[sprint_id]))

            console.print(table)

        if stats.weeks_tracked == 0 and stats.sprints_tracked == 0:
            console.print("[dim]No velocity data recorded yet.[/dim]")
            console.print("[dim]Velocity is tracked when tasks are completed.[/dim]")


def _get_burndown_generator():
    """Get a burndown generator instance."""
    from .metrics import BurndownGenerator
    root = repo_root()
    history_dir = root / ".paircoder" / "history"
    return BurndownGenerator(history_dir)


@metrics_app.command("burndown")
def metrics_burndown(
    sprint: str = typer.Option(None, "--sprint", "-s", help="Sprint ID (default: current sprint)"),
    start_date: str = typer.Option(None, "--start", help="Sprint start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", help="Sprint end date (YYYY-MM-DD)"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Generate burndown chart data for a sprint."""
    from .metrics import BurndownGenerator, SprintConfig
    from .planning.state import StateManager
    from .planning.parser import TaskParser

    root = repo_root()
    generator = _get_burndown_generator()

    # Get sprint ID
    if not sprint:
        state_manager = StateManager(root / ".paircoder")
        sprint = state_manager.state.active_sprint_id or ""
        if not sprint:
            console.print("[yellow]No sprint specified and no active sprint found.[/yellow]")
            console.print("Use --sprint to specify a sprint ID.")
            raise typer.Exit(1)

    # Parse dates or use defaults
    from datetime import datetime, timedelta

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid date format: {start_date}. Use YYYY-MM-DD.[/red]")
            raise typer.Exit(1)
    else:
        # Default to 2 weeks ago
        start_dt = datetime.now() - timedelta(days=14)

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid date format: {end_date}. Use YYYY-MM-DD.[/red]")
            raise typer.Exit(1)
    else:
        # Default to today
        end_dt = datetime.now()

    # Get total points from tasks
    task_parser = TaskParser(root / ".paircoder" / "tasks")
    tasks = task_parser.parse_all()
    sprint_tasks = [t for t in tasks if t.sprint == sprint]
    total_points = sum(t.complexity for t in sprint_tasks)

    if total_points == 0:
        console.print(f"[yellow]No tasks found for sprint '{sprint}'.[/yellow]")
        raise typer.Exit(1)

    # Create config and generate burndown
    config = SprintConfig(
        sprint_id=sprint,
        start_date=start_dt,
        end_date=end_dt,
        total_points=total_points,
    )

    data = generator.generate(config)

    if json_out:
        print_json(data.to_dict())
    else:
        console.print(f"[bold]Burndown Chart: {sprint}[/bold]")
        console.print("")
        console.print(f"Period: {config.start_date.strftime('%Y-%m-%d')} to {config.end_date.strftime('%Y-%m-%d')}")
        console.print(f"Total Points: {config.total_points}")
        console.print("")

        if data.data_points:
            table = Table()
            table.add_column("Date", style="cyan")
            table.add_column("Remaining", justify="right")
            table.add_column("Ideal", justify="right")
            table.add_column("Completed", justify="right")
            table.add_column("Status")

            for point in data.data_points:
                # Determine status indicator
                diff = point.remaining - point.ideal
                if diff < -5:
                    status = "[green]▲ Ahead[/green]"
                elif diff > 5:
                    status = "[red]▼ Behind[/red]"
                else:
                    status = "[yellow]● On Track[/yellow]"

                table.add_row(
                    point.date.strftime("%Y-%m-%d"),
                    str(point.remaining),
                    f"{point.ideal:.0f}",
                    str(point.completed),
                    status,
                )

            console.print(table)

            # Show summary
            last_point = data.data_points[-1]
            console.print("")
            console.print(f"Current Progress: {last_point.completed}/{config.total_points} points")
            pct = (last_point.completed / config.total_points * 100) if config.total_points > 0 else 0
            console.print(f"Completion: {pct:.0f}%")
        else:
            console.print("[dim]No data points generated. Check sprint dates.[/dim]")


def _get_accuracy_analyzer():
    """Get an accuracy analyzer instance."""
    from .metrics.accuracy import AccuracyAnalyzer
    root = repo_root()
    history_dir = root / ".paircoder" / "history"
    return AccuracyAnalyzer(history_dir)


@metrics_app.command("accuracy")
def metrics_accuracy(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show estimation accuracy report.

    Analyzes how accurate task estimates have been compared to actual time spent.
    Shows overall accuracy, bias direction, and breakdowns by task type and complexity.
    """
    analyzer = _get_accuracy_analyzer()
    report = analyzer.generate_report()
    stats = report["stats"]

    if json_out:
        print_json(report)
    else:
        console.print("[bold]Estimation Accuracy Report[/bold]")
        console.print("=" * 26)
        console.print("")

        if stats["total_tasks"] == 0:
            console.print("[dim]No historical data available.[/dim]")
            console.print("[dim]Accuracy is tracked when tasks are completed with time tracking.[/dim]")
            return

        # Overall stats
        console.print(f"Overall Accuracy: {stats['overall_accuracy']:.0f}%")
        bias_str = f"Bias: {stats['bias_direction'].title()}"
        if stats["bias_direction"] != "neutral":
            bias_str += f" by {stats['bias_percent']:.0f}%"
        console.print(bias_str)
        console.print("")

        # By Task Type
        by_type = report["by_task_type"]
        if by_type:
            console.print("[bold]By Task Type:[/bold]")
            for t in by_type:
                bias_info = ""
                if t["bias_direction"] != "neutral":
                    direction = "under" if t["bias_direction"] == "optimistic" else "over"
                    bias_info = f" ({t['bias_percent']:.0f}% {direction}estimate)"
                console.print(f"- {t['task_type'].title()}: {t['accuracy_percent']:.0f}% accurate{bias_info}")
            console.print("")

        # By Complexity
        by_band = report["by_complexity_band"]
        if by_band:
            console.print("[bold]By Complexity:[/bold]")
            for b in by_band:
                console.print(f"- {b['band']} ({b['complexity_range']}): {b['accuracy_percent']:.0f}% accurate")
            console.print("")

        # Recommendation
        console.print(f"[bold]Recommendation:[/bold] {report['recommendation']}")


def _get_token_tracker():
    """Get a token feedback tracker instance."""
    from .metrics.estimation import TokenFeedbackTracker
    root = repo_root()
    history_dir = root / ".paircoder" / "history"
    return TokenFeedbackTracker(history_dir)


@metrics_app.command("tokens")
def metrics_tokens(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show token estimation accuracy report.

    Analyzes how accurate token estimates have been compared to actual usage.
    Shows overall accuracy ratio, breakdowns by task type, and recommendations
    for adjusting estimation coefficients.
    """
    tracker = _get_token_tracker()
    report = tracker.generate_report()
    stats = report["stats"]

    if json_out:
        print_json(report)
    else:
        console.print("[bold]Token Estimation Accuracy Report[/bold]")
        console.print("=" * 34)
        console.print("")

        if stats["total_tasks"] == 0:
            console.print("[dim]No token usage data available.[/dim]")
            console.print("[dim]Token accuracy is tracked when tasks are completed with metrics recording.[/dim]")
            return

        # Overall stats
        accuracy_pct = int((1 / stats["avg_ratio"]) * 100) if stats["avg_ratio"] > 0 else 100
        console.print(f"Tasks Analyzed: {stats['total_tasks']}")
        console.print(f"Avg Ratio (actual/estimated): {stats['avg_ratio']:.2f}x")

        if stats["avg_ratio"] > 1.1:
            console.print(f"[yellow]Bias: Underestimating by ~{int((stats['avg_ratio'] - 1) * 100)}%[/yellow]")
        elif stats["avg_ratio"] < 0.9:
            console.print(f"[yellow]Bias: Overestimating by ~{int((1 - stats['avg_ratio']) * 100)}%[/yellow]")
        else:
            console.print("[green]Bias: Estimates are well-calibrated[/green]")
        console.print("")

        # By Task Type
        by_type = report["by_task_type"]
        if by_type:
            console.print("[bold]By Task Type:[/bold]")
            for task_type, type_stats in by_type.items():
                ratio = type_stats["avg_ratio"]
                ratio_str = f"{ratio:.2f}x"
                if ratio > 1.1:
                    ratio_str = f"[yellow]{ratio:.2f}x (underestimate)[/yellow]"
                elif ratio < 0.9:
                    ratio_str = f"[cyan]{ratio:.2f}x (overestimate)[/cyan]"
                console.print(f"- {task_type.title()}: {ratio_str} ({type_stats['count']} tasks)")
            console.print("")

        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            console.print("[bold]Recommendations:[/bold]")
            for rec in recommendations:
                console.print(f"- {rec}")
        else:
            console.print("[dim]No coefficient adjustments recommended yet.[/dim]")


# --- Timer Commands ---

def _get_time_manager() -> TimeTrackingManager:
    """Get a time tracking manager instance."""
    root = repo_root()
    cache_path = root / ".paircoder" / "history" / "time-entries.json"
    config = TimeTrackingConfig()  # Will use defaults or env vars
    return TimeTrackingManager(config, cache_path)


@timer_app.command("start")
def timer_start(
    task_id: str = typer.Argument(..., help="Task ID to track time for"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Timer description"),
):
    """Start a timer for a task."""
    manager = _get_time_manager()

    desc = description or f"{task_id}: Working on task"
    timer_id = manager.provider.start_timer(task_id, desc)

    console.print(f"[green]✓[/green] Timer started: {desc}")
    console.print(f"  Timer ID: {timer_id}")


@timer_app.command("stop")
def timer_stop():
    """Stop the current timer."""
    manager = _get_time_manager()

    current = manager.get_status()
    if not current:
        console.print("[yellow]No active timer[/yellow]")
        return

    entry = manager.provider.stop_timer(current.id)

    duration_str = manager.format_duration(entry.duration) if entry.duration else "0m"
    console.print(f"[green]✓[/green] Timer stopped: {duration_str}")
    console.print(f"  Task: {entry.task_id}")
    console.print(f"  Description: {entry.description}")


@timer_app.command("status")
def timer_status():
    """Show current timer status."""
    manager = _get_time_manager()

    current = manager.get_status()
    if not current:
        console.print("[dim]No active timer[/dim]")
        return

    elapsed = datetime.now() - current.start
    elapsed_str = manager.format_duration(elapsed)

    console.print(f"[bold]Active Timer[/bold]")
    console.print(f"  Task: {current.task_id}")
    console.print(f"  Description: {current.description}")
    console.print(f"  Started: {current.start.strftime('%H:%M:%S')}")
    console.print(f"  Elapsed: {elapsed_str}")


@timer_app.command("show")
def timer_show(
    task_id: str = typer.Argument(..., help="Task ID"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show time entries for a task."""
    manager = _get_time_manager()

    entries = manager.get_task_entries(task_id)
    total = manager.get_task_time(task_id)

    if json_out:
        print_json({
            "task_id": task_id,
            "entries": [e.to_dict() for e in entries],
            "total_seconds": total.total_seconds(),
            "total_formatted": manager.format_duration(total),
        })
        return

    console.print(f"[bold]Time for {task_id}[/bold]")
    console.print(f"Total: {manager.format_duration(total)}")
    console.print("")

    if entries:
        console.print("Entries:")
        for entry in entries:
            date_str = entry.start.strftime("%Y-%m-%d")
            time_str = entry.start.strftime("%H:%M")
            duration_str = manager.format_duration(entry.duration) if entry.duration else "running"
            console.print(f"  - {date_str} {time_str} ({duration_str})")
    else:
        console.print("[dim]No entries recorded[/dim]")


@timer_app.command("summary")
def timer_summary(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Filter by plan"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show time summary across tasks."""
    manager = _get_time_manager()

    task_ids = manager.cache.get_all_tasks()

    if plan_id:
        # Filter by plan prefix
        task_ids = [t for t in task_ids if t.startswith(plan_id) or plan_id in t]

    summary = {}
    total = manager.provider.cache.get_total("_total") if hasattr(manager.provider, "cache") else None

    for task_id in task_ids:
        if task_id.startswith("_"):
            continue
        time_spent = manager.get_task_time(task_id)
        if time_spent.total_seconds() > 0:
            summary[task_id] = {
                "seconds": time_spent.total_seconds(),
                "formatted": manager.format_duration(time_spent),
            }

    if json_out:
        print_json(summary)
        return

    if not summary:
        console.print("[dim]No time entries found[/dim]")
        return

    table = Table(title="Time Summary")
    table.add_column("Task", style="cyan")
    table.add_column("Time", justify="right")

    grand_total = sum(v["seconds"] for v in summary.values())

    for task_id, data in sorted(summary.items()):
        table.add_row(task_id, data["formatted"])

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {manager.format_duration(timedelta(seconds=grand_total))}")


# --- Benchmark Commands ---

def _get_benchmark_paths():
    """Get paths for benchmarking."""
    root = repo_root()
    suite_path = root / ".paircoder" / "benchmarks" / "suite.yaml"
    output_dir = root / ".paircoder" / "history" / "benchmarks"
    return suite_path, output_dir


@benchmark_app.command("run")
def benchmark_run(
    only: Optional[str] = typer.Option(None, "--only", help="Comma-separated benchmark IDs"),
    agents: Optional[str] = typer.Option(None, "--agents", "-a", help="Comma-separated agents to test"),
    iterations: int = typer.Option(3, "--iterations", "-i", help="Number of iterations per benchmark"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run without executing"),
):
    """Run benchmarks."""
    suite_path, output_dir = _get_benchmark_paths()

    if not suite_path.exists():
        console.print(f"[red]Benchmark suite not found: {suite_path}[/red]")
        console.print("[dim]Create .paircoder/benchmarks/suite.yaml to define benchmarks[/dim]")
        raise typer.Exit(1)

    config = BenchmarkConfig(
        iterations=iterations,
        agents=agents.split(",") if agents else ["claude-code"],
        dry_run=dry_run,
    )

    runner = BenchmarkRunner(suite_path, output_dir, config)

    benchmark_ids = only.split(",") if only else None

    console.print("[bold]Running benchmarks...[/bold]\n")

    results = runner.run(
        benchmark_ids=benchmark_ids,
        agents=config.agents,
        iterations=iterations,
    )

    # Show summary
    for bench_id in set(r.benchmark_id for r in results):
        bench_results = [r for r in results if r.benchmark_id == bench_id]
        console.print(f"\n{bench_id}:")
        for agent in config.agents:
            agent_results = [r for r in bench_results if r.agent == agent]
            passed = sum(1 for r in agent_results if r.success)
            total = len(agent_results)
            avg_duration = sum(r.duration_seconds for r in agent_results) / total if total else 0
            avg_cost = sum(r.cost_usd for r in agent_results) / total if total else 0

            status = "✓" * passed + "✗" * (total - passed)
            console.print(f"  {agent}: {status} ({passed}/{total}, avg {avg_duration:.1f}s, ${avg_cost:.4f})")

    # Overall summary
    total = len(results)
    passed = sum(1 for r in results if r.success)
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total: {total} runs")
    console.print(f"  Passed: {passed} ({passed/total*100:.1f}%)")


@benchmark_app.command("results")
def benchmark_results(
    run_id: Optional[str] = typer.Option(None, "--id", help="Specific run ID"),
    latest: bool = typer.Option(True, "--latest", help="Show latest results"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """View benchmark results."""
    _, output_dir = _get_benchmark_paths()

    reporter = BenchmarkReporter(output_dir)
    results = reporter.load_results(run_id if not latest else None)

    if not results:
        console.print("[dim]No benchmark results found[/dim]")
        return

    if json_out:
        print_json([r.to_dict() for r in results])
    else:
        console.print(reporter.format_summary(results))


@benchmark_app.command("compare")
def benchmark_compare(
    baseline: str = typer.Option(..., "--baseline", "-b", help="Baseline agent"),
    challenger: str = typer.Option(..., "--challenger", "-c", help="Challenger agent"),
    run_id: Optional[str] = typer.Option(None, "--id", help="Specific run ID"),
):
    """Compare two agents."""
    _, output_dir = _get_benchmark_paths()

    reporter = BenchmarkReporter(output_dir)
    results = reporter.load_results(run_id)

    if not results:
        console.print("[dim]No benchmark results found[/dim]")
        return

    comparison = reporter.compare_agents(results, baseline, challenger)
    console.print(reporter.format_comparison(comparison))


@benchmark_app.command("list")
def benchmark_list():
    """List available benchmarks."""
    suite_path, _ = _get_benchmark_paths()

    if not suite_path.exists():
        console.print("[dim]No benchmark suite found[/dim]")
        console.print(f"[dim]Create {suite_path} to define benchmarks[/dim]")
        return

    from .benchmarks.runner import BenchmarkSuite
    suite = BenchmarkSuite.from_yaml(suite_path)

    table = Table(title="Available Benchmarks")
    table.add_column("ID", style="cyan")
    table.add_column("Category")
    table.add_column("Complexity")
    table.add_column("Description")

    for bench_id, bench in suite.benchmarks.items():
        table.add_row(
            bench_id,
            bench.category,
            bench.complexity,
            bench.description[:40] + "..." if len(bench.description) > 40 else bench.description,
        )

    console.print(table)


# --- Cache Commands ---

@cache_app.command("stats")
def cache_stats(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show cache statistics."""
    root = repo_root()
    cache = ContextCache(root / ".paircoder" / "cache")
    stats = cache.stats()

    if json_out:
        print_json(stats)
    else:
        console.print("[bold]Cache Statistics[/bold]")
        console.print(f"  Entries: {stats['entries']}")
        console.print(f"  Total size: {stats['total_bytes']:,} bytes")
        if stats['oldest']:
            console.print(f"  Oldest: {stats['oldest']}")
        if stats['newest']:
            console.print(f"  Newest: {stats['newest']}")


@cache_app.command("clear")
def cache_clear(
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Confirm clear"),
):
    """Clear the context cache."""
    if not confirm:
        console.print("[yellow]Use --confirm to clear the cache[/yellow]")
        raise typer.Exit(1)

    root = repo_root()
    cache = ContextCache(root / ".paircoder" / "cache")
    count = cache.clear()
    console.print(f"[green]Cleared {count} cache entries[/green]")


@cache_app.command("invalidate")
def cache_invalidate(
    file_path: str = typer.Argument(..., help="File path to invalidate"),
):
    """Invalidate cache for a specific file."""
    root = repo_root()
    cache = ContextCache(root / ".paircoder" / "cache")
    full_path = root / file_path

    if cache.invalidate(full_path):
        console.print(f"[green]Invalidated cache for {file_path}[/green]")
    else:
        console.print(f"[dim]No cache entry for {file_path}[/dim]")


# --- MCP Commands ---

@mcp_app.command("serve")
def mcp_serve(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport: stdio or sse"),
    port: int = typer.Option(3000, "--port", "-p", help="Port for SSE transport"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Start MCP server for Claude and other MCP-compatible agents."""
    try:
        from .mcp.server import run_server
    except ImportError:
        console.print("[red]MCP package not installed.[/red]")
        console.print("[dim]Install with: pip install 'bpsai-pair[mcp]'[/dim]")
        raise typer.Exit(1)

    if verbose:
        console.print(f"[dim]Starting MCP server on {transport}...[/dim]")

    try:
        run_server(transport=transport, port=port)
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@mcp_app.command("tools")
def mcp_tools(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """List available MCP tools."""
    from .mcp.server import list_tools

    tools = list_tools()

    if json_out:
        print_json({"tools": tools, "count": len(tools)})
    else:
        table = Table(title="Available MCP Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description")
        table.add_column("Parameters", style="dim")

        for tool in tools:
            params = ", ".join(tool["parameters"]) if tool["parameters"] else "-"
            table.add_row(tool["name"], tool["description"], params)

        console.print(table)


@mcp_app.command("test")
def mcp_test(
    tool: str = typer.Argument(..., help="Tool name to test"),
    input_json: str = typer.Argument("{}", help="JSON input for the tool"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Test an MCP tool locally."""
    import asyncio

    try:
        input_data = json.loads(input_json)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)

    try:
        from .mcp.server import test_tool
    except ImportError:
        console.print("[red]MCP package not installed.[/red]")
        console.print("[dim]Install with: pip install 'bpsai-pair[mcp]'[/dim]")
        raise typer.Exit(1)

    try:
        result = asyncio.run(test_tool(tool, input_data))

        if json_out:
            print_json(result)
        else:
            console.print(f"[bold]Tool:[/bold] {tool}")
            console.print(f"[bold]Input:[/bold] {input_data}")
            console.print(f"[bold]Result:[/bold]")
            console.print_json(data=result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@flow_app.command("list")
def flow_list(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    root = repo_root()
    flows_dir = _flows_root(root)

    if not flows_dir.exists():
        if json_out:
            print_json({
                "flows": [],
                "count": 0,
                "path": str(flows_dir),
            })
        else:
            console.print("[dim]No flows directory found at .paircoder/flows[/dim]")
        raise typer.Exit(0)

    # Use v2 parser which supports both .flow.yml and .flow.md
    parser = FlowParserV2(flows_dir)
    flows = parser.parse_all()

    if json_out:
        print_json({
            "flows": [f.to_dict() for f in flows],
            "count": len(flows),
            "path": str(flows_dir),
        })
    else:
        table = Table(title="Available Flows")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Format")
        table.add_column("Triggers")

        for f in flows:
            # Truncate description to fit table
            desc = f.description[:50] + "..." if len(f.description) > 50 else f.description
            desc = desc.replace("\n", " ").strip()
            triggers = ", ".join(f.triggers[:3]) if f.triggers else "-"
            table.add_row(
                f.name,
                desc,
                f.format.upper(),
                triggers,
            )

        console.print(table)

@flow_app.command("show")
def flow_show(
    name: str = typer.Argument(..., help="Flow name"),
    json_out: bool = typer.Option(False, "--json"),
):
    root = repo_root()
    flows_dir = _flows_root(root)

    # Use v2 parser which supports both .flow.yml and .flow.md
    parser = FlowParserV2(flows_dir)
    flow = parser.get_flow_by_name(name)

    if not flow:
        console.print(f"[red]Flow not found: {name}[/red]")
        raise typer.Exit(1)

    if json_out:
        print_json(flow.to_dict())
    else:
        # Display flow details
        console.print(f"[bold cyan]{flow.name}[/bold cyan]")
        console.print(f"[dim]Format: {flow.format.upper()} | Version: {flow.version}[/dim]")
        console.print()

        if flow.description:
            console.print(f"[bold]Description:[/bold]")
            console.print(f"  {flow.description.strip()}")
            console.print()

        if flow.when_to_use:
            console.print(f"[bold]When to use:[/bold]")
            for item in flow.when_to_use:
                console.print(f"  - {item}")
            console.print()

        if flow.roles:
            console.print(f"[bold]Roles:[/bold]")
            for role in flow.roles:
                primary = " (primary)" if role.primary else ""
                console.print(f"  - {role.name}{primary}")
            console.print()

        if flow.triggers:
            console.print(f"[bold]Triggers:[/bold] {', '.join(flow.triggers)}")
            console.print()

        if flow.body:
            console.print(f"[bold]Flow Body:[/bold]")
            console.print("-" * 60)
            console.print(flow.body)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]bpsai-pair[/bold blue] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit"
    )
):
    """bpsai-pair: AI pair-coding workflow CLI"""
    pass


def repo_root() -> Path:
    """Get repo root with better error message."""
    p = Path.cwd()
    if not ops.GitOps.is_repo(p):
        console.print(
            "[red]✗ Not in a git repository.[/red]\n"
            "Please run from your project root directory (where .git exists).\n"
            "[dim]Hint: cd to your project directory first[/dim]"
        )
        raise typer.Exit(1)
    return p

def ensure_v2_config(root: Path) -> Path:
    """Ensure v2 config exists at .paircoder/config.yaml.

    - If only legacy .paircoder.yml exists, it will be read and re-saved into v2 format.
    - If nothing exists, a default config will be written in v2 format.
    """
    v2_path = root / ".paircoder" / "config.yaml"
    if v2_path.exists():
        return v2_path

    # Load from legacy/env/defaults and persist in v2 location
    cfg = Config.load(root)
    cfg.save(root, use_v2=True)
    return v2_path

@app.command()
def init(
    template: Optional[str] = typer.Argument(
        None, help="Path to template (optional, uses bundled template if not provided)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode to gather project info"
    ),
    preset: Optional[str] = typer.Option(
        None, "--preset", "-p",
        help="Use a preset configuration (python-cli, python-api, react, fullstack, library, minimal, autonomous)"
    ),
    project_name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Project name (used with --preset)"
    ),
    goal: Optional[str] = typer.Option(
        None, "--goal", "-g", help="Primary goal (used with --preset)"
    ),
):
    """Initialize repo with governance, context, prompts, scripts, and workflows.

    Use --preset for quick setup with project-type-specific defaults:

        bpsai-pair init --preset python-cli --name "My CLI" --goal "Build awesome CLI"

    Available presets: python-cli, python-api, react, fullstack, library, minimal, autonomous

    Use --interactive for guided setup, or no flags for minimal scaffolding.
    """
    import yaml
    root = repo_root()

    preexisting_config = Config.find_config_file(root)

    # Handle preset-based initialization
    if preset:
        preset_obj = get_preset(preset)
        if not preset_obj:
            console.print(f"[red]✗ Unknown preset: {preset}[/red]")
            console.print(f"[dim]Available presets: {', '.join(get_preset_names())}[/dim]")
            raise typer.Exit(1)

        # Get project name and goal
        p_name = project_name or typer.prompt("Project name", default="My Project")
        p_goal = goal or typer.prompt("Primary goal", default="Build awesome software")

        # Generate config from preset
        config_dict = preset_obj.to_config_dict(p_name, p_goal)

        # Ensure .paircoder directory exists
        paircoder_dir = root / ".paircoder"
        paircoder_dir.mkdir(exist_ok=True)

        # Write config file
        config_file = paircoder_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓[/green] Applied preset: {preset}")
        console.print(f"  Project: {p_name}")
        console.print(f"  Goal: {p_goal}")
        console.print(f"  Coverage target: {preset_obj.coverage_target}%")
        console.print(f"  Flows: {', '.join(preset_obj.enabled_flows)}")

    elif interactive:
        # Interactive mode to gather project information
        pname = typer.prompt("Project name", default="My Project")
        primary_goal = typer.prompt("Primary goal", default="Build awesome software")
        coverage = typer.prompt("Coverage target (%)", default="80")

        # Ask about preset selection
        console.print("\n[bold]Available presets:[/bold]")
        for p in list_presets():
            console.print(f"  {p.name}: {p.description}")

        use_preset = typer.confirm("\nWould you like to use a preset?", default=False)
        if use_preset:
            preset_choice = typer.prompt(
                "Select preset",
                default="python-cli"
            )
            preset_obj = get_preset(preset_choice)
            if preset_obj:
                config_dict = preset_obj.to_config_dict(pname, primary_goal)
                config_dict["project"]["coverage_target"] = int(coverage)

                paircoder_dir = root / ".paircoder"
                paircoder_dir.mkdir(exist_ok=True)
                config_file = paircoder_dir / "config.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                console.print(f"[green]✓[/green] Applied preset: {preset_choice}")
            else:
                console.print(f"[yellow]⚠ Unknown preset, using defaults[/yellow]")
                config = Config(
                    project_name=pname,
                    primary_goal=primary_goal,
                    coverage_target=int(coverage)
                )
                config.save(root, use_v2=True)
        else:
            # Create a config file without preset
            config = Config(
                project_name=pname,
                primary_goal=primary_goal,
                coverage_target=int(coverage)
            )
            config.save(root, use_v2=True)

    # Use bundled template if none provided
    if template is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing scaffolding...", total=None)
            result = init_bundled_cli.main()
            progress.update(task, completed=True)

        console.print("[green]✓[/green] Initialized repo with pair-coding scaffolding")
        # Ensure v2 configuration exists (canonical: .paircoder/config.yaml)
        if not preset:  # Don't overwrite preset config
            ensure_v2_config(root)
        console.print("[dim]Review diffs and commit changes[/dim]")
    else:
        # Use provided template (simplified for now)
        console.print(f"[yellow]Using template: {template}[/yellow]")
        # Ensure v2 configuration exists (canonical: .paircoder/config.yaml)
        if not preset:  # Don't overwrite preset config
            ensure_v2_config(root)
        # If this repo had no config before init ran, ensure we have a canonical v2 config file.
        # This keeps v1 repos stable (no surprise migrations) while making new scaffolds v2-native.
        if preexisting_config is None and not preset:
            v2_config = root / ".paircoder" / "config.yaml"
            v2_config_yml = root / ".paircoder" / "config.yml"
            if not v2_config.exists() and not v2_config_yml.exists():
                # Use defaults/env (or the legacy config that the template may have created)
                # and persist them to the canonical v2 location.
                Config.load(root).save(root, use_v2=True)


@app.command()
def feature(
    name: str = typer.Argument(..., help="Feature branch name (without prefix)"),
    primary: str = typer.Option("", "--primary", "-p", help="Primary goal to stamp into context"),
    phase: str = typer.Option("", "--phase", help="Phase goal for Next action"),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass dirty-tree check"),
    type: str = typer.Option(
        "feature",
        "--type",
        "-t",
        help="Branch type: feature|fix|refactor",
        case_sensitive=False,
    ),
):
    """Create feature branch and scaffold context (cross-platform)."""
    root = repo_root()

    # Validate branch type
    branch_type = type.lower()
    if branch_type not in {"feature", "fix", "refactor"}:
        console.print(
            f"[red]✗ Invalid branch type: {type}[/red]\n"
            "Must be one of: feature, fix, refactor"
        )
        raise typer.Exit(1)

    # Use Python ops instead of shell script
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Creating {branch_type}/{name}...", total=None)

        try:
            ops.FeatureOps.create_feature(
                root=root,
                name=name,
                branch_type=branch_type,
                primary_goal=primary,
                phase=phase,
                force=force
            )
            progress.update(task, completed=True)

            console.print(f"[green]✓[/green] Created branch [bold]{branch_type}/{name}[/bold]")
            console.print(f"[green]✓[/green] Updated context with primary goal and phase")
            console.print("[dim]Next: Connect your agent and share /context files[/dim]")

        except ValueError as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗ {e}[/red]")
            raise typer.Exit(1)


@app.command()
def pack(
    output: str = typer.Option("agent_pack.tgz", "--out", "-o", help="Output archive name"),
    extra: Optional[List[str]] = typer.Option(None, "--extra", "-e", help="Additional paths to include"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview files without creating archive"),
    list_only: bool = typer.Option(False, "--list", "-l", help="List files to be included"),
    lite: bool = typer.Option(False, "--lite", help="Minimal pack for Codex CLI (< 32KB)"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Create agent context package (cross-platform)."""
    root = repo_root()
    output_path = root / output

    # Use Python ops for packing
    files = ops.ContextPacker.pack(
        root=root,
        output=output_path,
        extra_files=extra,
        dry_run=(dry_run or list_only),
        lite=lite,
    )

    if json_out:
        result = {
            "files": [str(f.relative_to(root)) for f in files],
            "count": len(files),
            "dry_run": dry_run,
            "list_only": list_only
        }
        if not (dry_run or list_only):
            result["output"] = str(output)
            result["size"] = output_path.stat().st_size if output_path.exists() else 0
        print_json(result)
    elif list_only:
        for f in files:
            console.print(str(f.relative_to(root)))
    elif dry_run:
        console.print(f"[yellow]Would pack {len(files)} files:[/yellow]")
        for f in files[:10]:  # Show first 10
            console.print(f"  • {f.relative_to(root)}")
        if len(files) > 10:
            console.print(f"  [dim]... and {len(files) - 10} more[/dim]")
    else:
        console.print(f"[green]✓[/green] Created [bold]{output}[/bold]")
        size_kb = output_path.stat().st_size / 1024
        console.print(f"  Size: {size_kb:.1f} KB")
        console.print(f"  Files: {len(files)}")
        console.print("[dim]Upload this archive to your agent session[/dim]")


@app.command("context-sync")
def context_sync(
    overall: Optional[str] = typer.Option(None, "--overall", help="Overall goal override"),
    last: str = typer.Option(..., "--last", "-l", help="What changed and why"),
    next: str = typer.Option(..., "--next", "--nxt", "-n", help="Next smallest valuable step"),
    blockers: str = typer.Option("", "--blockers", "-b", help="Blockers/Risks"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Update the Context Loop in /context/state.md (or legacy development.md)."""
    root = repo_root()
    context_dir = root / CONTEXT_DIR

    # Check for state.md (v2) first, then fallback to development.md (legacy)
    state_file = context_dir / "state.md"
    dev_file = context_dir / "development.md"

    if state_file.exists():
        context_file = state_file
        is_v2 = True
    elif dev_file.exists():
        context_file = dev_file
        is_v2 = False
    else:
        console.print(
            f"[red]✗ No context file found[/red]\n"
            "Run 'bpsai-pair init' first to set up the project structure"
        )
        raise typer.Exit(1)

    # Update context
    content = context_file.read_text()
    import re

    if is_v2:
        # v2 state.md format - update sections
        # Update "What Was Just Done" section
        content = re.sub(
            r'(## What Was Just Done\n\n).*?(?=\n## |\Z)',
            f'\\1- {last}\n\n',
            content,
            flags=re.DOTALL
        )
        # Update "What's Next" section
        content = re.sub(
            r"(## What's Next\n\n).*?(?=\n## |\Z)",
            f'\\g<1>1. {next}\n\n',
            content,
            flags=re.DOTALL
        )
        # Update "Blockers" section if provided
        if blockers:
            content = re.sub(
                r'(## Blockers\n\n).*?(?=\n## |\Z)',
                f'\\1{blockers if blockers else "None"}\n\n',
                content,
                flags=re.DOTALL
            )
        # Update "Active Plan" if overall provided
        if overall:
            content = re.sub(
                r'(\*\*Plan:\*\*) .*',
                f'\\1 {overall}',
                content
            )
    else:
        # Legacy development.md format
        if overall:
            content = re.sub(r'Overall goal is:.*', f'Overall goal is: {overall}', content)
        content = re.sub(r'Last action was:.*', f'Last action was: {last}', content)
        content = re.sub(r'Next action will be:.*', f'Next action will be: {next}', content)
        if blockers:
            content = re.sub(r'Blockers(/Risks)?:.*', f'Blockers/Risks: {blockers}', content)

    context_file.write_text(content)

    if json_out:
        result = {
            "updated": True,
            "file": str(context_file.relative_to(root)),
            "format": "v2" if is_v2 else "legacy",
            "context": {
                "overall": overall,
                "last": last,
                "next": next,
                "blockers": blockers
            }
        }
        print_json(result)
    else:
        console.print("[green]✓[/green] Context Sync updated")
        console.print(f"  [dim]Last: {last}[/dim]")
        console.print(f"  [dim]Next: {next}[/dim]")


# Alias for context-sync
app.command("sync", hidden=True)(context_sync)


@app.command()
def status(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show current context loop status and recent changes."""
    root = repo_root()
    context_dir = root / CONTEXT_DIR

    # Check for state.md (v2) first, then fallback to development.md (legacy)
    state_file = context_dir / "state.md"
    dev_file = context_dir / "development.md"

    # Get current branch
    current_branch = ops.GitOps.current_branch(root)
    is_clean = ops.GitOps.is_clean(root)

    # Parse context sync - check v2 format first
    context_data = {}
    import re

    if state_file.exists():
        content = state_file.read_text()

        # v2 state.md format
        plan_match = re.search(r'\*\*Plan:\*\*\s*(.*)', content)
        status_match = re.search(r'\*\*Status:\*\*\s*(.*)', content)
        # Get first bullet from "What Was Just Done"
        last_section = re.search(r'## What Was Just Done\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        # Get first item from "What's Next"
        next_section = re.search(r"## What's Next\n\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        blockers_section = re.search(r'## Blockers\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)

        last_text = "Not set"
        if last_section:
            lines = [l.strip() for l in last_section.group(1).strip().split('\n') if l.strip()]
            if lines:
                last_text = lines[0].lstrip('- ')

        next_text = "Not set"
        if next_section:
            lines = [l.strip() for l in next_section.group(1).strip().split('\n') if l.strip()]
            if lines:
                next_text = lines[0].lstrip('0123456789. ')

        blockers_text = "None"
        if blockers_section:
            blockers_text = blockers_section.group(1).strip() or "None"

        context_data = {
            "phase": status_match.group(1) if status_match else "Not set",
            "overall": plan_match.group(1) if plan_match else "Not set",
            "last": last_text,
            "next": next_text,
            "blockers": blockers_text
        }
    elif dev_file.exists():
        content = dev_file.read_text()

        # Legacy development.md format
        overall_match = re.search(r'Overall goal is:\s*(.*)', content)
        last_match = re.search(r'Last action was:\s*(.*)', content)
        next_match = re.search(r'Next action will be:\s*(.*)', content)
        blockers_match = re.search(r'Blockers(/Risks)?:\s*(.*)', content)
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.*)', content)

        context_data = {
            "phase": phase_match.group(1) if phase_match else "Not set",
            "overall": overall_match.group(1) if overall_match else "Not set",
            "last": last_match.group(1) if last_match else "Not set",
            "next": next_match.group(1) if next_match else "Not set",
            "blockers": blockers_match.group(2) if blockers_match else "None"
        }

    # Check for recent pack
    pack_files = list(root.glob("*.tgz"))
    latest_pack = None
    if pack_files:
        latest_pack = max(pack_files, key=lambda p: p.stat().st_mtime)

    if json_out:
        age_hours = None
        if latest_pack:
            age_hours = (datetime.now() - datetime.fromtimestamp(latest_pack.stat().st_mtime)).total_seconds() / 3600

        result = {
            "branch": current_branch,
            "clean": is_clean,
            "context": context_data,
            "latest_pack": str(latest_pack.name) if latest_pack else None,
            "pack_age": age_hours
        }
        print_json(result)
    else:
        # Create a nice table
        table = Table(title="PairCoder Status", show_header=False)
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")

        # Git status
        table.add_row("Branch", f"[bold]{current_branch}[/bold]")
        table.add_row("Working Tree", "[green]Clean[/green]" if is_clean else "[yellow]Modified[/yellow]")

        # Context status
        if context_data:
            table.add_row("Phase", context_data["phase"])
            table.add_row("Overall Goal", context_data["overall"][:60] + "..." if len(context_data["overall"]) > 60 else context_data["overall"])
            table.add_row("Last Action", context_data["last"][:60] + "..." if len(context_data["last"]) > 60 else context_data["last"])
            table.add_row("Next Action", context_data["next"][:60] + "..." if len(context_data["next"]) > 60 else context_data["next"])
            if context_data["blockers"] and context_data["blockers"] != "None":
                table.add_row("Blockers", f"[red]{context_data['blockers']}[/red]")

        # Pack status
        if latest_pack:
            age_hours = (datetime.now() - datetime.fromtimestamp(latest_pack.stat().st_mtime)).total_seconds() / 3600
            age_str = f"{age_hours:.1f} hours ago" if age_hours < 24 else f"{age_hours/24:.1f} days ago"
            table.add_row("Latest Pack", f"{latest_pack.name} ({age_str})")

        console.print(table)

        # Suggestions
        if not is_clean:
            console.print("\n[yellow]⚠ Working tree has uncommitted changes[/yellow]")
            console.print("[dim]Consider committing or stashing before creating a pack[/dim]")

        if not latest_pack or (latest_pack and age_hours is not None and age_hours > 24):
            console.print("\n[dim]Tip: Run 'bpsai-pair pack' to create a fresh context pack[/dim]")


@app.command()
def validate(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Validate repo structure and context consistency."""
    root = repo_root()
    issues = []
    fixes = []

    # Check required files (v2.1 paths with legacy fallback)
    required_files_v2 = [
        (Path(".paircoder/context/state.md"), Path("context/development.md")),
        (Path(".paircoder/config.yaml"), None),
        (Path("AGENTS.md"), Path("context/agents.md")),
        (Path("CLAUDE.md"), None),
        (Path(".agentpackignore"), None),
    ]

    for v2_path, legacy_path in required_files_v2:
        full_v2 = root / v2_path
        full_legacy = root / legacy_path if legacy_path else None

        # Check v2 path first, then legacy
        if full_v2.exists():
            continue  # v2 path exists, all good
        elif full_legacy and full_legacy.exists():
            issues.append(f"Using legacy path {legacy_path}, migrate to {v2_path}")
            continue  # Legacy exists, warn but don't block
        else:
            issues.append(f"Missing required file: {v2_path}")
            if fix:
                # Create with minimal content at v2 path
                full_v2.parent.mkdir(parents=True, exist_ok=True)
                if v2_path.name == "state.md":
                    full_v2.write_text("# Current State\n\n## Active Plan\n\nNo active plan.\n")
                elif v2_path.name == "config.yaml":
                    full_v2.write_text("version: 2.1\nproject_name: unnamed\n")
                elif v2_path.name == "AGENTS.md":
                    full_v2.write_text("# AGENTS.md\n\nSee `.paircoder/` for project context.\n")
                elif v2_path.name == "CLAUDE.md":
                    full_v2.write_text("# CLAUDE.md\n\nSee `.paircoder/context/state.md` for current state.\n")
                elif v2_path.name == ".agentpackignore":
                    full_v2.write_text(".git/\n.venv/\n__pycache__/\nnode_modules/\n")
                else:
                    full_v2.touch()
                fixes.append(f"Created {v2_path}")

    # Check context sync format (v2.1 state.md or legacy development.md)
    state_file = root / ".paircoder" / "context" / "state.md"
    dev_file = root / CONTEXT_DIR / "development.md"

    if state_file.exists():
        content = state_file.read_text()
        # v2.1 state.md uses different sections
        required_sections = ["## Active Plan", "## Current Focus"]
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing state section: {section}")
    elif dev_file.exists():
        content = dev_file.read_text()
        # Legacy development.md sections
        required_sections = [
            "Overall goal is:",
            "Last action was:",
            "Next action will be:",
        ]
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing context sync section: {section}")
                if fix:
                    content += f"\n{section} (to be updated)\n"
                    dev_file.write_text(content)
                    fixes.append(f"Added section: {section}")

    # Check for uncommitted context changes
    if not ops.GitOps.is_clean(root):
        context_files = [
            ".paircoder/context/state.md",
            "context/development.md",
            "AGENTS.md",
        ]
        for cf in context_files:
            if (root / cf).exists():
                result = subprocess.run(
                    ["git", "diff", "--name-only", cf],
                    cwd=root,
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    issues.append(f"Uncommitted changes in {cf}")

    if json_out:
        result = {
            "valid": len(issues) == 0,
            "issues": issues,
            "fixes_applied": fixes if fix else []
        }
        print_json(result)
    else:
        if issues:
            console.print("[red]✗ Validation failed[/red]")
            console.print("\nIssues found:")
            for issue in issues:
                console.print(f"  • {issue}")

            if fixes:
                console.print("\n[green]Fixed:[/green]")
                for fix_msg in fixes:
                    console.print(f"  ✓ {fix_msg}")
            elif not fix:
                console.print("\n[dim]Run with --fix to attempt automatic fixes[/dim]")
        else:
            console.print("[green]✓ All validation checks passed[/green]")


@app.command()
def ci(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run local CI checks (cross-platform)."""
    root = repo_root()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running CI checks...", total=None)

        results = ops.LocalCI.run_all(root)

        progress.update(task, completed=True)

    if json_out:
        print_json(results)
    else:
        console.print("[bold]Local CI Results[/bold]\n")

        # Python results
        if results["python"]:
            console.print("[cyan]Python:[/cyan]")
            for check, status in results["python"].items():
                icon = "✓" if "passed" in status else "✗"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        # Node results
        if results["node"]:
            console.print("\n[cyan]Node.js:[/cyan]")
            for check, status in results["node"].items():
                icon = "✓" if "passed" in status else "✗"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        if not results["python"] and not results["node"]:
            console.print("[dim]No Python or Node.js project detected[/dim]")


# ============================================================================
# Flow commands (v2) - YAML-based flows with steps
# ============================================================================


def _find_flow_v2(root: Path, name: str):
    """Find a flow by name using the v2 parser."""
    # Search paths in order of priority
    search_paths = [
        root / FLOWS_DIR,  # Primary location (.paircoder/flows)
        root / "flows",     # Fallback location
    ]

    for flows_dir in search_paths:
        if not flows_dir.exists():
            continue
        parser = FlowParserV2(flows_dir)
        flow = parser.get_flow_by_name(name)
        if flow:
            return flow

    return None


@flow_app.command("run")
def flow_run(
    name: str = typer.Argument(..., help="Flow name or filename"),
    var: Optional[List[str]] = typer.Option(
        None, "--var", "-v", help="Variable assignment (key=value)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run a flow and output as checklist (no LLM calls - renders steps only)."""
    root = repo_root()

    # Find the flow using v2 parser
    flow = _find_flow_v2(root, name)
    if not flow:
        console.print(f"[red]Flow not found: {name}[/red]")
        console.print(f"[dim]Available flows: bpsai-pair flow list[/dim]")
        raise typer.Exit(1)

    # Parse variables (v2 flows may not have variables, use empty dict as default)
    variables = {}
    if var:
        for v in var:
            if "=" not in v:
                console.print(f"[red]Invalid variable format: {v}[/red]")
                console.print("[dim]Use: --var key=value[/dim]")
                raise typer.Exit(1)
            key, value = v.split("=", 1)
            variables[key] = value

    if json_out:
        result = flow.to_dict()
        result["variables"] = variables
        print_json(result)
    else:
        # Display flow with steps/body
        console.print(f"[bold cyan]{flow.name}[/bold cyan]")
        console.print(f"[dim]Format: {flow.format.upper()}[/dim]")
        console.print()

        if flow.description:
            console.print(f"{flow.description.strip()}")
            console.print()

        if flow.steps:
            console.print("[bold]Steps:[/bold]")
            for i, step in enumerate(flow.steps, 1):
                console.print(f"  {i}. [{step.role}] {step.summary}")
                if step.checklist:
                    for item in step.checklist:
                        console.print(f"       - {item}")
            console.print()

        if flow.body:
            console.print("[bold]Instructions:[/bold]")
            console.print("-" * 60)
            console.print(flow.body)

        if variables:
            console.print("\n[dim]Variables:[/dim]")
            for k, v in variables.items():
                console.print(f"  [cyan]{k}[/cyan]: {v}")


@flow_app.command("validate")
def flow_validate(
    name: str = typer.Argument(..., help="Flow name or filename"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Validate a flow definition."""
    root = repo_root()

    # Find the flow using v2 parser
    flow = _find_flow_v2(root, name)
    if not flow:
        if json_out:
            print_json({"valid": False, "error": f"Flow not found: {name}"})
        else:
            console.print(f"[red]Flow not found: {name}[/red]")
        raise typer.Exit(1)

    # Basic validation for v2 flows
    errors = []
    if not flow.name:
        errors.append("Flow name is required")
    if not flow.description:
        errors.append("Flow description is recommended")

    if json_out:
        print_json({
            "valid": len(errors) == 0,
            "flow": flow.name,
            "format": flow.format,
            "file": str(flow.source_path) if flow.source_path else None,
            "errors": errors,
            "step_count": len(flow.steps),
            "has_body": bool(flow.body),
        })
    else:
        if errors:
            console.print(f"[red]Flow '{flow.name}' has validation errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise typer.Exit(1)
        else:
            console.print(f"[green]Flow '{flow.name}' is valid[/green]")
            console.print(f"  Format: {flow.format.upper()}")
            console.print(f"  Steps: {len(flow.steps)}")
            if flow.source_path:
                console.print(f"  File: {flow.source_path}")


# ============================================================================
# Security commands - Secret scanning
# ============================================================================

security_app = typer.Typer(
    help="Security tools for secret scanning and vulnerability detection",
    context_settings={"help_option_names": ["-h", "--help"]}
)
app.add_typer(security_app, name="security")


def _get_secret_scanner():
    """Get a SecretScanner instance with project allowlist."""
    from .security import SecretScanner, AllowlistConfig

    root = repo_root()
    allowlist_path = root / ".paircoder" / "security" / "secret-allowlist.yaml"
    allowlist = AllowlistConfig.load(allowlist_path)
    return SecretScanner(allowlist), root


@security_app.command("scan-secrets")
def scan_secrets(
    path: Optional[str] = typer.Argument(None, help="File or directory to scan"),
    staged: bool = typer.Option(False, "--staged", "-s", help="Scan staged git changes only"),
    diff_ref: Optional[str] = typer.Option(None, "--diff", "-d", help="Scan diff since git reference (e.g., HEAD~1)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Scan for secrets and credentials in code.

    By default, scans all files in the current directory.

    Examples:

        bpsai-pair security scan-secrets              # Scan all files

        bpsai-pair security scan-secrets --staged    # Scan staged changes

        bpsai-pair security scan-secrets --diff HEAD~1  # Scan since last commit

        bpsai-pair security scan-secrets src/        # Scan specific directory
    """
    from .security import SecretScanner, AllowlistConfig, format_scan_results

    scanner, root = _get_secret_scanner()

    matches = []

    if staged:
        # Scan staged changes
        matches = scanner.scan_staged(root)
        scan_target = "staged changes"
    elif diff_ref:
        # Scan since reference
        matches = scanner.scan_commit_range(diff_ref, root)
        scan_target = f"changes since {diff_ref}"
    elif path:
        # Scan specific path
        target = Path(path)
        if target.is_file():
            matches = scanner.scan_file(target)
            scan_target = str(target)
        elif target.is_dir():
            matches = scanner.scan_directory(target)
            scan_target = f"directory {target}"
        else:
            console.print(f"[red]Path not found: {path}[/red]")
            raise typer.Exit(1)
    else:
        # Scan entire project
        matches = scanner.scan_directory(root)
        scan_target = "project"

    if json_out:
        result = {
            "target": scan_target,
            "secrets_found": len(matches),
            "matches": [m.to_dict() for m in matches],
        }
        print_json(result)
    else:
        if matches:
            console.print(f"[red]Found {len(matches)} potential secret(s) in {scan_target}[/red]\n")
            console.print(format_scan_results(matches, verbose=verbose))
            console.print("\n[dim]Review these findings and remove any real secrets before committing.[/dim]")
            raise typer.Exit(1)
        else:
            console.print(f"[green]No secrets detected in {scan_target}[/green]")


@security_app.command("pre-commit")
def pre_commit_hook(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run secret scan as a pre-commit hook.

    This command is designed to be used in git hooks:

        # .git/hooks/pre-commit
        #!/bin/bash
        bpsai-pair security pre-commit

    Exit codes:
        0 - No secrets found
        1 - Secrets found (blocks commit)
    """
    from .security import format_scan_results

    scanner, root = _get_secret_scanner()
    matches = scanner.scan_staged(root)

    if json_out:
        print_json({
            "blocked": len(matches) > 0,
            "secrets_found": len(matches),
            "matches": [m.to_dict() for m in matches],
        })
    else:
        if matches:
            console.print("[red]BLOCKED: Secrets detected in staged changes[/red]\n")
            console.print(format_scan_results(matches, verbose=True))
            console.print("\n[yellow]Remove secrets before committing.[/yellow]")
            console.print("[dim]Use environment variables or a secrets manager instead.[/dim]")
            raise typer.Exit(1)
        else:
            console.print("[green]Pre-commit secret scan passed[/green]")


@security_app.command("install-hook")
def install_hook(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing hook"),
):
    """Install pre-commit hook for secret scanning.

    Creates .git/hooks/pre-commit to run secret scanning
    before each commit.
    """
    root = repo_root()
    hooks_dir = root / ".git" / "hooks"
    hook_path = hooks_dir / "pre-commit"

    hook_content = '''#!/bin/bash
# PairCoder secret scanning pre-commit hook
# Installed by: bpsai-pair security install-hook

set -e

echo "Running secret scan on staged changes..."
bpsai-pair security pre-commit

# Add other pre-commit checks below if needed
'''

    if hook_path.exists() and not force:
        console.print("[yellow]Pre-commit hook already exists[/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")

        # Check if our hook is already in there
        existing = hook_path.read_text()
        if "bpsai-pair security pre-commit" in existing:
            console.print("[green]Secret scanning already configured in hook[/green]")
            return

        console.print("\n[dim]You can manually add this line to your existing hook:[/dim]")
        console.print("  bpsai-pair security pre-commit")
        raise typer.Exit(1)

    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)

    console.print("[green]Installed pre-commit hook for secret scanning[/green]")
    console.print(f"  Location: {hook_path}")


# Also add scan-secrets as a top-level command for convenience
@app.command("scan-secrets")
def scan_secrets_shortcut(
    path: Optional[str] = typer.Argument(None, help="File or directory to scan"),
    staged: bool = typer.Option(False, "--staged", "-s", help="Scan staged git changes only"),
    diff_ref: Optional[str] = typer.Option(None, "--diff", "-d", help="Scan diff since git reference"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Scan for secrets and credentials (shortcut for 'security scan-secrets')."""
    # Call the security sub-command
    scan_secrets(path=path, staged=staged, diff_ref=diff_ref, verbose=verbose, json_out=json_out)


@security_app.command("scan-deps")
def scan_deps(
    path: Optional[str] = typer.Argument(None, help="Directory to scan for dependencies"),
    fail_on: Optional[str] = typer.Option(None, "--fail-on", "-f", help="Fail if severity >= value (low, medium, high, critical)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching of scan results"),
):
    """Scan dependencies for known vulnerabilities.

    Scans Python (pip-audit) and npm (npm audit) dependencies for CVEs.

    Examples:

        bpsai-pair security scan-deps             # Scan all dependencies

        bpsai-pair security scan-deps --fail-on high  # Fail on high+ severity

        bpsai-pair security scan-deps --verbose   # Show detailed CVE info
    """
    from .security import DependencyScanner, Severity, format_scan_report

    root = Path(path) if path else repo_root()
    scanner = DependencyScanner()

    report = scanner.scan_all(root, use_cache=not no_cache)

    if json_out:
        print_json(report.to_dict())
    else:
        console.print(format_scan_report(report, verbose=verbose))

        if fail_on:
            min_severity = Severity.from_string(fail_on)
            if report.has_severity(min_severity):
                console.print(f"\n[red]FAILED: Found vulnerabilities with severity >= {fail_on}[/red]")
                raise typer.Exit(1)

        if report.has_critical():
            console.print("\n[yellow]Warning: Critical vulnerabilities found![/yellow]")


# Also add scan-deps as a top-level command for convenience
@app.command("scan-deps")
def scan_deps_shortcut(
    path: Optional[str] = typer.Argument(None, help="Directory to scan for dependencies"),
    fail_on: Optional[str] = typer.Option(None, "--fail-on", "-f", help="Fail if severity >= value"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching"),
):
    """Scan dependencies for vulnerabilities (shortcut for 'security scan-deps')."""
    scan_deps(path=path, fail_on=fail_on, verbose=verbose, json_out=json_out, no_cache=no_cache)


# Export for entry point
def run():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
