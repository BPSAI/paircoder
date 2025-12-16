---
id: TASK-041
title: Add Trello-backed task commands
plan: plan-2025-01-paircoder-v2-upgrade
type: feature
priority: P0
complexity: 70
status: done
sprint: sprint-10
tags:
  - trello
  - cli
  - tasks
depends_on:
  - TASK-040
---

# Objective

Extend `bpsai-pair task` commands to work with Trello as the backend when enabled, allowing task management directly from the CLI.

# Background

With Trello integration enabled (TASK-025), the `task` commands should be able to:
- List tasks from Trello cards
- Show task details
- Start/claim tasks (move to In Progress)
- Complete tasks (move to Done/Review)
- Block tasks with reason
- Add comments

# Implementation Plan

## 1. Create Task-Trello Commands Module

Create `tools/cli/bpsai_pair/trello/task_commands.py`:

```python
"""
Trello-backed task commands.
"""
import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .auth import load_token
from .client import TrelloService
from ..config import load_config

app = typer.Typer()
console = Console()

AGENT_TYPE = "claude"  # Identifies this agent in comments


def get_board_client() -> tuple[TrelloService, dict]:
    """Get client with board already set."""
    creds = load_token()
    if not creds:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)
    
    config = load_config()
    board_id = config.get("trello", {}).get("board_id")
    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)
    
    client = TrelloService(api_key=creds["api_key"], token=creds["token"])
    client.set_board(board_id)
    return client, config


def find_card(client: TrelloService, card_id: str):
    """Find a card by ID or short ID."""
    for lst in client.board.all_lists():
        for card in lst.list_cards():
            if card.id == card_id or str(card.short_id) == card_id or f"TRELLO-{card.short_id}" == card_id:
                return card, lst
    return None, None


def format_card_id(card) -> str:
    """Format card ID for display."""
    return f"TRELLO-{card.short_id}"


def log_activity(card, action: str, summary: str):
    """Add activity comment to card."""
    comment = f"🧠 [{AGENT_TYPE}] {action}: {summary}"
    card.comment(comment)


@app.command("list")
def task_list(
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Filter by list name"),
    agent_tasks: bool = typer.Option(False, "--agent", "-a", help="Only show Agent Task cards"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (sprint, in_progress, blocked, done)"),
):
    """List tasks from Trello board."""
    client, config = get_board_client()
    
    # Map status to list names
    status_map = {
        "backlog": "Backlog",
        "sprint": "Sprint",
        "in_progress": "In Progress",
        "review": "In Review",
        "done": "Done",
        "blocked": "Blocked",
    }
    
    cards = []
    
    if list_name:
        cards = client.get_cards_in_list(list_name)
    elif status:
        target_list = status_map.get(status, status)
        cards = client.get_cards_in_list(target_list)
    else:
        # Default: Sprint + In Progress
        for ln in ["Sprint", "In Progress"]:
            cards.extend(client.get_cards_in_list(ln))
    
    # Filter for agent tasks if requested
    if agent_tasks:
        filtered = []
        for card in cards:
            try:
                field = card.get_custom_field_by_name("Agent Task")
                if field and field.value == True:
                    filtered.append(card)
            except:
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
    
    for card in cards:
        card_list = card.get_list().name
        blocked = "🚫" if client.is_card_blocked(card) else "✓"
        
        # Try to get priority
        priority = "-"
        try:
            pfield = card.get_custom_field_by_name("Priority")
            if pfield and pfield.value:
                priority = pfield.value
        except:
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
    client, _ = get_board_client()
    card, lst = find_card(client, card_id)
    
    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)
    
    card.fetch()  # Get full details
    
    # Header
    console.print(Panel(f"[bold]{card.name}[/bold]", subtitle=format_card_id(card)))
    
    # Metadata
    console.print(f"[dim]List:[/dim] {lst.name}")
    console.print(f"[dim]URL:[/dim] {card.url}")
    
    # Labels
    if card.labels:
        labels = ", ".join([l.name for l in card.labels if l.name])
        console.print(f"[dim]Labels:[/dim] {labels}")
    
    # Priority
    try:
        pfield = card.get_custom_field_by_name("Priority")
        if pfield and pfield.value:
            console.print(f"[dim]Priority:[/dim] {pfield.value}")
    except:
        pass
    
    # Blocked status
    if client.is_card_blocked(card):
        console.print("[red]⚠ BLOCKED - has unchecked dependencies[/red]")
    
    # Description
    if card.description:
        console.print("\n[dim]Description:[/dim]")
        console.print(Markdown(card.description))
    
    # Checklists
    if card.checklists:
        console.print("\n[dim]Checklists:[/dim]")
        for cl in card.checklists:
            console.print(f"  [bold]{cl.name}[/bold]")
            for item in cl.items:
                check = "✓" if item["checked"] else "○"
                style = "green" if item["checked"] else ""
                console.print(f"    [{style}]{check} {item['name']}[/{style}]")


@app.command("start")
def task_start(
    card_id: str = typer.Argument(..., help="Card ID to start"),
    summary: str = typer.Option("Beginning work", "--summary", "-s", help="Start summary"),
):
    """Start working on a task (moves to In Progress)."""
    client, _ = get_board_client()
    card, lst = find_card(client, card_id)
    
    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)
    
    if client.is_card_blocked(card):
        console.print(f"[red]Cannot start - card has unchecked dependencies[/red]")
        raise typer.Exit(1)
    
    # Move to In Progress
    client.move_card(card, "In Progress")
    
    # Log activity
    log_activity(card, "started", summary)
    
    console.print(f"[green]✓ Started: {card.name}[/green]")
    console.print(f"  Moved to: In Progress")
    console.print(f"  URL: {card.url}")


@app.command("done")
def task_done(
    card_id: str = typer.Argument(..., help="Card ID to complete"),
    summary: str = typer.Option(..., "--summary", "-s", prompt=True, help="Completion summary"),
    list_name: str = typer.Option("In Review", "--list", "-l", help="Target list (default: In Review)"),
):
    """Complete a task (moves to In Review or Done)."""
    client, _ = get_board_client()
    card, lst = find_card(client, card_id)
    
    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)
    
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
    client, _ = get_board_client()
    card, lst = find_card(client, card_id)
    
    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)
    
    # Move to Blocked
    client.move_card(card, "Blocked")
    
    # Log activity
    log_activity(card, "blocked", reason)
    
    console.print(f"[yellow]⚠ Blocked: {card.name}[/yellow]")
    console.print(f"  Reason: {reason}")


@app.command("comment")
def task_comment(
    card_id: str = typer.Argument(..., help="Card ID"),
    message: str = typer.Argument(..., help="Comment message"),
):
    """Add a comment to a task."""
    client, _ = get_board_client()
    card, lst = find_card(client, card_id)
    
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
    card, lst = find_card(client, card_id)
    
    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)
    
    old_list = lst.name
    client.move_card(card, list_name)
    
    console.print(f"[green]✓ Moved: {card.name}[/green]")
    console.print(f"  {old_list} → {list_name}")
```

