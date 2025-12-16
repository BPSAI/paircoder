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


@plan_app.command("status")
def plan_status(
    plan_id: str = typer.Argument("current", help="Plan ID or 'current' for active plan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show individual task list"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show plan status with sprint/task breakdown."""
    paircoder_dir = find_paircoder_dir()
    state_manager = get_state_manager()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    # If "current", get from state
    if plan_id == "current":
        plan_id = state_manager.get_active_plan_id()
        if not plan_id:
            console.print("[yellow]No active plan. Specify a plan ID.[/yellow]")
            console.print("[dim]List plans: bpsai-pair plan list[/dim]")
            raise typer.Exit(1)

    # Load plan
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Load tasks for this plan (filter by plan_id in frontmatter)
    tasks = task_parser.get_tasks_for_plan(plan.id)

    # Calculate task counts
    task_counts = {"pending": 0, "in_progress": 0, "done": 0, "blocked": 0, "cancelled": 0}
    for task in tasks:
        status_key = task.status.value
        if status_key in task_counts:
            task_counts[status_key] += 1

    total_tasks = len(tasks)
    done_count = task_counts["done"]
    progress_pct = int((done_count / total_tasks) * 100) if total_tasks > 0 else 0

    # Group tasks by sprint
    sprints_tasks = {}
    no_sprint = []
    for task in tasks:
        if task.sprint:
            if task.sprint not in sprints_tasks:
                sprints_tasks[task.sprint] = []
            sprints_tasks[task.sprint].append(task)
        else:
            no_sprint.append(task)

    # Find blockers with reasons
    blockers = []
    for task in tasks:
        if task.status == TaskStatus.BLOCKED:
            if task.depends_on:
                reason = f"depends on {', '.join(task.depends_on)}"
            else:
                reason = "blocked"
            blockers.append((task.id, task.title, reason))

    # JSON output
    if json_out:
        data = {
            "plan_id": plan.id,
            "title": plan.title,
            "status": plan.status.value,
            "type": plan.type.value,
            "goals": plan.goals,
            "progress_percent": progress_pct,
            "task_counts": task_counts,
            "total_tasks": total_tasks,
            "sprints": {
                sprint_id: {
                    "tasks": len(tasks_list),
                    "done": sum(1 for t in tasks_list if t.status == TaskStatus.DONE),
                }
                for sprint_id, tasks_list in sprints_tasks.items()
            },
            "blockers": [{"id": b[0], "title": b[1], "reason": b[2]} for b in blockers],
        }
        console.print(json.dumps(data, indent=2))
        return

    # Rich output
    console.print(f"\n[bold]Plan:[/bold] {plan.id}")
    console.print(f"[bold]Title:[/bold] {plan.title}")
    console.print(f"[bold]Status:[/bold] {plan.status_emoji} {plan.status.value}")
    console.print(f"[bold]Type:[/bold] {plan.type.value}")

    # Goals
    if plan.goals:
        console.print("\n[bold]Goals:[/bold]")
        for goal in plan.goals:
            check = "✓" if "complete" in goal.lower() or "done" in goal.lower() else "○"
            console.print(f"  {check} {goal}")

    # Sprint progress
    if sprints_tasks:
        console.print("\n[bold]Sprint Progress:[/bold]")
        for sprint_id in sorted(sprints_tasks.keys()):
            sprint_tasks = sprints_tasks[sprint_id]
            sprint_total = len(sprint_tasks)
            sprint_done = sum(1 for t in sprint_tasks if t.status == TaskStatus.DONE)
            sprint_pct = int((sprint_done / sprint_total) * 100) if sprint_total > 0 else 0

            # Progress bar (16 chars)
            filled = int(sprint_pct / 6.25)  # 16 blocks = 100%
            bar = "█" * filled + "░" * (16 - filled)
            console.print(f"  {sprint_id} [{bar}] {sprint_pct:3d}%  ({sprint_done}/{sprint_total} tasks)")

    # Overall task status
    console.print("\n[bold]Task Status:[/bold]")
    console.print(f"  ✓ Done:        {task_counts['done']}")
    console.print(f"  ● In Progress: {task_counts['in_progress']}")
    console.print(f"  ○ Pending:     {task_counts['pending']}")
    console.print(f"  ⊘ Blocked:     {task_counts['blocked']}")
    if task_counts['cancelled'] > 0:
        console.print(f"  ✗ Cancelled:   {task_counts['cancelled']}")

    # Overall progress
    filled = int(progress_pct / 6.25)
    bar = "█" * filled + "░" * (16 - filled)
    console.print(f"\n[bold]Overall:[/bold] [{bar}] {progress_pct}% ({done_count}/{total_tasks} tasks)")

    # Blockers
    if blockers:
        console.print("\n[bold]Blockers:[/bold]")
        for task_id, title, reason in blockers:
            console.print(f"  [red]⊘[/red] {task_id}: {title}")
            console.print(f"    [dim]→ {reason}[/dim]")

    # Verbose: show all tasks
    if verbose:
        console.print("\n[bold]All Tasks:[/bold]")
        table = Table(show_header=True)
        table.add_column("Status", width=3)
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Sprint")
        table.add_column("Priority")

        for task in sorted(tasks, key=lambda t: (t.sprint or "", t.priority, t.id)):
            table.add_row(
                task.status_emoji,
                task.id,
                task.title[:40] + "..." if len(task.title) > 40 else task.title,
                task.sprint or "-",
                task.priority,
            )

        console.print(table)

    console.print("")


@plan_app.command("sync-trello")
def plan_sync_trello(
    plan_id: str = typer.Argument(..., help="Plan ID to sync"),
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Target Trello board ID"),
    create_lists: bool = typer.Option(True, "--create-lists/--no-create-lists", help="Create sprint lists if missing"),
    link_cards: bool = typer.Option(True, "--link/--no-link", help="Store card IDs in task files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without making changes"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Sync plan tasks to Trello board as cards."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    # Load plan
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Load tasks
    tasks = task_parser.get_tasks_for_plan(plan_id)
    if not tasks:
        console.print(f"[yellow]No tasks found for plan: {plan_id}[/yellow]")
        raise typer.Exit(1)

    results = {
        "plan_id": plan_id,
        "board_id": board_id,
        "lists_created": [],
        "cards_created": [],
        "cards_updated": [],
        "errors": [],
        "dry_run": dry_run,
    }

    # Group tasks by sprint
    sprints_tasks = {}
    for task in tasks:
        sprint_name = task.sprint or "Backlog"
        if sprint_name not in sprints_tasks:
            sprints_tasks[sprint_name] = []
        sprints_tasks[sprint_name].append(task)

    if dry_run:
        # Preview mode
        console.print(f"\n[bold]Would sync plan:[/bold] {plan_id}")
        console.print(f"[bold]Target board:[/bold] {board_id or '(not specified)'}")
        console.print(f"\n[bold]Tasks to sync:[/bold]")

        for sprint_name, sprint_tasks in sorted(sprints_tasks.items()):
            console.print(f"\n  [cyan]{sprint_name}[/cyan]:")
            for task in sprint_tasks:
                console.print(f"    [{task.id}] {task.title}")
                results["cards_created"].append({
                    "task_id": task.id,
                    "title": task.title,
                    "sprint": sprint_name,
                })

        console.print(f"\n[dim]Total: {len(tasks)} tasks in {len(sprints_tasks)} lists[/dim]")

        if json_out:
            console.print(json.dumps(results, indent=2))
        return

    # Check for Trello connection
    if not board_id:
        console.print("[red]Board ID required. Use --board <board-id>[/red]")
        console.print("[dim]List boards: bpsai-pair trello boards[/dim]")
        raise typer.Exit(1)

    try:
        from ..trello.auth import load_token
        from ..trello.client import TrelloService

        token_data = load_token()
        if not token_data:
            console.print("[red]Not connected to Trello. Run 'bpsai-pair trello connect' first.[/red]")
            raise typer.Exit(1)

        service = TrelloService(
            api_key=token_data["api_key"],
            token=token_data["token"]
        )

        # Set board
        service.set_board(board_id)
        results["board_id"] = board_id

        console.print(f"\n[bold]Syncing plan:[/bold] {plan_id}")
        console.print(f"[bold]Target board:[/bold] {service.board.name}")

        # Process each sprint
        for sprint_name, sprint_tasks in sorted(sprints_tasks.items()):
            console.print(f"\n  [cyan]{sprint_name}[/cyan]:")

            # Get or create list
            board_lists = service.get_board_lists()
            if sprint_name not in board_lists:
                if create_lists:
                    service.board.add_list(sprint_name)
                    service.lists = {lst.name: lst for lst in service.board.all_lists()}
                    results["lists_created"].append(sprint_name)
                    console.print(f"    [green]+ Created list[/green]")
                else:
                    results["errors"].append(f"List not found: {sprint_name}")
                    console.print(f"    [red]✗ List not found[/red]")
                    continue

            target_list = service.lists.get(sprint_name)
            if not target_list:
                continue

            # Create cards for tasks
            for task in sprint_tasks:
                try:
                    # Check if card already exists
                    existing_cards = target_list.list_cards()
                    existing = None
                    for card in existing_cards:
                        if f"[{task.id}]" in card.name:
                            existing = card
                            break

                    # Card description
                    desc = f"""## Objective
{getattr(task, 'objective', None) or task.title}

## Details
- **Priority:** {task.priority}
- **Complexity:** {task.complexity}
- **Sprint:** {task.sprint or 'N/A'}

---
*Synced from PairCoder*
"""

                    if existing:
                        # Update existing card
                        existing.set_description(desc)
                        results["cards_updated"].append({
                            "task_id": task.id,
                            "card_id": existing.id,
                        })
                        console.print(f"    [yellow]↻[/yellow] {task.id}: {task.title}")
                    else:
                        # Create new card
                        card_name = f"[{task.id}] {task.title}"
                        card = target_list.add_card(card_name, desc)
                        results["cards_created"].append({
                            "task_id": task.id,
                            "card_id": card.id,
                        })
                        console.print(f"    [green]+[/green] {task.id}: {task.title}")

                        # Update task file with card ID if requested
                        if link_cards:
                            _update_task_with_card_id(task, card.id, task_parser)

                except Exception as e:
                    error_msg = f"Failed to create card for {task.id}: {str(e)}"
                    results["errors"].append(error_msg)
                    console.print(f"    [red]✗[/red] {task.id}: {str(e)}")

        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Lists created: {len(results['lists_created'])}")
        console.print(f"  Cards created: {len(results['cards_created'])}")
        console.print(f"  Cards updated: {len(results['cards_updated'])}")
        if results["errors"]:
            console.print(f"  [red]Errors: {len(results['errors'])}[/red]")

        if json_out:
            console.print(json.dumps(results, indent=2))

    except ImportError:
        console.print("[red]py-trello not installed. Install with: pip install 'bpsai-pair[trello]'[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _update_task_with_card_id(task: Task, card_id: str, task_parser: TaskParser) -> bool:
    """Update task file with Trello card ID."""
    try:
        # Find task file
        task_file = task_parser._find_task_file(task.id)
        if not task_file:
            return False

        content = task_file.read_text()

        # Insert trello_card_id into frontmatter
        if "trello_card_id:" not in content:
            # Find end of frontmatter
            lines = content.split("\n")
            new_lines = []
            in_frontmatter = False
            inserted = False

            for line in lines:
                if line.strip() == "---":
                    if in_frontmatter and not inserted:
                        # Insert before closing ---
                        new_lines.append(f'trello_card_id: "{card_id}"')
                        inserted = True
                    in_frontmatter = not in_frontmatter
                new_lines.append(line)

            task_file.write_text("\n".join(new_lines))
            return True

        return False
    except Exception:
        return False


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
def task_next(
    start: bool = typer.Option(False, "--start", "-s", help="Automatically start the next task"),
):
    """Show the next task to work on.

    Use --start to automatically set the task to in_progress.
    """
    state_manager = get_state_manager()
    task = state_manager.get_next_task()

    if not task:
        console.print("[dim]No tasks available. Create a plan first![/dim]")
        return

    # If --start flag, auto-assign the task
    if start and task.status != TaskStatus.IN_PROGRESS:
        from .auto_assign import auto_assign_next

        paircoder_dir = find_paircoder_dir()
        task = auto_assign_next(paircoder_dir, plan_id=task.plan_id)

        if task:
            console.print(f"[green]✓ Auto-started task:[/green] {task.id}")
        else:
            console.print("[red]Failed to auto-start task[/red]")
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

    if task.status != TaskStatus.IN_PROGRESS:
        console.print(f"\n[dim]To start: bpsai-pair task next --start[/dim]")
        console.print(f"[dim]Or: bpsai-pair task update {task.id} --status in_progress[/dim]")


@task_app.command("auto-next")
def task_auto_next(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to filter tasks"),
):
    """Automatically assign and start the next pending task.

    This command finds the highest-priority pending task and sets it to in_progress.
    Tasks are prioritized by: priority (P0 > P1 > P2), then complexity (lower first).

    Example:
        # Auto-start next task from any plan
        bpsai-pair task auto-next

        # Auto-start next task from specific plan
        bpsai-pair task auto-next --plan plan-2025-12-sprint-13-autonomy
    """
    from .auto_assign import auto_assign_next

    paircoder_dir = find_paircoder_dir()
    task = auto_assign_next(paircoder_dir, plan_id=plan_id)

    if not task:
        console.print("[yellow]No pending tasks available[/yellow]")
        return

    console.print(f"[green]✓ Auto-assigned:[/green] {task.id}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority} | Complexity: {task.complexity}")
    console.print(f"[cyan]Status:[/cyan] {task.status_emoji} {task.status.value}")


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
# INTENT DETECTION COMMANDS
# ============================================================================

intent_app = typer.Typer(
    help="Intent detection and planning mode commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@intent_app.command("detect")
def intent_detect(
    text: str = typer.Argument(..., help="Text to analyze for intent"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Detect work intent from text."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    matches = detector.detect_all(text)

    if json_out:
        import json as json_module
        output = [{
            "intent": m.intent.value,
            "confidence": m.confidence,
            "suggested_flow": m.suggested_flow,
            "triggers": m.triggers,
        } for m in matches]
        console.print(json_module.dumps(output, indent=2))
        return

    if not matches:
        console.print("[dim]No clear intent detected[/dim]")
        return

    console.print("[bold]Detected Intents:[/bold]\n")
    for match in matches:
        confidence_color = "green" if match.confidence >= 0.8 else "yellow" if match.confidence >= 0.6 else "dim"
        console.print(f"[{confidence_color}]{match.intent.value}[/{confidence_color}] ({match.confidence:.0%})")
        if match.suggested_flow:
            console.print(f"  Suggested flow: {match.suggested_flow}")
        if match.triggers:
            console.print(f"  Triggers: {', '.join(match.triggers[:3])}")
        console.print()


@intent_app.command("should-plan")
def intent_should_plan(
    text: str = typer.Argument(..., help="Text to analyze"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Check if text should trigger planning mode."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    should_plan, match = detector.should_enter_planning_mode(text)

    if json_out:
        import json as json_module
        output = {
            "should_plan": should_plan,
            "intent": match.intent.value if match else None,
            "confidence": match.confidence if match else 0,
            "suggested_flow": match.suggested_flow if match else None,
        }
        console.print(json_module.dumps(output, indent=2))
        return

    if should_plan and match:
        console.print(f"[green]YES - Planning mode recommended[/green]")
        console.print(f"  Intent: {match.intent.value} ({match.confidence:.0%})")
        console.print(f"  Suggested flow: {match.suggested_flow}")
    else:
        console.print("[dim]No - Direct action is fine[/dim]")


@intent_app.command("suggest-flow")
def intent_suggest_flow(
    text: str = typer.Argument(..., help="Text to analyze"),
):
    """Suggest appropriate flow for text."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    flow = detector.get_flow_suggestion(text)

    if flow:
        console.print(f"[green]Suggested flow: {flow}[/green]")
        console.print(f"\n[dim]Run: bpsai-pair flow run {flow}[/dim]")
    else:
        console.print("[dim]No specific flow suggested for this request.[/dim]")


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
