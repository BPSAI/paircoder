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
        from ..core.ops import find_project_root
        import yaml
        config_file = find_project_root() / ".paircoder" / "config.yaml"
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
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


def _get_unchecked_ac_items(card, checklist_name: str = "Acceptance Criteria") -> list:
    """Get all unchecked items in the Acceptance Criteria checklist.

    Args:
        card: Trello card object
        checklist_name: Name of the checklist to check (default: "Acceptance Criteria")

    Returns:
        List of unchecked item dicts with 'id' and 'name' keys
    """
    if not card.checklists:
        return []

    unchecked = []
    for checklist in card.checklists:
        if checklist.name.lower() != checklist_name.lower():
            continue

        for item in checklist.items:
            if not item.get("checked"):
                unchecked.append(item)

    return unchecked


from ..core.bypass_log import log_bypass

def _log_bypass(command: str, task_id: str, reason: str = "forced") -> None:
    """Log bypass to audit file - delegates to core module."""
    log_bypass(command=command, target=task_id, reason=reason)


def _get_task_id_from_card(card) -> Optional[str]:
    """Extract local task ID from Trello card.

    Looks for task ID in:
    1. Card name pattern "[T27.1]" or "[TASK-123]" (bracketed)
    2. Card name pattern "T27.1: ..." or "TASK-123: ..." (at start)
    3. Card description containing "Task: T27.1"

    Args:
        card: Trello card object with name and description attributes

    Returns:
        Task ID string (e.g., "T27.1") or None if not found
    """
    import re

    # Get card name
    name = card.name if hasattr(card, 'name') else ""

    # Try bracketed pattern first (e.g., "[T27.1] Create module")
    match = re.search(r'\[(T\d+\.\d+|TASK-\d+)]', name)
    if match:
        return match.group(1)

    # Try start of name pattern (e.g., "T27.1: Create module" or "T27.1 - Create")
    match = re.match(r'^(T\d+\.\d+|TASK-\d+)[\s:\-]', name)
    if match:
        return match.group(1)

    # Try description
    desc = card.description if hasattr(card, 'description') else ""
    if desc:
        match = re.search(r'Task:\s*(T\d+\.\d+|TASK-\d+)', desc)
        if match:
            return match.group(1)

    return None


def _update_local_task_status(card, status: str, summary: str = "") -> tuple[bool, Optional[str]]:
    """Update the corresponding local task file after ttask operation.

    Args:
        card: Trello card object (with name and description attributes)
        status: The new status to set
        summary: Optional completion summary

    Returns:
        Tuple of (success: bool, task_id: Optional[str])
    """
    try:
        # Extract task ID from card
        task_id = _get_task_id_from_card(card)
        if not task_id:
            return False, None

        # Find paircoder dir
        from ..core.ops import find_paircoder_dir
        paircoder_dir = find_paircoder_dir()
        if not paircoder_dir.exists():
            return False, task_id

        # Import task parser
        from ..planning.parser import TaskParser

        task_parser = TaskParser(paircoder_dir / "tasks")
        success = task_parser.update_status(task_id, status)

        return success, task_id
    except FileNotFoundError:
        raise  # Re-raise for caller to handle
    except Exception as e:
        console.print(f"[yellow]⚠ Could not update local task file: {e}[/yellow]")
        return False, None


def _run_completion_hooks(task_id: str) -> bool:
    """Run completion hooks to update state.md and other side effects.

    Args:
        task_id: The task ID that was completed

    Returns:
        True if hooks ran successfully, False otherwise
    """
    try:
        from ..core.ops import find_paircoder_dir

        paircoder_dir = find_paircoder_dir()
        if not paircoder_dir.exists():
            return False

        # Record CLI update to cache (for manual edit detection)
        try:
            from ..planning.cli_update_cache import get_cli_update_cache
            cli_cache = get_cli_update_cache(paircoder_dir)
            cli_cache.record_update(task_id, "done")
        except Exception:
            pass  # Best effort

        # Try to run hooks if available
        try:
            from ..core.hooks import HookRunner, HookContext
            from ..core.config import load_config

            config = load_config(paircoder_dir)
            hook_runner = HookRunner(config, paircoder_dir)

            # Create context for completion hooks
            context = HookContext(
                task_id=task_id,
                task=None,  # Task object not available here
                event="on_task_complete",
            )
            hook_runner.run_hooks("on_task_complete", context)
            return True
        except ImportError:
            # Hooks module not available
            return False
        except Exception as e:
            console.print(f"[yellow]⚠ Could not run completion hooks: {e}[/yellow]")
            return False
    except Exception:
        return False


