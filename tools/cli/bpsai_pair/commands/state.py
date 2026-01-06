"""Task state CLI commands.

Location: tools/cli/bpsai_pair/commands/state.py
"""
import typer
from typing import Optional

app = typer.Typer(help="Task execution state management")


@app.command("show")
def show_state(
    task_id: str = typer.Argument(..., help="Task ID (e.g., T28.1)"),
):
    """Show current execution state for a task.
    
    Examples:
        bpsai-pair state show T28.1
    """
    from rich.console import Console
    from rich.panel import Panel
    
    from ..core.task_state import (
        get_state_manager,
        VALID_TRANSITIONS,
        TRANSITION_TRIGGERS,
        is_state_machine_enabled,
    )
    
    console = Console()
    
    # Check if enabled
    if not is_state_machine_enabled():
        console.print("[yellow]⚠️ State machine is disabled in config[/yellow]")
        console.print("[dim]Enable with: enforcement.state_machine: true in config.yaml[/dim]\n")
    
    mgr = get_state_manager()
    current = mgr.get_state(task_id)
    
    # Build state info
    valid_next = VALID_TRANSITIONS.get(current, [])
    
    lines = [f"[bold]State:[/bold] {current.value}"]
    
    if valid_next:
        lines.append("")
        lines.append("[bold]Next valid states:[/bold]")
        for next_state in valid_next:
            trigger = TRANSITION_TRIGGERS.get((current, next_state), "")
            lines.append(f"  • {next_state.value}")
            if trigger:
                lines.append(f"    [dim]→ {trigger}[/dim]")
    else:
        lines.append("")
        lines.append("[green]✓ Complete (terminal state)[/green]")
    
    console.print(Panel("\n".join(lines), title=f"Task {task_id}"))


@app.command("history")
def show_history(
    task_id: Optional[str] = typer.Argument(None, help="Task ID (optional, shows all if omitted)"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
):
    """Show state transition history.
    
    Examples:
        bpsai-pair state history
        bpsai-pair state history T28.1
        bpsai-pair state history --limit 50
    """
    from rich.console import Console
    from rich.table import Table
    
    from ..core.task_state import get_state_manager
    
    console = Console()
    mgr = get_state_manager()
    
    history = mgr.get_history(task_id=task_id, limit=limit)
    
    if not history:
        console.print("[dim]No state transitions recorded.[/dim]")
        return
    
    table = Table(title="State Transition History")
    table.add_column("Time", style="dim", width=16)
    table.add_column("Task", width=10)
    table.add_column("From", width=14)
    table.add_column("To", width=14)
    table.add_column("Trigger", width=30)
    
    for entry in history:
        ts = entry["timestamp"][:16].replace("T", " ")
        trigger = entry.get("trigger", "")[:30]
        
        # Color code transitions
        to_state = entry["to_state"]
        if to_state == "completed":
            style = "green"
        elif to_state == "blocked":
            style = "red"
        elif to_state == "in_progress":
            style = "cyan"
        else:
            style = ""
        
        table.add_row(
            ts,
            entry["task_id"],
            entry["from_state"],
            f"[{style}]{to_state}[/{style}]" if style else to_state,
            trigger,
        )
    
    console.print(table)


@app.command("list")
def list_states(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by state"),
):
    """List all tracked task states.
    
    Examples:
        bpsai-pair state list
        bpsai-pair state list --status in_progress
    """
    from rich.console import Console
    from rich.table import Table
    
    from ..core.task_state import get_state_manager, TaskState
    
    console = Console()
    mgr = get_state_manager()
    
    all_states = mgr.get_all_states()
    
    if not all_states:
        console.print("[dim]No tasks being tracked.[/dim]")
        return
    
    # Filter if requested
    if status:
        all_states = {k: v for k, v in all_states.items() if v == status}
        if not all_states:
            console.print(f"[dim]No tasks in state '{status}'[/dim]")
            return
    
    table = Table(title="Tracked Task States")
    table.add_column("Task ID", width=12)
    table.add_column("State", width=14)
    
    for task_id, state in sorted(all_states.items()):
        # Color code
        if state == "completed":
            style = "green"
        elif state == "blocked":
            style = "red"
        elif state == "in_progress":
            style = "cyan"
        else:
            style = "dim"
        
        table.add_row(task_id, f"[{style}]{state}[/{style}]")
    
    console.print(table)


@app.command("reset")
def reset_state(
    task_id: str = typer.Argument(..., help="Task ID to reset"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Reset a task to NOT_STARTED state.
    
    Use this to re-do a task or fix state issues.
    
    Examples:
        bpsai-pair state reset T28.1
        bpsai-pair state reset T28.1 --yes
    """
    from ..core.task_state import get_state_manager
    
    mgr = get_state_manager()
    current = mgr.get_state(task_id)
    
    if current.value == "not_started":
        typer.echo(f"Task {task_id} is already in not_started state.")
        return
    
    if not confirm:
        typer.confirm(
            f"Reset task {task_id} from '{current.value}' to 'not_started'?",
            abort=True
        )
    
    mgr.reset_task(task_id)


@app.command("advance")
def advance_state(
    task_id: str = typer.Argument(..., help="Task ID"),
    to_state: str = typer.Argument(..., help="Target state"),
    reason: str = typer.Option("manual", "--reason", "-r", help="Reason for transition"),
):
    """Manually advance task to a new state.
    
    Only valid transitions are allowed.
    
    Examples:
        bpsai-pair state advance T28.1 budget_checked
        bpsai-pair state advance T28.1 in_progress --reason "Starting work"
    """
    from ..core.task_state import get_state_manager, TaskState
    
    # Parse target state
    try:
        target = TaskState(to_state)
    except ValueError:
        valid = [s.value for s in TaskState]
        typer.echo(f"Invalid state '{to_state}'. Valid states: {', '.join(valid)}", err=True)
        raise typer.Exit(1)
    
    mgr = get_state_manager()
    mgr.transition(task_id, target, trigger=reason)
