"""
CLI Commands for Planning System (Typer version)

Implements the following commands:
- bpsai-pair plan new|list|show|tasks|add-task
- bpsai-pair task list|show|update|next

To integrate into main CLI:
    from .planning.cli_commands import plan_app, task_app
    app.add_typer(plan_app, name="plan")
    app.add_typer(task_app, name="task")
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json

import typer
from rich.console import Console
from rich.table import Table

from .models import Plan, Task, TaskStatus, PlanStatus, PlanType, Sprint
from .parser import PlanParser, TaskParser
from .state import StateManager

# Import task lifecycle management
try:
    from ..tasks import TaskArchiver, TaskLifecycle, ChangelogGenerator, TaskState
except ImportError:
    TaskArchiver = None
    TaskLifecycle = None
    ChangelogGenerator = None
    TaskState = None


console = Console()


def find_paircoder_dir() -> Path:
    """Find .paircoder directory in current or parent directories."""
    current = Path.cwd()

    # Check current and parent directories
    for _ in range(10):  # Limit search depth
        paircoder_dir = current / ".paircoder"
        if paircoder_dir.exists():
            return paircoder_dir
        if current.parent == current:
            break
        current = current.parent

    # Default to current directory
    return Path.cwd() / ".paircoder"


def get_state_manager() -> StateManager:
    """Get a StateManager instance for the current project."""
    return StateManager(find_paircoder_dir())


# ============================================================================
# PLAN COMMANDS
# ============================================================================

plan_app = typer.Typer(
    help="Manage plans (goals, tasks, sprints)",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@plan_app.command("new")
def plan_new(
    slug: str = typer.Argument(..., help="Short identifier (e.g., 'workspace-filter')"),
    plan_type: str = typer.Option(
        "feature", "--type", "-t",
        help="Type: feature|bugfix|refactor|chore"
    ),
    title: Optional[str] = typer.Option(None, "--title", "-T", help="Plan title"),
    flow: str = typer.Option("design-plan-implement", "--flow", "-f", help="Associated flow"),
    goal: Optional[List[str]] = typer.Option(None, "--goal", "-g", help="Plan goals (repeatable)"),
):
    """Create a new plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")

    # Generate plan ID
    date_str = datetime.now().strftime("%Y-%m")
    plan_id = f"plan-{date_str}-{slug}"

    # Check if plan already exists
    existing = plan_parser.get_plan_by_id(plan_id)
    if existing:
        console.print(f"[red]Plan already exists: {plan_id}[/red]")
        raise typer.Exit(1)

    # Validate plan type
    try:
        ptype = PlanType(plan_type)
    except ValueError:
        console.print(f"[red]Invalid plan type: {plan_type}[/red]")
        console.print("Valid types: feature, bugfix, refactor, chore")
        raise typer.Exit(1)

    # Create plan
    plan = Plan(
        id=plan_id,
        title=title or slug.replace("-", " ").title(),
        type=ptype,
        status=PlanStatus.PLANNED,
        created_at=datetime.now(),
        flows=[flow],
        goals=list(goal) if goal else [],
    )

    # Save plan
    plan_path = plan_parser.save(plan)

    console.print(f"[green]Created plan:[/green] {plan_id}")
    console.print(f"  Path: {plan_path}")
    console.print(f"  Type: {plan_type}")
    console.print(f"  Flow: {flow}")

    if goal:
        console.print("  Goals:")
        for g in goal:
            console.print(f"    - {g}")

    console.print("")
    console.print("[dim]Next steps:[/dim]")
    console.print(f"  1. Add tasks: bpsai-pair plan add-task {plan_id}")
    console.print(f"  2. Or run flow: bpsai-pair flow run {flow} --plan {plan_id}")