## 2. Update Main CLI to Use Trello Tasks When Enabled

Modify `tools/cli/bpsai_pair/cli.py` to route task commands based on config:

```python
# Add import at top
from .trello.task_commands import app as trello_task_app

# Add helper function
def is_trello_enabled() -> bool:
    """Check if Trello backend is enabled for tasks."""
    try:
        config = load_config()
        return config.get("trello", {}).get("enabled", False)
    except:
        return False

# Option A: Add as separate command group
app.add_typer(trello_task_app, name="ttask", help="Trello task commands")

# Option B: Override task commands when trello enabled
# (More complex, implement in future iteration)
```

## 3. Add Convenience Alias

For easier usage, add alias in CLI:

```python
@app.command("next")
def next_task():
    """Show next task to work on (from Trello if enabled)."""
    if is_trello_enabled():
        from .trello.task_commands import task_list
        # Show sprint tasks sorted by priority
        task_list(list_name=None, agent_tasks=True, status="sprint")
    else:
        # Fall back to file-based
        from .planning.cli_commands import task_next
        task_next()
```

# Files to Create/Modify

| Action | File |
|--------|------|
| Create | `tools/cli/bpsai_pair/trello/task_commands.py` |
| Modify | `tools/cli/bpsai_pair/cli.py` |

# Acceptance Criteria

- [ ] `bpsai-pair ttask list` shows tasks from Trello
- [ ] `bpsai-pair ttask list --agent` filters to Agent Task cards
- [ ] `bpsai-pair ttask list --status sprint` filters by list
- [ ] `bpsai-pair ttask show <id>` displays card details
- [ ] `bpsai-pair ttask start <id>` moves card and adds comment
- [ ] `bpsai-pair ttask done <id> --summary "..."` completes task
- [ ] `bpsai-pair ttask block <id> --reason "..."` blocks task
- [ ] `bpsai-pair ttask comment <id> "message"` adds comment
- [ ] `bpsai-pair ttask move <id> --list "Done"` moves card
- [ ] All comments include agent identifier (🧠 [claude])

# Verification

```bash
# List tasks
bpsai-pair ttask list
bpsai-pair ttask list --status sprint
bpsai-pair ttask list --agent

# Work on a task
bpsai-pair ttask show TRELLO-123
bpsai-pair ttask start TRELLO-123
bpsai-pair ttask comment TRELLO-123 "Halfway done"
bpsai-pair ttask done TRELLO-123 --summary "Implemented feature"

# Check Trello board - should see:
# - Card moved to correct lists
# - Comments with 🧠 [claude] prefix
```
