"""
CLI Commands for Planning System

Implements the following commands:
- bpsai-pair plan new|list|show|tasks
- bpsai-pair task list|show|update

To integrate into main CLI, add these command groups to cli.py
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from .models import Plan, Task, TaskStatus, PlanStatus, PlanType, Sprint
from .parser import PlanParser, TaskParser
from .state import StateManager


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

@click.group(name="plan")
def plan_group():
    """Manage plans (goals, tasks, sprints)."""
    pass


@plan_group.command(name="new")
@click.argument("slug")
@click.option("--type", "-t", "plan_type", 
              type=click.Choice(["feature", "bugfix", "refactor", "chore"]),
              default="feature",
              help="Type of plan")
@click.option("--title", "-T", default=None, help="Plan title (defaults to slug)")
@click.option("--flow", "-f", default="design-plan-implement", help="Flow to associate")
@click.option("--goal", "-g", multiple=True, help="Plan goals (can specify multiple)")
def plan_new(slug: str, plan_type: str, title: Optional[str], flow: str, goal: tuple):
    """
    Create a new plan.
    
    SLUG is a short identifier like 'workspace-filter' or 'fix-login-bug'
    """
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    
    # Generate plan ID
    date_str = datetime.now().strftime("%Y-%m")
    plan_id = f"plan-{date_str}-{slug}"
    
    # Check if plan already exists
    existing = plan_parser.get_plan_by_id(plan_id)
    if existing:
        click.echo(f"❌ Plan already exists: {plan_id}", err=True)
        raise SystemExit(1)
    
    # Create plan
    plan = Plan(
        id=plan_id,
        title=title or slug.replace("-", " ").title(),
        type=PlanType(plan_type),
        status=PlanStatus.PLANNED,
        created_at=datetime.now(),
        flows=[flow],
        goals=list(goal) if goal else [],
    )
    
    # Save plan
    plan_path = plan_parser.save(plan)
    
    click.echo(f"✅ Created plan: {plan_id}")
    click.echo(f"   Path: {plan_path}")
    click.echo(f"   Type: {plan_type}")
    click.echo(f"   Flow: {flow}")
    
    if goal:
        click.echo("   Goals:")
        for g in goal:
            click.echo(f"     - {g}")
    
    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  1. Add tasks: bpsai-pair plan add-task {plan_id}")
    click.echo(f"  2. Or run the flow: bpsai-pair flow run {flow} --plan {plan_id}")


@plan_group.command(name="list")
@click.option("--status", "-s", 
              type=click.Choice(["planned", "in_progress", "complete", "archived"]),
              default=None,
              help="Filter by status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def plan_list(status: Optional[str], as_json: bool):
    """List all plans."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    
    plans = plan_parser.parse_all()
    
    # Filter by status if specified
    if status:
        plans = [p for p in plans if p.status.value == status]
    
    if as_json:
        import json
        data = [p.to_dict() for p in plans]
        click.echo(json.dumps(data, indent=2, default=str))
        return
    
    if not plans:
        click.echo("No plans found.")
        return
    
    click.echo(f"Found {len(plans)} plan(s):\n")
    
    for plan in plans:
        status_emoji = plan.status_emoji
        click.echo(f"{status_emoji} {plan.id}")
        click.echo(f"   Title: {plan.title}")
        click.echo(f"   Type: {plan.type.value} | Status: {plan.status.value}")
        click.echo(f"   Tasks: {len(plan.tasks)}")
        click.echo("")