@plan_app.command("list")
def plan_list(
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: planned|in_progress|complete|archived"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all plans."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")

    plans = plan_parser.parse_all()

    # Filter by status if specified
    if status:
        plans = [p for p in plans if p.status.value == status]

    if json_out:
        data = [p.to_dict() for p in plans]
        console.print(json.dumps(data, indent=2, default=str))
        return

    if not plans:
        console.print("[dim]No plans found.[/dim]")
        return

    table = Table(title=f"Plans ({len(plans)})")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Tasks", justify="right")

    for plan in plans:
        table.add_row(
            plan.id,
            plan.title,
            plan.type.value,
            f"{plan.status_emoji} {plan.status.value}",
            str(len(plan.tasks)),
        )

    console.print(table)


@plan_app.command("show")
def plan_show(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)

    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    if json_out:
        console.print(json.dumps(plan.to_dict(), indent=2, default=str))
        return

    console.print(f"[bold]{plan.status_emoji} {plan.id}[/bold]")
    console.print(f"{'=' * 60}")
    console.print(f"[cyan]Title:[/cyan] {plan.title}")
    console.print(f"[cyan]Type:[/cyan] {plan.type.value}")
    console.print(f"[cyan]Status:[/cyan] {plan.status.value}")

    if plan.owner:
        console.print(f"[cyan]Owner:[/cyan] {plan.owner}")
    if plan.created_at:
        console.print(f"[cyan]Created:[/cyan] {plan.created_at.strftime('%Y-%m-%d')}")

    if plan.flows:
        console.print(f"\n[cyan]Flows:[/cyan] {', '.join(plan.flows)}")

    if plan.goals:
        console.print("\n[cyan]Goals:[/cyan]")
        for goal in plan.goals:
            console.print(f"  - {goal}")

    if plan.sprints:
        console.print("\n[cyan]Sprints:[/cyan]")
        for sprint in plan.sprints:
            console.print(f"  [{sprint.id}] {sprint.title}")
            if sprint.goal:
                console.print(f"       Goal: {sprint.goal}")
            console.print(f"       Tasks: {len(sprint.task_ids)}")

    # Load actual task files for status
    tasks = task_parser.parse_all(plan.slug)
    if tasks:
        console.print("\n[cyan]Tasks:[/cyan]")
        for task in tasks:
            console.print(f"  {task.status_emoji} {task.id}: {task.title}")
            console.print(f"       Priority: {task.priority} | Complexity: {task.complexity}")


@plan_app.command("tasks")
def plan_tasks(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: pending|in_progress|done|blocked"
    ),
):
    """List tasks for a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    tasks = task_parser.parse_all(plan.slug)

    if status:
        tasks = [t for t in tasks if t.status.value == status]

    if not tasks:
        console.print(f"[dim]No tasks found for plan: {plan_id}[/dim]")
        return

    table = Table(title=f"Tasks for {plan_id}")
    table.add_column("Status", width=3)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Complexity", justify="right")
    table.add_column("Sprint")

    for task in tasks:
        table.add_row(
            task.status_emoji,
            task.id,
            task.title,
            task.priority,
            str(task.complexity),
            task.sprint or "-",
        )

    console.print(table)


@plan_app.command("add-task")
def plan_add_task(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    task_id: str = typer.Option(..., "--id", help="Task ID (e.g., TASK-007)"),
    title: str = typer.Option(..., "--title", "-t", help="Task title"),
    task_type: str = typer.Option("feature", "--type", help="Task type"),
    priority: str = typer.Option("P1", "--priority", "-p", help="Priority (P0, P1, P2)"),
    complexity: int = typer.Option(50, "--complexity", "-c", help="Complexity (0-100)"),
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Sprint ID"),
):
    """Add a task to a plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Create task
    task = Task(
        id=task_id,
        title=title,
        plan_id=plan.id,
        type=task_type,
        priority=priority,
        complexity=complexity,
        status=TaskStatus.PENDING,
        sprint=sprint,
    )

    # Save task
    task_path = task_parser.save(task, plan.slug)

    console.print(f"[green]Created task:[/green] {task_id}")
    console.print(f"  Path: {task_path}")
    console.print(f"  Plan: {plan_id}")


# ============================================================================
# TASK COMMANDS
# ============================================================================