def _check_task_budget(task_id: str, card_id: str, budget_override: bool = False) -> bool:
    """Check if task can proceed within token budget.

    Args:
        task_id: The task ID to estimate tokens for
        card_id: The Trello card ID (for display)
        budget_override: If True, log bypass and allow anyway

    Returns:
        True if task can proceed, False if blocked
    """
    try:
        from ..core.ops import find_paircoder_dir
        from ..planning.parser import TaskParser
        from ..metrics.estimation import TokenEstimator
        from ..metrics.budget import BudgetEnforcer
        from ..metrics.collector import MetricsCollector

        paircoder_dir = find_paircoder_dir()
        if not paircoder_dir.exists():
            return True  # No paircoder dir, skip check

        # Load the task
        task_parser = TaskParser(paircoder_dir / "tasks")
        task = task_parser.get_task_by_id(task_id)
        if not task:
            return True  # Task not found, skip check

        # Estimate tokens
        estimator = TokenEstimator()
        token_estimate = estimator.estimate_for_task(task)
        estimated_tokens = token_estimate.total_tokens

        # Convert tokens to estimated cost (rough: $0.003 per 1K input tokens for Claude)
        # Using a conservative estimate that includes both input and output
        estimated_cost_usd = (estimated_tokens / 1000) * 0.015  # $0.015 per 1K tokens

        # Check budget
        collector = MetricsCollector(paircoder_dir / "metrics")
        budget = BudgetEnforcer(collector)
        can_proceed, reason = budget.can_proceed(estimated_cost_usd)

        if not can_proceed:
            if budget_override:
                _log_bypass("budget_override", task_id, f"User override: {reason}")
                console.print(f"[yellow]⚠ Starting despite budget limit (logged): {reason}[/yellow]")
                return True
            else:
                status = budget.check_budget()
                console.print("[red]❌ BLOCKED: Task would exceed token budget[/red]")
                console.print("")
                console.print(f"[dim]Estimated tokens:[/dim] {estimated_tokens:,}")
                console.print(f"[dim]Estimated cost:[/dim]   ${estimated_cost_usd:.2f}")
                console.print(f"[dim]Daily remaining:[/dim]  ${status.daily_remaining:.2f}")
                console.print(f"[dim]Daily limit:[/dim]      ${status.daily_limit:.2f}")
                console.print("")
                console.print("[yellow]Options:[/yellow]")
                console.print("  1. Wait until tomorrow (limit resets)")
                console.print(f"  2. Override: [cyan]bpsai-pair ttask start {card_id} --budget-override[/cyan]")
                console.print("  3. Check budget: [cyan]bpsai-pair budget status[/cyan]")
                return False

        # Within budget
        console.print(f"[dim]Budget check passed ({estimated_tokens:,} tokens, ~${estimated_cost_usd:.2f})[/dim]")
        return True

    except ImportError as e:
        # Budget/metrics module not available, continue without check
        console.print(f"[dim]Budget check skipped: {e}[/dim]")
        return True
    except Exception as e:
        # Budget check failed, log but continue
        console.print(f"[dim]Budget check skipped: {e}[/dim]")
        return True


def _auto_check_acceptance_criteria(card, client: TrelloService, checklist_name: str = "Acceptance Criteria") -> int:
    """Check off all items in the Acceptance Criteria checklist.

    Args:
        card: Trello card object
        client: TrelloService instance
        checklist_name: Name of the checklist to check off (default: "Acceptance Criteria")

    Returns:
        Number of items that were checked off
    """
    import requests
    from .auth import load_token

    if not card.checklists:
        return 0

    checked_count = 0

    for checklist in card.checklists:
        if checklist.name.lower() != checklist_name.lower():
            continue

        for item in checklist.items:
            # Skip already checked items
            if item.get("checked"):
                continue

            item_name = item.get("name", "")

            # Try py-trello's method first
            try:
                checklist.set_checklist_item(item_name, checked=True)
                checked_count += 1
            except AttributeError:
                # Fallback: use direct API call
                try:
                    creds = load_token()
                    check_item_id = item.get("id")
                    url = f"https://api.trello.com/1/cards/{card.id}/checkItem/{check_item_id}"

                    response = requests.put(
                        url,
                        params={
                            "key": creds["api_key"],
                            "token": creds["token"],
                            "state": "complete"
                        }
                    )

                    if response.status_code == 200:
                        checked_count += 1
                except Exception:
                    pass  # Best effort - continue with other items

    return checked_count


