"""
Trello-backed task commands.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .auth import load_token
from .client import TrelloService

app = typer.Typer(name="ttask", help="Trello task commands")
console = Console()

AGENT_TYPE = "claude"  # Identifies this agent in comments


def get_board_client() -> tuple[TrelloService, dict]:
    """Get client with board already set.

    Returns:
        Tuple of (TrelloService, config dict)

    Raises:
        typer.Exit: If not connected or no board configured
    """
    creds = load_token()
    if not creds:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)

    # Load config
    try:
        from pathlib import Path
        import yaml
        config_file = Path.cwd() / ".paircoder" / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
    except Exception:
        config = {}

    board_id = config.get("trello", {}).get("board_id")
    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    try:
        client = TrelloService(api_key=creds["api_key"], token=creds["token"])
        client.set_board(board_id)
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    return client, config


def format_card_id(card) -> str:
    """Format card ID for display."""
    return f"TRELLO-{card.short_id}"


def log_activity(card, action: str, summary: str) -> None:
    """Add activity comment to card.

    Args:
        card: Trello card object
        action: Action type (started, completed, blocked, progress)
        summary: Summary text
    """
    comment = f"[{AGENT_TYPE}] {action}: {summary}"
    try:
        card.comment(comment)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not add comment: {e}[/yellow]")


@app.command("list")
def task_list(
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Filter by list name"),
    agent_tasks: bool = typer.Option(False, "--agent", "-a", help="Only show Agent Task cards"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (backlog, sprint, in_progress, review, done, blocked)"),
):
    """List tasks from Trello board."""
    client, config = get_board_client()

    # Get list name mappings from config
    list_mappings = config.get("trello", {}).get("lists", {
        "backlog": "Backlog",
        "sprint": "Sprint",
        "in_progress": "In Progress",
        "review": "In Review",
        "done": "Done",
        "blocked": "Blocked",
    })

    cards = []

    if list_name:
        cards = client.get_cards_in_list(list_name)
    elif status:
        target_list = list_mappings.get(status, status)
        cards = client.get_cards_in_list(target_list)
    else:
        # Default: Sprint + In Progress
        for ln in [list_mappings.get("sprint", "Sprint"), list_mappings.get("in_progress", "In Progress")]:
            cards.extend(client.get_cards_in_list(ln))

    # Filter for agent tasks if requested
    if agent_tasks:
        filtered = []
        agent_field = config.get("trello", {}).get("custom_fields", {}).get("agent_task", "Agent Task")
        for card in cards:
            try:
                field = card.get_custom_field_by_name(agent_field)
                if field and field.value == True:
                    filtered.append(card)
            except Exception:
                pass
        cards = filtered

    if not cards:
        console.print("[yellow]No tasks found matching criteria[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Title", width=40)
    table.add_column("List", style="dim")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")

    priority_field = config.get("trello", {}).get("custom_fields", {}).get("priority", "Priority")

    for card in cards:
        try:
            card_list = card.get_list().name
        except Exception:
            card_list = "Unknown"

        blocked = "[red]Blocked[/red]" if client.is_card_blocked(card) else "[green]Ready[/green]"

        # Try to get priority
        priority = "-"
        try:
            pfield = card.get_custom_field_by_name(priority_field)
            if pfield and pfield.value:
                priority = str(pfield.value)
        except Exception:
            pass

        table.add_row(
            format_card_id(card),
            card.name[:40],
            card_list,
            priority,
            blocked
        )

    console.print(table)


@app.command("show")
def task_show(card_id: str = typer.Argument(..., help="Card ID (e.g., TRELLO-123 or just 123)")):
    """Show task details from Trello."""
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    try:
        card.fetch()  # Get full details
    except Exception:
        pass

    # Header
    console.print(Panel(f"[bold]{card.name}[/bold]", subtitle=format_card_id(card)))

    # Metadata
    if lst:
        console.print(f"[dim]List:[/dim] {lst.name}")
    console.print(f"[dim]URL:[/dim] {card.url}")

    # Labels
    try:
        if card.labels:
            labels = ", ".join([l.name for l in card.labels if l.name])
            if labels:
                console.print(f"[dim]Labels:[/dim] {labels}")
    except Exception:
        pass

    # Priority
    try:
        priority_field = config.get("trello", {}).get("custom_fields", {}).get("priority", "Priority")
        pfield = card.get_custom_field_by_name(priority_field)
        if pfield and pfield.value:
            console.print(f"[dim]Priority:[/dim] {pfield.value}")
    except Exception:
        pass

    # Blocked status
    if client.is_card_blocked(card):
        console.print("[red]BLOCKED - has unchecked dependencies[/red]")

    # Description
    try:
        if card.description:
            console.print("\n[dim]Description:[/dim]")
            console.print(Markdown(card.description))
    except Exception:
        pass

    # Checklists
    try:
        if card.checklists:
            console.print("\n[dim]Checklists:[/dim]")
            for cl in card.checklists:
                console.print(f"  [bold]{cl.name}[/bold]")
                for item in cl.items:
                    check = "[green]✓[/green]" if item.get("checked") else "○"
                    console.print(f"    {check} {item.get('name', '')}")
    except Exception:
        pass


@app.command("start")
def task_start(
    card_id: str = typer.Argument(..., help="Card ID to start"),
    summary: str = typer.Option("Beginning work", "--summary", "-s", help="Start summary"),
):
    """Start working on a task (moves to In Progress)."""
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    if client.is_card_blocked(card):
        console.print(f"[red]Cannot start - card has unchecked dependencies[/red]")
        raise typer.Exit(1)

    # Move to In Progress
    in_progress_list = config.get("trello", {}).get("lists", {}).get("in_progress", "In Progress")
    client.move_card(card, in_progress_list)

    # Log activity
    log_activity(card, "started", summary)

    console.print(f"[green]✓ Started: {card.name}[/green]")
    console.print(f"  Moved to: {in_progress_list}")
    console.print(f"  URL: {card.url}")


@app.command("done")
def task_done(
    card_id: str = typer.Argument(..., help="Card ID to complete"),
    summary: str = typer.Option(..., "--summary", "-s", prompt=True, help="Completion summary"),
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Target list (default: In Review)"),
):
    """Complete a task (moves to In Review or Done)."""
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    # Determine target list
    if list_name is None:
        list_name = config.get("trello", {}).get("lists", {}).get("review", "In Review")

    # Move to target list
    client.move_card(card, list_name)

    # Log activity
    log_activity(card, "completed", summary)

    console.print(f"[green]✓ Completed: {card.name}[/green]")
    console.print(f"  Moved to: {list_name}")
    console.print(f"  Summary: {summary}")


@app.command("block")
def task_block(
    card_id: str = typer.Argument(..., help="Card ID to block"),
    reason: str = typer.Option(..., "--reason", "-r", prompt=True, help="Block reason"),
):
    """Mark a task as blocked."""
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    # Move to Blocked
    blocked_list = config.get("trello", {}).get("lists", {}).get("blocked", "Blocked")
    client.move_card(card, blocked_list)

    # Log activity
    log_activity(card, "blocked", reason)

    console.print(f"[yellow]Blocked: {card.name}[/yellow]")
    console.print(f"  Reason: {reason}")


@app.command("comment")
def task_comment(
    card_id: str = typer.Argument(..., help="Card ID"),
    message: str = typer.Argument(..., help="Comment message"),
):
    """Add a comment to a task."""
    client, _ = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    # Log as progress update
    log_activity(card, "progress", message)

    console.print(f"[green]✓ Comment added to: {card.name}[/green]")


@app.command("move")
def task_move(
    card_id: str = typer.Argument(..., help="Card ID"),
    list_name: str = typer.Option(..., "--list", "-l", help="Target list name"),
):
    """Move a task to a different list."""
    client, _ = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    old_list = lst.name if lst else "Unknown"
    client.move_card(card, list_name)

    console.print(f"[green]✓ Moved: {card.name}[/green]")
    console.print(f"  {old_list} → {list_name}")