task_app = typer.Typer(
    help="Manage tasks",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@task_app.command("list")
def task_list(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Filter by plan ID"),
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: pending|in_progress|done|blocked"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List tasks."""
    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    # Determine plan slug
    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    tasks = task_parser.parse_all(plan_slug)

    if status:
        tasks = [t for t in tasks if t.status.value == status]

    if json_out:
        data = [t.to_dict() for t in tasks]
        console.print(json.dumps(data, indent=2))
        return

    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=f"Tasks ({len(tasks)})")
    table.add_column("Status", width=3)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Plan")
    table.add_column("Priority")
    table.add_column("Complexity", justify="right")

    for task in tasks:
        table.add_row(
            task.status_emoji,
            task.id,
            task.title[:40] + "..." if len(task.title) > 40 else task.title,
            task.plan_id or "-",
            task.priority,
            str(task.complexity),
        )

    console.print(table)


@task_app.command("show")
def task_show(
    task_id: str = typer.Argument(..., help="Task ID"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to narrow search"),
):
    """Show details of a specific task."""
    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    task = task_parser.get_task_by_id(task_id, plan_slug)

    if not task:
        console.print(f"[red]Task not found: {task_id}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]{task.status_emoji} {task.id}[/bold]")
    console.print(f"{'=' * 60}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Plan:[/cyan] {task.plan_id}")
    console.print(f"[cyan]Type:[/cyan] {task.type}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority}")
    console.print(f"[cyan]Complexity:[/cyan] {task.complexity}")
    console.print(f"[cyan]Status:[/cyan] {task.status.value}")

    if task.sprint:
        console.print(f"[cyan]Sprint:[/cyan] {task.sprint}")

    if task.tags:
        console.print(f"[cyan]Tags:[/cyan] {', '.join(task.tags)}")

    if task.body:
        console.print(f"\n{'-' * 60}")
        console.print(task.body)


@task_app.command("update")
def task_update(
    task_id: str = typer.Argument(..., help="Task ID"),
    status: str = typer.Option(
        ..., "--status", "-s",
        help="New status: pending|in_progress|done|blocked|cancelled"
    ),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to narrow search"),
):
    """Update a task's status."""
    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    success = task_parser.update_status(task_id, status, plan_slug)

    if success:
        emoji_map = {
            "pending": "\u23f3",
            "in_progress": "\U0001f504",
            "done": "\u2705",
            "blocked": "\U0001f6ab",
            "cancelled": "\u274c",
        }
        console.print(f"{emoji_map.get(status, '\u2713')} Updated {task_id} -> {status}")
    else:
        console.print(f"[red]Failed to update task: {task_id}[/red]")
        raise typer.Exit(1)


@task_app.command("next")
def task_next():
    """Show the next task to work on."""
    state_manager = get_state_manager()
    task = state_manager.get_next_task()

    if not task:
        console.print("[dim]No tasks available. Create a plan first![/dim]")
        return

    console.print(f"[bold]Next task:[/bold] {task.status_emoji} {task.id}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority} | Complexity: {task.complexity}")

    if task.body:
        # Show first section of body
        lines = task.body.split("\n")
        preview = "\n".join(lines[:10])
        console.print(f"\n{preview}")
        if len(lines) > 10:
            console.print(f"\n[dim]... ({len(lines) - 10} more lines)[/dim]")

    console.print(f"\n[dim]To start: bpsai-pair task update {task.id} --status in_progress[/dim]")


@task_app.command("archive")
def task_archive(
    task_ids: Optional[List[str]] = typer.Argument(None, help="Task IDs to archive"),
    completed: bool = typer.Option(False, "--completed", help="Archive all completed tasks"),
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Archive tasks from sprint(s), comma-separated"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version for changelog entry"),
    no_changelog: bool = typer.Option(False, "--no-changelog", help="Skip changelog update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be archived"),
):
    """Archive completed tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        # Try to get from active plan in state
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan:
            plan_id = state.active_plan.replace("plan-", "").split("-", 2)[-1] if "-" in state.active_plan else state.active_plan
        else:
            console.print("[red]No plan specified and no active plan found[/red]")
            raise typer.Exit(1)

    # Normalize plan slug (remove plan- prefix and date)
    plan_slug = plan_id
    if plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)
    lifecycle = TaskLifecycle(paircoder_dir / "tasks")

    # Collect tasks to archive
    tasks_to_archive = []
    plan_dir = paircoder_dir / "tasks" / plan_slug

    if not plan_dir.exists():
        console.print(f"[red]Plan directory not found: {plan_dir}[/red]")
        raise typer.Exit(1)

    if task_ids:
        # Archive specific tasks
        for task_id in task_ids:
            task_file = plan_dir / f"{task_id}.task.md"
            if task_file.exists():
                task = lifecycle.load_task(task_file)
                tasks_to_archive.append(task)
            else:
                console.print(f"[yellow]Task not found: {task_id}[/yellow]")
    elif sprint:
        # Archive by sprint
        sprints = [s.strip() for s in sprint.split(",")]
        tasks_to_archive = lifecycle.get_tasks_by_sprint(plan_dir, sprints)
    elif completed:
        # Archive all completed
        tasks_to_archive = lifecycle.get_tasks_by_status(
            plan_dir, [TaskState.COMPLETED, TaskState.CANCELLED]
        )
    else:
        console.print("[red]Specify --completed, --sprint, or task IDs[/red]")
        raise typer.Exit(1)

    if not tasks_to_archive:
        console.print("[dim]No tasks to archive.[/dim]")
        return

    # Show what will be archived
    if dry_run:
        console.print("[bold]Would archive:[/bold]")
        for task in tasks_to_archive:
            console.print(f"  {task.id}: {task.title} ({task.status.value})")
        console.print(f"\n[dim]Total: {len(tasks_to_archive)} tasks[/dim]")
        return

    # Perform archive
    console.print(f"Archiving {len(tasks_to_archive)} tasks...")
    result = archiver.archive_batch(tasks_to_archive, plan_slug, version)

    for task in result.archived:
        console.print(f"  [green]\u2713[/green] {task.id}: {task.title}")

    for skip in result.skipped:
        console.print(f"  [yellow]\u23f8[/yellow] {skip}")

    for error in result.errors:
        console.print(f"  [red]\u2717[/red] {error}")

    # Update changelog
    if not no_changelog and result.archived and version:
        changelog_path = root_dir / "CHANGELOG.md"
        changelog = ChangelogGenerator(changelog_path)
        changelog.update_changelog(result.archived, version)
        console.print(f"\n[green]Updated CHANGELOG.md with {version}[/green]")

    console.print(f"\n[green]Archived {len(result.archived)} tasks to:[/green]")
    console.print(f"  {result.archive_path}")


@task_app.command("restore")
def task_restore(
    task_id: str = typer.Argument(..., help="Task ID to restore"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
):
    """Restore a task from archive."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan:
            plan_id = state.active_plan

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)

    try:
        restored_path = archiver.restore_task(task_id, plan_slug)
        console.print(f"[green]\u2713 Restored {task_id} to:[/green]")
        console.print(f"  {restored_path}")
    except FileNotFoundError:
        console.print(f"[red]Archived task not found: {task_id}[/red]")
        raise typer.Exit(1)


