---
id: TASK-43
title: Update config schema for Trello settings
plan: plan-2025-01-paircoder-v2-upgrade
type: feature
priority: P1
complexity: 30
status: pending
sprint: sprint-10
tags:
  - trello
  - config
depends_on:
  - TASK-040
---

# Objective

Update PairCoder's config schema to support Trello integration settings, including task backend selection and list mappings.

# Implementation Plan

## 1. Update Config Model

Modify `tools/cli/bpsai_pair/config.py` to add Trello schema:

```python
# Add to existing config handling

TRELLO_CONFIG_SCHEMA = {
    "enabled": bool,           # Is Trello backend active
    "board_id": str,           # Trello board ID
    "board_name": str,         # Board name (for display)
    "lists": {                 # Map status to list names
        "backlog": str,
        "sprint": str,
        "in_progress": str,
        "review": str,
        "done": str,
        "blocked": str,
    },
    "custom_fields": {         # Custom field names
        "agent_task": str,
        "priority": str,
    },
    "agent_identity": str,     # "claude" or "codex"
    "auto_sync": bool,         # Auto-update on status change
}

DEFAULT_TRELLO_CONFIG = {
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


def get_trello_config() -> dict:
    """Get Trello configuration with defaults."""
    config = load_config()
    trello = config.get("trello", {})
    
    # Merge with defaults
    result = DEFAULT_TRELLO_CONFIG.copy()
    result.update(trello)
    
    # Ensure nested dicts are merged
    for key in ["lists", "custom_fields"]:
        if key in trello:
            result[key] = {**DEFAULT_TRELLO_CONFIG[key], **trello[key]}
    
    return result


def set_trello_config(updates: dict) -> None:
    """Update Trello configuration."""
    config = load_config()
    
    if "trello" not in config:
        config["trello"] = DEFAULT_TRELLO_CONFIG.copy()
    
    # Deep merge updates
    for key, value in updates.items():
        if isinstance(value, dict) and key in config["trello"]:
            config["trello"][key].update(value)
        else:
            config["trello"][key] = value
    
    save_config(config)
```

## 2. Add Config CLI Commands

Add to `tools/cli/bpsai_pair/trello/commands.py`:

```python
@app.command("config")
def trello_config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    set_list: Optional[str] = typer.Option(None, "--set-list", help="Set list mapping (format: status=ListName)"),
    set_field: Optional[str] = typer.Option(None, "--set-field", help="Set custom field (format: field=FieldName)"),
    agent: Optional[str] = typer.Option(None, "--agent", help="Set agent identity (claude/codex)"),
):
    """View or modify Trello configuration."""
    from ..config import get_trello_config, set_trello_config
    
    if show or (not set_list and not set_field and not agent):
        config = get_trello_config()
        console.print("[bold]Trello Configuration[/bold]\n")
        console.print(f"Enabled: {config['enabled']}")
        console.print(f"Board: {config['board_name']} ({config['board_id']})")
        console.print(f"Agent: {config['agent_identity']}")
        console.print(f"Auto-sync: {config['auto_sync']}")
        console.print("\n[dim]List Mappings:[/dim]")
        for status, list_name in config['lists'].items():
            console.print(f"  {status}: {list_name}")
        console.print("\n[dim]Custom Fields:[/dim]")
        for field, name in config['custom_fields'].items():
            console.print(f"  {field}: {name}")
        return
    
    updates = {}
    
    if set_list:
        status, list_name = set_list.split("=", 1)
        updates["lists"] = {status: list_name}
        console.print(f"[green]✓ Set list mapping: {status} → {list_name}[/green]")
    
    if set_field:
        field, name = set_field.split("=", 1)
        updates["custom_fields"] = {field: name}
        console.print(f"[green]✓ Set custom field: {field} → {name}[/green]")
    
    if agent:
        if agent not in ["claude", "codex"]:
            console.print("[red]Agent must be 'claude' or 'codex'[/red]")
            raise typer.Exit(1)
        updates["agent_identity"] = agent
        console.print(f"[green]✓ Set agent identity: {agent}[/green]")
    
    if updates:
        set_trello_config(updates)
```

## 3. Update Config YAML Template

Update cookiecutter template `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/config.yaml`:

```yaml
# PairCoder Configuration
project_name: "{{ cookiecutter.project_name }}"
version: "2.1"

# Task management backend
# Options: "file" (default) or "trello"
tasks:
  backend: "file"

# Trello integration (when tasks.backend: "trello")
# Run `bpsai-pair trello connect` to set up
trello:
  enabled: false
  board_id: null
  board_name: null
  
  # Map PairCoder statuses to Trello list names
  lists:
    backlog: "Backlog"
    sprint: "Sprint"
    in_progress: "In Progress"
    review: "In Review"
    done: "Done"
    blocked: "Blocked"
  
  # Trello custom field names
  custom_fields:
    agent_task: "Agent Task"
    priority: "Priority"
  
  # Agent identification in comments
  agent_identity: "claude"
  
  # Auto-sync status changes to Trello
  auto_sync: true
```

## 4. Add Validation

Add config validation in `tools/cli/bpsai_pair/config.py`:

```python
def validate_trello_config(config: dict) -> list[str]:
    """Validate Trello configuration, return list of errors."""
    errors = []
    trello = config.get("trello", {})
    
    if trello.get("enabled"):
        if not trello.get("board_id"):
            errors.append("Trello enabled but no board_id configured")
        
        # Check required lists exist
        required_lists = ["sprint", "in_progress", "done"]
        for status in required_lists:
            if not trello.get("lists", {}).get(status):
                errors.append(f"Missing list mapping for '{status}'")
    
    return errors
```

# Files to Modify

| Action | File |
|--------|------|
| Modify | `tools/cli/bpsai_pair/config.py` |
| Modify | `tools/cli/bpsai_pair/trello/commands.py` |
| Modify | `tools/cli/bpsai_pair/data/cookiecutter-paircoder/.../config.yaml` |

# Acceptance Criteria

- [ ] `get_trello_config()` returns merged config with defaults
- [ ] `set_trello_config()` persists changes to config.yaml
- [ ] `bpsai-pair trello config --show` displays current settings
- [ ] `bpsai-pair trello config --set-list sprint=Active` updates mapping
- [ ] `bpsai-pair trello config --agent codex` changes agent identity
- [ ] Config validation catches missing required settings
- [ ] Cookiecutter template includes Trello config section

# Verification

```bash
# Check defaults
bpsai-pair trello config --show

# Customize list mapping
bpsai-pair trello config --set-list "in_progress=Working On"

# Verify persisted
cat .paircoder/config.yaml | grep -A 20 trello

# Test validation
bpsai-pair validate  # Should warn if trello enabled without board
```