@plan_group.command(name="show")
@click.argument("plan_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def plan_show(plan_id: str, as_json: bool):
    """Show details of a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")
    
    plan = plan_parser.get_plan_by_id(plan_id)
    
    if not plan:
        click.echo(f"❌ Plan not found: {plan_id}", err=True)
        raise SystemExit(1)
    
    if as_json:
        import json
        click.echo(json.dumps(plan.to_dict(), indent=2, default=str))
        return
    
    click.echo(f"{plan.status_emoji} {plan.id}")
    click.echo(f"{'=' * 60}")
    click.echo(f"Title: {plan.title}")
    click.echo(f"Type: {plan.type.value}")
    click.echo(f"Status: {plan.status.value}")
    if plan.owner:
        click.echo(f"Owner: {plan.owner}")
    if plan.created_at:
        click.echo(f"Created: {plan.created_at.strftime('%Y-%m-%d')}")
    
    if plan.flows:
        click.echo(f"\nFlows: {', '.join(plan.flows)}")
    
    if plan.goals:
        click.echo("\nGoals:")
        for goal in plan.goals:
            click.echo(f"  • {goal}")
    
    if plan.sprints:
        click.echo("\nSprints:")
        for sprint in plan.sprints:
            click.echo(f"  [{sprint.id}] {sprint.title}")
            if sprint.goal:
                click.echo(f"       Goal: {sprint.goal}")
            click.echo(f"       Tasks: {len(sprint.task_ids)}")
    
    # Load actual task files for status
    tasks = task_parser.parse_all(plan.slug)
    if tasks:
        click.echo("\nTasks:")
        for task in tasks:
            click.echo(f"  {task.status_emoji} {task.id}: {task.title}")
            click.echo(f"       Priority: {task.priority} | Complexity: {task.complexity}")


@plan_group.command(name="tasks")
@click.argument("plan_id")
@click.option("--status", "-s",
              type=click.Choice(["pending", "in_progress", "done", "blocked"]),
              default=None,
              help="Filter by status")
def plan_tasks(plan_id: str, status: Optional[str]):
    """List tasks for a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")
    
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        click.echo(f"❌ Plan not found: {plan_id}", err=True)
        raise SystemExit(1)
    
    tasks = task_parser.parse_all(plan.slug)
    
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    
    if not tasks:
        click.echo(f"No tasks found for plan: {plan_id}")
        return
    
    click.echo(f"Tasks for {plan_id}:\n")
    
    # Group by sprint if available
    sprint_tasks = {}
    no_sprint = []
    
    for task in tasks:
        if task.sprint:
            if task.sprint not in sprint_tasks:
                sprint_tasks[task.sprint] = []
            sprint_tasks[task.sprint].append(task)
        else:
            no_sprint.append(task)
    
    def print_task(task: Task):
        click.echo(f"  {task.status_emoji} {task.id}: {task.title}")
        click.echo(f"       P: {task.priority} | C: {task.complexity} | {task.type}")
    
    for sprint_id, sprint_task_list in sprint_tasks.items():
        sprint = plan.get_sprint_by_id(sprint_id)
        sprint_title = sprint.title if sprint else sprint_id
        click.echo(f"[{sprint_id}] {sprint_title}")
        for task in sprint_task_list:
            print_task(task)
        click.echo("")
    
    if no_sprint:
        click.echo("[No Sprint]")
        for task in no_sprint:
            print_task(task)


@plan_group.command(name="add-task")
@click.argument("plan_id")
@click.option("--id", "task_id", required=True, help="Task ID (e.g., TASK-007)")
@click.option("--title", "-t", required=True, help="Task title")
@click.option("--type", "task_type", default="feature", help="Task type")
@click.option("--priority", "-p", default="P1", help="Priority (P0, P1, P2)")
@click.option("--complexity", "-c", type=int, default=50, help="Complexity (0-100)")
@click.option("--sprint", "-s", default=None, help="Sprint ID")
def plan_add_task(plan_id: str, task_id: str, title: str, task_type: str, 
                  priority: str, complexity: int, sprint: Optional[str]):
    """Add a task to a plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")
    
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        click.echo(f"❌ Plan not found: {plan_id}", err=True)
        raise SystemExit(1)
    
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
    
    click.echo(f"✅ Created task: {task_id}")
    click.echo(f"   Path: {task_path}")
    click.echo(f"   Plan: {plan_id}")


# ============================================================================
# TASK COMMANDS
# ============================================================================

@click.group(name="task")
def task_group():
    """Manage tasks."""
    pass


@task_group.command(name="list")
@click.option("--plan", "-p", "plan_id", default=None, help="Filter by plan ID")
@click.option("--status", "-s",
              type=click.Choice(["pending", "in_progress", "done", "blocked"]),
              default=None,
              help="Filter by status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def task_list(plan_id: Optional[str], status: Optional[str], as_json: bool):
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
    
    if as_json:
        import json
        data = [t.to_dict() for t in tasks]
        click.echo(json.dumps(data, indent=2))
        return
    
    if not tasks:
        click.echo("No tasks found.")
        return
    
    click.echo(f"Found {len(tasks)} task(s):\n")
    
    for task in tasks:
        click.echo(f"{task.status_emoji} {task.id}: {task.title}")
        click.echo(f"   Plan: {task.plan_id}")
        click.echo(f"   Priority: {task.priority} | Complexity: {task.complexity}")
        click.echo("")


@task_group.command(name="show")
@click.argument("task_id")
@click.option("--plan", "-p", "plan_id", default=None, help="Plan ID to narrow search")
def task_show(task_id: str, plan_id: Optional[str]):
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
        click.echo(f"❌ Task not found: {task_id}", err=True)
        raise SystemExit(1)
    
    click.echo(f"{task.status_emoji} {task.id}")
    click.echo(f"{'=' * 60}")
    click.echo(f"Title: {task.title}")
    click.echo(f"Plan: {task.plan_id}")
    click.echo(f"Type: {task.type}")
    click.echo(f"Priority: {task.priority}")
    click.echo(f"Complexity: {task.complexity}")
    click.echo(f"Status: {task.status.value}")
    
    if task.sprint:
        click.echo(f"Sprint: {task.sprint}")
    
    if task.tags:
        click.echo(f"Tags: {', '.join(task.tags)}")
    
    if task.body:
        click.echo(f"\n{'-' * 60}")
        click.echo(task.body)


@task_group.command(name="update")
@click.argument("task_id")
@click.option("--status", "-s",
              type=click.Choice(["pending", "in_progress", "done", "blocked", "cancelled"]),
              required=True,
              help="New status")
@click.option("--plan", "-p", "plan_id", default=None, help="Plan ID to narrow search")
def task_update(task_id: str, status: str, plan_id: Optional[str]):
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
        status_emoji = TaskStatus(status).value
        emoji_map = {
            "pending": "⏳",
            "in_progress": "🔄",
            "done": "✅",
            "blocked": "🚫",
            "cancelled": "❌",
        }
        click.echo(f"{emoji_map.get(status, '✓')} Updated {task_id} → {status}")
    else:
        click.echo(f"❌ Failed to update task: {task_id}", err=True)
        raise SystemExit(1)


@task_group.command(name="next")
def task_next():
    """Show the next task to work on."""
    state_manager = get_state_manager()
    task = state_manager.get_next_task()
    
    if not task:
        click.echo("No tasks available. Create a plan first!")
        return
    
    click.echo(f"Next task: {task.status_emoji} {task.id}")
    click.echo(f"Title: {task.title}")
    click.echo(f"Priority: {task.priority} | Complexity: {task.complexity}")
    
    if task.body:
        # Show first section of body
        lines = task.body.split("\n")
        preview = "\n".join(lines[:10])
        click.echo(f"\n{preview}")
        if len(lines) > 10:
            click.echo(f"\n... ({len(lines) - 10} more lines)")
    
    click.echo(f"\nTo start: bpsai-pair task update {task.id} --status in_progress")


# ============================================================================
# STATUS COMMAND (enhanced)
# ============================================================================

def planning_status():
    """
    Get planning status for the enhanced status command.
    
    Call this from the main status command to include planning info.
    """
    state_manager = get_state_manager()
    return state_manager.format_status_report()


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def register_commands(cli_group):
    """
    Register plan and task commands with main CLI.
    
    Usage in cli.py:
        from .planning.cli_commands import register_commands
        register_commands(cli)
    """
    cli_group.add_command(plan_group)
    cli_group.add_command(task_group)