@app.command("list")
def task_list(
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Filter by list name"),
    agent_tasks: bool = typer.Option(False, "--agent", "-a", help="Only show Agent Task cards"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (backlog, sprint, in_progress, review, done, blocked)"),
):
    """List tasks from Trello board."""
    client, config = get_board_client()

    # Get list name mappings from config with sensible defaults
    # These defaults include common variants to handle spacing differences
    list_mappings = config.get("trello", {}).get("lists", {
        "backlog": "Intake/Backlog",
        "sprint": "Planned/Ready",
        "in_progress": "In Progress",
        "review": "Review/Testing",
        "done": "Deployed/Done",
        "blocked": "Issues/Tech Debt",
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
    budget_override: bool = typer.Option(
        False, "--budget-override",
        help="Start despite budget warning (logged for audit)"
    ),
):
    """Start working on a task (moves to In Progress).

    Checks token budget before starting. Use --budget-override to bypass
    budget limits (logged for audit).
    """
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    # Check token budget BEFORE starting
    task_id = _get_task_id_from_card(card)
    if task_id:
        budget_ok = _check_task_budget(task_id, card_id, budget_override)
        if not budget_ok:
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
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Target list (default: Deployed/Done)"),
    auto_check: bool = typer.Option(False, "--auto-check",
                                    help="Auto-check all acceptance criteria (use with caution)"),
    strict: bool = typer.Option(True, "--strict/--no-strict",
                                help="Block if acceptance criteria unchecked (default: strict)"),
):
    """Complete a task (moves to Done list)."""

    # ENFORCEMENT: Block --no-strict when strict_ac_verification is enabled
    if not strict:
        import yaml
        try:
            from ..core.ops import find_paircoder_dir
            config_path = find_paircoder_dir() / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f) or {}
                strict_ac = config.get("enforcement", {}).get("strict_ac_verification", False)
                if strict_ac:
                    console.print(
                        "\n[red]❌ BLOCKED: --no-strict is disabled when strict_ac_verification is enabled.[/red]")
                    console.print("")
                    console.print("[yellow]You must verify acceptance criteria before completion:[/yellow]")
                    console.print(f"  1. Check items manually on Trello card")
                    console.print(f"  2. Use: [cyan]bpsai-pair ttask check {card_id} \"<item text>\"[/cyan]")
                    console.print(f"  3. Then: [cyan]bpsai-pair ttask done {card_id} --summary \"...\"[/cyan]")
                    console.print("")
                    console.print("[dim]This ensures all acceptance criteria are verified before completion.[/dim]")
                    raise typer.Exit(1)
        except (ImportError, FileNotFoundError):
            pass
    client, config = get_board_client()
    card, lst = client.find_card(card_id)

    if not card:
        console.print(f"[red]Card not found: {card_id}[/red]")
        raise typer.Exit(1)

    # Refresh card to get checklists
    try:
        card.fetch()
    except Exception:
        pass

        # Handle AC verification based on flags
        ac_status_msg = ""

        # AUTO-CHECK FIRST (if requested) - before strict verification
        if auto_check:
            checked_count = _auto_check_acceptance_criteria(card, client)
            if checked_count > 0:
                console.print(f"[green]✓ Auto-checked {checked_count} acceptance criteria item(s)[/green]")
                # Refresh card to get updated checklist state
                try:
                    card.fetch()
                except Exception:
                    pass

        # Now verify (strict mode or after auto-check)
        if strict:
            unchecked = _get_unchecked_ac_items(card)
            if unchecked:
                console.print(f"[red]❌ Cannot complete: {len(unchecked)} acceptance criteria item(s) unchecked[/red]")
                console.print("\n[dim]Unchecked items:[/dim]")
                for item in unchecked:
                    console.print(f"  ○ {item.get('name', '')}")
                console.print("\n[dim]Options:[/dim]")
                console.print(f"  1. Check items: [cyan]bpsai-pair ttask check {card_id} \"<item text>\"[/cyan]")
                console.print(f"  2. Check on Trello directly")
                if auto_check:
                    console.print(f"\n[yellow]Note: --auto-check ran but some items could not be checked.[/yellow]")
                raise typer.Exit(1)
            console.print("[green]✓ All acceptance criteria verified[/green]")
            ac_status_msg = "All AC items verified"
        else:
            # --no-strict: skip verification but log bypass
            unchecked = _get_unchecked_ac_items(card)
            if unchecked:
                console.print(f"[yellow]⚠ Completing with {len(unchecked)} unchecked AC item(s)[/yellow]")
                _log_bypass("ttask done", card_id, f"--no-strict with {len(unchecked)} unchecked AC items")
                ac_status_msg = f"Bypassed with {len(unchecked)} unchecked AC items (logged)"
            else:
                ac_status_msg = "AC verification skipped (all items already complete)"

    # Determine target list
    if list_name is None:
        list_name = config.get("trello", {}).get("lists", {}).get("review", "In Review")

    # Move to target list
    client.move_card(card, list_name)

    # Log activity with AC status
    completion_msg = f"{summary} | {ac_status_msg}"
    log_activity(card, "completed", completion_msg)

    console.print(f"[green]✓ Completed: {card.name}[/green]")
    console.print(f"  Moved to: {list_name}")
    console.print(f"  Summary: {summary}")

    # Auto-update local task file and run completion hooks
    try:
        success, task_id = _update_local_task_status(card, "done", summary)
        if success and task_id:
            console.print(f"[green]✓ Local task {task_id} updated to done[/green]")
            # Run completion hooks to update state.md
            _run_completion_hooks(task_id)
        elif task_id:
            console.print(f"[yellow]⚠ Could not update local task {task_id}[/yellow]")
        # If no task_id found, silently continue (card may not have local task)
    except FileNotFoundError as e:
        task_id = _get_task_id_from_card(card)
        if task_id:
            console.print(f"[yellow]⚠ Local task file not found for {task_id}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠ Could not sync local task: {e}[/yellow]")
        # Don't fail - Trello is source of truth


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