@task_app.command("list-archived")
def task_list_archived(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List archived tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)
    archived = archiver.list_archived(plan_slug)

    if json_out:
        from dataclasses import asdict
        data = [asdict(t) for t in archived]
        console.print(json.dumps(data, indent=2))
        return

    if not archived:
        console.print("[dim]No archived tasks found.[/dim]")
        return

    table = Table(title=f"Archived Tasks ({len(archived)})")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Sprint")
    table.add_column("Archived At")

    for task in archived:
        table.add_row(
            task.id,
            task.title[:40] + "..." if task.title and len(task.title) > 40 else task.title or "",
            task.sprint or "-",
            task.archived_at[:10] if task.archived_at else "-",
        )

    console.print(table)


@task_app.command("cleanup")
def task_cleanup(
    retention_days: int = typer.Option(90, "--retention", "-r", help="Retention period in days"),
    dry_run: bool = typer.Option(True, "--dry-run/--confirm", help="Dry run or confirm deletion"),
):
    """Clean up old archived tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    archiver = TaskArchiver(root_dir)
    to_remove = archiver.cleanup(retention_days, dry_run)

    if not to_remove:
        console.print(f"[dim]No tasks older than {retention_days} days.[/dim]")
        return

    if dry_run:
        console.print(f"[bold]Would remove ({len(to_remove)} tasks older than {retention_days} days):[/bold]")
        for item in to_remove:
            console.print(f"  {item}")
        console.print("\n[dim]Run with --confirm to delete[/dim]")
    else:
        console.print(f"[green]Removed {len(to_remove)} archived tasks:[/green]")
        for item in to_remove:
            console.print(f"  [red]\u2717[/red] {item}")


@task_app.command("changelog-preview")
def task_changelog_preview(
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Sprint(s) to preview, comma-separated"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    version: str = typer.Option("vX.Y.Z", "--version", "-v", help="Version string"),
):
    """Preview changelog entry for tasks."""
    if TaskArchiver is None or ChangelogGenerator is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan:
            plan_id = state.active_plan

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    lifecycle = TaskLifecycle(paircoder_dir / "tasks")
    plan_dir = paircoder_dir / "tasks" / plan_slug

    if not plan_dir.exists():
        console.print(f"[red]Plan directory not found: {plan_dir}[/red]")
        raise typer.Exit(1)

    # Get tasks
    if sprint:
        sprints = [s.strip() for s in sprint.split(",")]
        tasks = lifecycle.get_tasks_by_sprint(plan_dir, sprints)
    else:
        tasks = lifecycle.get_tasks_by_status(plan_dir, [TaskState.COMPLETED])

    if not tasks:
        console.print("[dim]No completed tasks found.[/dim]")
        return

    # Convert to ArchivedTask format for changelog generator
    from ..tasks.archiver import ArchivedTask
    archived_tasks = [
        ArchivedTask(
            id=t.id,
            title=t.title,
            sprint=t.sprint,
            status=t.status.value,
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
            archived_at="",
            changelog_entry=t.changelog_entry,
            tags=t.tags,
        )
        for t in tasks
    ]

    changelog = ChangelogGenerator(root_dir / "CHANGELOG.md")
    preview = changelog.preview(archived_tasks, version)

    console.print("[bold]Changelog Preview:[/bold]\n")
    console.print(preview)


# ============================================================================
# STATUS COMMAND (enhanced)
# ============================================================================

def planning_status() -> str:
    """
    Get planning status for the enhanced status command.

    Call this from the main status command to include planning info.
    """
    state_manager = get_state_manager()
    return state_manager.format_status_report()
