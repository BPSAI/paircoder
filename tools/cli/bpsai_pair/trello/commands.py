"""
Trello CLI commands for PairCoder.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from .auth import load_token, store_token, clear_token, is_connected
from .client import TrelloService

app = typer.Typer(name="trello", help="Trello integration commands")
console = Console()


def get_client() -> TrelloService:
    """Get an authenticated Trello client.

    Returns:
        TrelloService instance

    Raises:
        typer.Exit: If not connected to Trello
    """
    creds = load_token()
    if not creds:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)
    return TrelloService(api_key=creds["api_key"], token=creds["token"])


def _load_config() -> dict:
    """Load project config with error handling."""
    try:
        from ..config import Config
        from pathlib import Path
        import yaml

        root = Path.cwd()
        config_file = root / ".paircoder" / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f) or {}
        return {}
    except Exception:
        return {}


def _save_config(config: dict) -> None:
    """Save project config."""
    try:
        from pathlib import Path
        import yaml

        root = Path.cwd()
        config_dir = root / ".paircoder"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.yaml"

        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save config: {e}[/yellow]")


@app.command()
def connect(
    api_key: str = typer.Option(..., prompt=True, help="Trello API key"),
    token: str = typer.Option(..., prompt=True, hide_input=True, help="Trello token"),
):
    """Connect to Trello (validates and stores credentials)."""
    try:
        client = TrelloService(api_key=api_key, token=token)
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if not client.healthcheck():
        console.print("[red]Failed to validate Trello credentials[/red]")
        raise typer.Exit(1)

    store_token(token=token, api_key=api_key)
    console.print("[green]✓ Connected to Trello[/green]")


@app.command()
def status():
    """Check Trello connection status."""
    if is_connected():
        console.print("[green]✓ Connected to Trello[/green]")

        config = _load_config()
        board_id = config.get("trello", {}).get("board_id")
        board_name = config.get("trello", {}).get("board_name")

        if board_id:
            console.print(f"  Board: {board_name} ({board_id})")
        else:
            console.print("  [yellow]No board configured. Run: bpsai-pair trello use-board <id>[/yellow]")
    else:
        console.print("[yellow]Not connected. Run: bpsai-pair trello connect[/yellow]")


@app.command()
def disconnect():
    """Remove stored Trello credentials."""
    clear_token()
    console.print("[green]✓ Disconnected from Trello[/green]")


@app.command()
def boards():
    """List available Trello boards."""
    client = get_client()
    board_list = client.list_boards()

    table = Table(title="Trello Boards")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("URL")

    for board in board_list:
        if not board.closed:
            table.add_row(board.id, board.name, board.url)

    console.print(table)


@app.command("use-board")
def use_board(board_id: str = typer.Argument(..., help="Board ID to use")):
    """Set the active Trello board for this project."""
    client = get_client()
    board = client.set_board(board_id)

    config = _load_config()
    if "trello" not in config:
        config["trello"] = {}
    config["trello"]["board_id"] = board_id
    config["trello"]["board_name"] = board.name
    config["trello"]["enabled"] = True
    _save_config(config)

    console.print(f"[green]✓ Using board: {board.name}[/green]")

    lists = client.get_board_lists()
    console.print(f"\nLists: {', '.join(lists.keys())}")


@app.command()
def lists():
    """Show lists on the active board."""
    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    client = get_client()
    client.set_board(board_id)

    table = Table(title=f"Lists on {config['trello'].get('board_name', board_id)}")
    table.add_column("Name")
    table.add_column("Cards", justify="right")

    for name, lst in client.get_board_lists().items():
        card_count = len(lst.list_cards())
        table.add_row(name, str(card_count))

    console.print(table)


@app.command("config")
def trello_config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    set_list: Optional[str] = typer.Option(None, "--set-list", help="Set list mapping (format: status=ListName)"),
    set_field: Optional[str] = typer.Option(None, "--set-field", help="Set custom field (format: field=FieldName)"),
    agent: Optional[str] = typer.Option(None, "--agent", help="Set agent identity (claude/codex)"),
):
    """View or modify Trello configuration."""
    config = _load_config()
    trello = config.get("trello", {})

    # Merge with defaults
    defaults = {
        "enabled": False,
        "board_id": None,
        "board_name": None,
        "lists": {
            "backlog": "Backlog",
            "sprint": "Sprint",
            "in_progress": "In Progress",
            "review": "In Review",
            "done": "Done",
            "blocked": "Blocked",
        },
        "custom_fields": {
            "agent_task": "Agent Task",
            "priority": "Priority",
        },
        "agent_identity": "claude",
        "auto_sync": True,
    }

    for key, default in defaults.items():
        if key not in trello:
            trello[key] = default
        elif isinstance(default, dict) and isinstance(trello.get(key), dict):
            trello[key] = {**default, **trello[key]}

    if show or (not set_list and not set_field and not agent):
        console.print("[bold]Trello Configuration[/bold]\n")
        console.print(f"Enabled: {trello['enabled']}")
        console.print(f"Board: {trello['board_name']} ({trello['board_id']})")
        console.print(f"Agent: {trello['agent_identity']}")
        console.print(f"Auto-sync: {trello['auto_sync']}")
        console.print("\n[dim]List Mappings:[/dim]")
        for status, list_name in trello.get('lists', {}).items():
            console.print(f"  {status}: {list_name}")
        console.print("\n[dim]Custom Fields:[/dim]")
        for field, name in trello.get('custom_fields', {}).items():
            console.print(f"  {field}: {name}")
        return

    updates_made = False

    if set_list:
        if "=" not in set_list:
            console.print("[red]Invalid format. Use: --set-list status=ListName[/red]")
            raise typer.Exit(1)
        status, list_name = set_list.split("=", 1)
        if "lists" not in trello:
            trello["lists"] = {}
        trello["lists"][status] = list_name
        console.print(f"[green]✓ Set list mapping: {status} → {list_name}[/green]")
        updates_made = True

    if set_field:
        if "=" not in set_field:
            console.print("[red]Invalid format. Use: --set-field field=FieldName[/red]")
            raise typer.Exit(1)
        field, name = set_field.split("=", 1)
        if "custom_fields" not in trello:
            trello["custom_fields"] = {}
        trello["custom_fields"][field] = name
        console.print(f"[green]✓ Set custom field: {field} → {name}[/green]")
        updates_made = True

    if agent:
        if agent not in ["claude", "codex"]:
            console.print("[red]Agent must be 'claude' or 'codex'[/red]")
            raise typer.Exit(1)
        trello["agent_identity"] = agent
        console.print(f"[green]✓ Set agent identity: {agent}[/green]")
        updates_made = True

    if updates_made:
        config["trello"] = trello
        _save_config(config)


@app.command("progress")
def progress_comment(
    task_id: str = typer.Argument(..., help="Task ID (e.g., TASK-001)"),
    message: str = typer.Argument(None, help="Progress message"),
    blocked: Optional[str] = typer.Option(None, "--blocked", "-b", help="Report blocking issue"),
    waiting: Optional[str] = typer.Option(None, "--waiting", "-w", help="Report waiting for dependency"),
    step: Optional[str] = typer.Option(None, "--step", "-s", help="Report completed step"),
    started: bool = typer.Option(False, "--started", help="Report task started"),
    completed: bool = typer.Option(False, "--completed", "-c", help="Report task completed"),
    review: bool = typer.Option(False, "--review", "-r", help="Report submitted for review"),
    agent: str = typer.Option("claude", "--agent", "-a", help="Agent name for comment"),
):
    """Post a progress comment to a Trello card.

    Examples:
        # Report progress
        bpsai-pair trello progress TASK-001 "Completed authentication module"

        # Report blocking issue
        bpsai-pair trello progress TASK-001 --blocked "Waiting for API access"

        # Report step completion
        bpsai-pair trello progress TASK-001 --step "Unit tests passing"

        # Report task started
        bpsai-pair trello progress TASK-001 --started

        # Report completion with summary
        bpsai-pair trello progress TASK-001 --completed "Added user auth with OAuth2"
    """
    from pathlib import Path
    from .progress import create_progress_reporter

    paircoder_dir = Path.cwd() / ".paircoder"
    if not paircoder_dir.exists():
        console.print("[red]Not in a PairCoder project directory[/red]")
        raise typer.Exit(1)

    reporter = create_progress_reporter(paircoder_dir, task_id, agent)
    if not reporter:
        console.print("[red]Could not create progress reporter. Check Trello connection.[/red]")
        raise typer.Exit(1)

    success = False

    if started:
        success = reporter.report_start()
        if success:
            console.print(f"[green]Posted: Task started[/green]")
    elif blocked:
        success = reporter.report_blocked(blocked)
        if success:
            console.print(f"[green]Posted: Blocked - {blocked}[/green]")
    elif waiting:
        success = reporter.report_waiting(waiting)
        if success:
            console.print(f"[green]Posted: Waiting for {waiting}[/green]")
    elif step:
        success = reporter.report_step_complete(step)
        if success:
            console.print(f"[green]Posted: Completed step - {step}[/green]")
    elif completed:
        summary = message or "Task completed"
        success = reporter.report_completion(summary)
        if success:
            console.print(f"[green]Posted: Task completed[/green]")
    elif review:
        success = reporter.report_review()
        if success:
            console.print(f"[green]Posted: Submitted for review[/green]")
    elif message:
        success = reporter.report_progress(message)
        if success:
            console.print(f"[green]Posted: {message}[/green]")
    else:
        console.print("[yellow]No progress update specified. Use --help for options.[/yellow]")
        raise typer.Exit(1)

    if not success:
        console.print("[red]Failed to post progress comment[/red]")
        raise typer.Exit(1)


@app.command("sync")
def trello_sync(
    from_trello: bool = typer.Option(False, "--from-trello", help="Sync changes FROM Trello to local tasks"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview changes without applying"),
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Only sync cards from specific list"),
):
    """Sync tasks between Trello and local files.

    By default, previews what would be synced. Use --from-trello to pull
    changes from Trello cards and update local task files.

    Examples:
        # Preview what would be synced
        bpsai-pair trello sync --preview

        # Pull changes from Trello to local
        bpsai-pair trello sync --from-trello

        # Only sync cards from a specific list
        bpsai-pair trello sync --from-trello --list "In Progress"
    """
    from pathlib import Path
    from rich.table import Table
    from .sync import TrelloToLocalSync
    from .auth import load_token

    paircoder_dir = Path.cwd() / ".paircoder"
    if not paircoder_dir.exists():
        console.print("[red]Not in a PairCoder project directory[/red]")
        raise typer.Exit(1)

    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")
    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    token_data = load_token()
    if not token_data:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)

    # Create sync instance
    try:
        from .client import TrelloService
        service = TrelloService(token_data["api_key"], token_data["token"])
        service.set_board(board_id)
        sync_manager = TrelloToLocalSync(service, paircoder_dir / "tasks")
    except Exception as e:
        console.print(f"[red]Failed to connect to Trello: {e}[/red]")
        raise typer.Exit(1)

    if preview or not from_trello:
        # Preview mode
        console.print("\n[bold]Sync Preview (Trello → Local)[/bold]\n")

        preview_results = sync_manager.get_sync_preview()
        if not preview_results:
            console.print("[dim]No cards with task IDs found on board[/dim]")
            return

        table = Table()
        table.add_column("Task ID", style="cyan")
        table.add_column("Action", style="yellow")
        table.add_column("Details")

        updates_pending = 0
        for item in preview_results:
            task_id = item["task_id"]
            action = item["action"]

            if action == "update":
                details = f"{item['field']}: {item['from']} → {item['to']}"
                table.add_row(task_id, "[green]update[/green]", details)
                updates_pending += 1
            elif action == "skip":
                reason = item.get("reason", "No changes")
                table.add_row(task_id, "[dim]skip[/dim]", f"[dim]{reason}[/dim]")
            elif action == "error":
                table.add_row(task_id, "[red]error[/red]", item.get("reason", "Unknown error"))

        console.print(table)
        console.print(f"\n[bold]{updates_pending}[/bold] task(s) would be updated")

        if updates_pending > 0 and not from_trello:
            console.print("\n[dim]Run with --from-trello to apply changes[/dim]")

    else:
        # Apply changes
        console.print("\n[bold]Syncing from Trello → Local[/bold]\n")

        list_filter = [list_name] if list_name else None
        results = sync_manager.sync_all_cards(list_filter=list_filter)

        if not results:
            console.print("[dim]No cards with task IDs found on board[/dim]")
            return

        updated = 0
        skipped = 0
        errors = 0

        for result in results:
            if result.action == "updated":
                updated += 1
                changes_str = ", ".join(
                    f"{k}: {v['from']} → {v['to']}"
                    for k, v in result.changes.items()
                )
                console.print(f"  [green]✓[/green] {result.task_id}: {changes_str}")

                # Show conflicts if any
                for conflict in result.conflicts:
                    console.print(f"    [yellow]⚠ Conflict: {conflict.field} ({conflict.resolution})[/yellow]")

            elif result.action == "skipped":
                skipped += 1
            elif result.action == "error":
                errors += 1
                console.print(f"  [red]✗[/red] {result.task_id}: {result.error}")

        console.print(f"\n[bold]Summary:[/bold] {updated} updated, {skipped} skipped, {errors} errors")


# Register webhook subcommands
from .webhook_commands import app as webhook_app
app.add_typer(webhook_app, name="webhook")