@app.command("check")
def check_item(
    task_id: str = typer.Argument(..., help="Task ID (e.g., TASK-089 or TRELLO-123)"),
    item_text: str = typer.Argument(..., help="Checklist item text (partial match OK)"),
    checklist_name: Optional[str] = typer.Option(None, "--checklist", "-c", help="Checklist name (default: search all)"),
):
    """Check off a checklist item as complete.

    Use this to mark acceptance criteria as done while working on a task.
    Partial text matching is supported - just provide enough to uniquely identify the item.

    Examples:
        bpsai-pair ttask check TASK-089 "No hardcoded credentials"
        bpsai-pair ttask check TASK-089 "SQL injection" --checklist "Acceptance Criteria"
    """
    import requests

    client, _ = get_board_client()
    card, _ = client.find_card(task_id)

    if not card:
        console.print(f"[red]Card not found: {task_id}[/red]")
        raise typer.Exit(1)

    # Refresh card to get checklists
    try:
        card.fetch()
    except Exception:
        pass

    if not card.checklists:
        console.print(f"[yellow]No checklists found on card: {task_id}[/yellow]")
        raise typer.Exit(1)

    # Search for the item
    found_item = None
    found_checklist = None
    item_text_lower = item_text.lower()

    for checklist in card.checklists:
        # Filter by checklist name if specified
        if checklist_name and checklist.name.lower() != checklist_name.lower():
            continue

        for item in checklist.items:
            item_name = item.get("name", "")
            if item_text_lower in item_name.lower():
                if found_item is not None:
                    # Multiple matches - need more specific text
                    console.print(f"[yellow]Multiple items match '{item_text}'. Be more specific.[/yellow]")
                    console.print(f"  Found: {found_item.get('name', '')}")
                    console.print(f"  Found: {item_name}")
                    raise typer.Exit(1)
                found_item = item
                found_checklist = checklist

    if not found_item:
        console.print(f"[red]Checklist item not found: {item_text}[/red]")
        console.print("\n[dim]Available items:[/dim]")
        for checklist in card.checklists:
            console.print(f"  [bold]{checklist.name}[/bold]")
            for item in checklist.items:
                check = "✓" if item.get("checked") else "○"
                console.print(f"    {check} {item.get('name', '')}")
        raise typer.Exit(1)

    # Check if already checked
    if found_item.get("checked"):
        console.print(f"[dim]Already checked: {found_item.get('name', '')}[/dim]")
        return

    # Check the item using py-trello's method
    try:
        # py-trello uses set_checklist_item method
        found_checklist.set_checklist_item(found_item.get("name"), checked=True)
        console.print(f"[green]✓ Checked: {found_item.get('name', '')}[/green]")

        # Log activity
        log_activity(card, "checked", found_item.get("name", "")[:50])
    except AttributeError:
        # Fallback: use direct API call if py-trello method not available
        try:
            from .auth import load_token
            creds = load_token()

            check_item_id = found_item.get("id")
            url = f"https://api.trello.com/1/cards/{card.id}/checkItem/{check_item_id}"

            response = requests.put(
                url,
                params={
                    "key": creds["api_key"],
                    "token": creds["token"],
                    "state": "complete"
                }
            )

            if response.status_code == 200:
                console.print(f"[green]✓ Checked: {found_item.get('name', '')}[/green]")
                log_activity(card, "checked", found_item.get("name", "")[:50])
            else:
                console.print(f"[red]Failed to check item: {response.status_code}[/red]")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error checking item: {e}[/red]")
            raise typer.Exit(1)


