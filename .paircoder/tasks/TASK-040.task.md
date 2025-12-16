---
id: TASK-040
title: Add Trello CLI commands to PairCoder
plan: plan-2025-01-paircoder-v2-upgrade
type: feature
priority: P0
complexity: 60
status: done
sprint: sprint-10
tags:
  - trello
  - cli
  - integration
---

# Objective

Add `bpsai-pair trello` command group for connecting to and managing Trello integration.

# Background

PairCoder currently uses file-based task management (`.paircoder/tasks/`). This task adds optional Trello integration as an alternative backend, sharing authentication with CodexAgent-Trello via `~/.trello_codex_tokens/`.

# Implementation Plan

## 1. Add Dependencies

Update `tools/cli/pyproject.toml`:
```toml
dependencies = [
    # ... existing deps
    "py-trello>=0.19.0",
]
```

## 2. Create Trello Auth Module

Create `tools/cli/bpsai_pair/trello/auth.py`:

```python
"""
Trello authentication - compatible with CodexAgent-Trello token storage.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any

TOKENS_FOLDER = Path.home() / ".trello_codex_tokens"
TOKEN_FILE = TOKENS_FOLDER / "trello_token.json"
TOKEN_STORE_VERSION = 2

def ensure_token_dir():
    TOKENS_FOLDER.mkdir(exist_ok=True)

def store_token(token: str, api_key: str) -> None:
    ensure_token_dir()
    payload = {
        "token": token,
        "api_key": api_key,
        "version": TOKEN_STORE_VERSION,
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(payload, f)

def load_token() -> Optional[Dict[str, Any]]:
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        if data.get("token") and data.get("api_key"):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None

def clear_token() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()

def is_connected() -> bool:
    return load_token() is not None
```

## 3. Create Trello Client Module

Create `tools/cli/bpsai_pair/trello/client.py`:

```python
"""
Trello client wrapper.
"""
from typing import List, Optional
from trello import TrelloClient, Card, List as TrelloList
import logging

logger = logging.getLogger(__name__)

class TrelloService:
    def __init__(self, api_key: str, token: str):
        self.client = TrelloClient(api_key=api_key, token=token)
        self.board = None
        self.lists: dict[str, TrelloList] = {}

    def healthcheck(self) -> bool:
        try:
            self.client.list_boards()
            return True
        except Exception:
            return False

    def list_boards(self):
        return self.client.list_boards()

    def set_board(self, board_id: str):
        self.board = self.client.get_board(board_id)
        self.lists = {lst.name: lst for lst in self.board.all_lists()}
        return self.board

    def get_board_lists(self) -> dict[str, TrelloList]:
        if not self.board:
            raise ValueError("Board not set")
        return self.lists

    def get_cards_in_list(self, list_name: str) -> List[Card]:
        lst = self.lists.get(list_name)
        if not lst:
            return []
        return lst.list_cards()

    def move_card(self, card: Card, list_name: str):
        target = self.lists.get(list_name)
        if not target:
            target = self.board.add_list(list_name)
            self.lists[list_name] = target
        card.change_list(target.id)

    def add_comment(self, card: Card, comment: str):
        card.comment(comment)

    def is_card_blocked(self, card: Card) -> bool:
        for checklist in card.checklists:
            if checklist.name == 'card dependencies':
                for item in checklist.items:
                    if not item['checked']:
                        return True
        return False
```

## 4. Create Trello CLI Commands

Create `tools/cli/bpsai_pair/trello/commands.py`:

```python
"""
Trello CLI commands for PairCoder.
"""
import typer
from rich.console import Console
from rich.table import Table

from .auth import load_token, store_token, clear_token, is_connected
from .client import TrelloService
from ..config import load_config, save_config

app = typer.Typer(name="trello", help="Trello integration commands")
console = Console()


def get_client() -> TrelloService:
    creds = load_token()
    if not creds:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)
    return TrelloService(api_key=creds["api_key"], token=creds["token"])


@app.command()
def connect(
    api_key: str = typer.Option(..., prompt=True, help="Trello API key"),
    token: str = typer.Option(..., prompt=True, hide_input=True, help="Trello token"),
):
    """Connect to Trello (validates and stores credentials)."""
    client = TrelloService(api_key=api_key, token=token)
    
    if not client.healthcheck():
        console.print("[red]Failed to validate Trello credentials[/red]")
        raise typer.Exit(1)
    
    store_token(token=token, api_key=api_key)
    console.print("[green]✓ Connected to Trello[/green]")


@app.command()
def status():
    """Check Trello connection status."""
    if is_connected():
        creds = load_token()
        console.print("[green]✓ Connected to Trello[/green]")
        
        config = load_config()
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
    boards = client.list_boards()
    
    table = Table(title="Trello Boards")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("URL")
    
    for board in boards:
        if not board.closed:
            table.add_row(board.id, board.name, board.url)
    
    console.print(table)


@app.command("use-board")
def use_board(board_id: str = typer.Argument(..., help="Board ID to use")):
    """Set the active Trello board for this project."""
    client = get_client()
    board = client.set_board(board_id)
    
    config = load_config()
    if "trello" not in config:
        config["trello"] = {}
    config["trello"]["board_id"] = board_id
    config["trello"]["board_name"] = board.name
    config["trello"]["enabled"] = True
    save_config(config)
    
    console.print(f"[green]✓ Using board: {board.name}[/green]")
    
    lists = client.get_board_lists()
    console.print(f"\nLists: {', '.join(lists.keys())}")


@app.command()
def lists():
    """Show lists on the active board."""
    config = load_config()
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
```

## 5. Register Commands in Main CLI

Update `tools/cli/bpsai_pair/cli.py`:

```python
# Add import
from .trello.commands import app as trello_app

# In CLI setup (after other command registrations)
app.add_typer(trello_app, name="trello")
```

## 6. Create Package Init

Create `tools/cli/bpsai_pair/trello/__init__.py`:

```python
"""Trello integration for PairCoder."""
from .auth import is_connected, load_token
from .client import TrelloService

__all__ = ["is_connected", "load_token", "TrelloService"]
```

# Files to Create/Modify

| Action | File |
|--------|------|
| Create | `tools/cli/bpsai_pair/trello/__init__.py` |
| Create | `tools/cli/bpsai_pair/trello/auth.py` |
| Create | `tools/cli/bpsai_pair/trello/client.py` |
| Create | `tools/cli/bpsai_pair/trello/commands.py` |
| Modify | `tools/cli/bpsai_pair/cli.py` |
| Modify | `tools/cli/pyproject.toml` |

# Acceptance Criteria

- [ ] `bpsai-pair trello connect` prompts for credentials and validates
- [ ] `bpsai-pair trello status` shows connection state
- [ ] `bpsai-pair trello boards` lists available boards
- [ ] `bpsai-pair trello use-board <id>` configures project
- [ ] `bpsai-pair trello lists` shows lists on configured board
- [ ] `bpsai-pair trello disconnect` removes credentials
- [ ] Credentials stored in `~/.trello_codex_tokens/` (shared with CodexAgent-Trello)

# Verification

```bash
# Install updated CLI
pip install -e tools/cli

# Test commands
bpsai-pair trello --help
bpsai-pair trello connect
bpsai-pair trello status
bpsai-pair trello boards
bpsai-pair trello use-board <board-id>
bpsai-pair trello lists
```