@app.command("uncheck")
def uncheck_item(
    task_id: str = typer.Argument(..., help="Task ID (e.g., TASK-089 or TRELLO-123)"),
    item_text: str = typer.Argument(..., help="Checklist item text (partial match OK)"),
    checklist_name: Optional[str] = typer.Option(None, "--checklist", "-c", help="Checklist name (default: search all)"),
):
    """Uncheck a checklist item (mark as incomplete).

    Use this if you need to undo a checked item.

    Examples:
        bpsai-pair ttask uncheck TASK-089 "No hardcoded credentials"
    """
    import requests

    client, _ = get_board_client()
    card, _ = client.find_card(task_id)

    if not card:
        console.print(f"[red]Card not found: {task_id}[/red]")
        raise typer.Exit(1)

    try:
        card.fetch()
    except Exception:
        pass

    if not card.checklists:
        console.print(f"[yellow]No checklists found on card: {task_id}[/yellow]")
        raise typer.Exit(1)

    # Search for the item
    found_item = None
    found_checklist = None
    item_text_lower = item_text.lower()

    for checklist in card.checklists:
        if checklist_name and checklist.name.lower() != checklist_name.lower():
            continue

        for item in checklist.items:
            item_name = item.get("name", "")
            if item_text_lower in item_name.lower():
                if found_item is not None:
                    console.print(f"[yellow]Multiple items match '{item_text}'. Be more specific.[/yellow]")
                    raise typer.Exit(1)
                found_item = item
                found_checklist = checklist

    if not found_item:
        console.print(f"[red]Checklist item not found: {item_text}[/red]")
        raise typer.Exit(1)

    if not found_item.get("checked"):
        console.print(f"[dim]Already unchecked: {found_item.get('name', '')}[/dim]")
        return

    try:
        found_checklist.set_checklist_item(found_item.get("name"), checked=False)
        console.print(f"[yellow]○ Unchecked: {found_item.get('name', '')}[/yellow]")
    except AttributeError:
        try:
            from .auth import load_token
            creds = load_token()

            check_item_id = found_item.get("id")
            url = f"https://api.trello.com/1/cards/{card.id}/checkItem/{check_item_id}"

            response = requests.put(
                url,
                params={
                    "key": creds["api_key"],
                    "token": creds["token"],
                    "state": "incomplete"
                }
            )

            if response.status_code == 200:
                console.print(f"[yellow]○ Unchecked: {found_item.get('name', '')}[/yellow]")
            else:
                console.print(f"[red]Failed to uncheck item: {response.status_code}[/red]")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error unchecking item: {e}[/red]")
            raise typer.Exit(1)


@app.command("comment")
def task_comment(
    task_id: str = typer.Argument(..., help="Task or Card ID (e.g., TASK-001 or TRELLO-123)"),
    message: str = typer.Argument(..., help="Comment message"),
):
    """Add a progress comment to a task.

    Uses structured activity logging with emojis and timestamps.
    """
    from .activity import TrelloActivityLogger

    client, _ = get_board_client()

    # Create activity logger for structured comments
    activity_logger = TrelloActivityLogger(client)

    # Try to log via activity logger (handles both TASK-XXX and TRELLO-XXX)
    success = activity_logger.log_progress(task_id, note=message)

    if success:
        console.print(f"[green]✓ Progress logged for: {task_id}[/green]")
        console.print(f"  📝 {message}")
    else:
        # Fall back to direct card lookup
        card, lst = client.find_card(task_id)

        if not card:
            console.print(f"[red]Card not found: {task_id}[/red]")
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
