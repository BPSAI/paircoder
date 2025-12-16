---
id: TASK-044
title: Add Trello integration tests
plan: plan-2025-01-paircoder-v2-upgrade
type: test
priority: P2
complexity: 40
status: pending
sprint: sprint-6
tags:
  - trello
  - testing
depends_on:
  - TASK-040
  - TASK-041
---

# Objective

Add unit and integration tests for the Trello integration commands to ensure reliability and prevent regressions.

# Implementation Plan

## 1. Create Test Fixtures

Create `tools/cli/tests/conftest_trello.py`:

```python
"""
Trello test fixtures and mocks.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import json
import tempfile


@pytest.fixture
def mock_trello_token(tmp_path):
    """Create mock token file."""
    tokens_dir = tmp_path / ".trello_codex_tokens"
    tokens_dir.mkdir()
    token_file = tokens_dir / "trello_token.json"
    token_file.write_text(json.dumps({
        "token": "test-token",
        "api_key": "test-api-key",
        "version": 2
    }))
    
    with patch('bpsai_pair.trello.auth.TOKENS_FOLDER', tokens_dir):
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            yield token_file


@pytest.fixture
def mock_trello_client():
    """Create mock TrelloService."""
    client = MagicMock()
    
    # Mock board
    mock_board = MagicMock()
    mock_board.id = "board-123"
    mock_board.name = "Test Board"
    mock_board.url = "https://trello.com/b/abc123"
    
    # Mock lists
    mock_sprint = MagicMock()
    mock_sprint.name = "Sprint"
    mock_sprint.id = "list-sprint"
    
    mock_progress = MagicMock()
    mock_progress.name = "In Progress"
    mock_progress.id = "list-progress"
    
    mock_done = MagicMock()
    mock_done.name = "Done"
    mock_done.id = "list-done"
    
    mock_board.all_lists.return_value = [mock_sprint, mock_progress, mock_done]
    
    # Mock cards
    mock_card = MagicMock()
    mock_card.id = "card-123"
    mock_card.short_id = 123
    mock_card.name = "Test Task"
    mock_card.description = "Test description"
    mock_card.url = "https://trello.com/c/xyz789"
    mock_card.labels = []
    mock_card.checklists = []
    mock_card.get_list.return_value = mock_sprint
    mock_card.get_custom_field_by_name.return_value = None
    
    mock_sprint.list_cards.return_value = [mock_card]
    mock_progress.list_cards.return_value = []
    mock_done.list_cards.return_value = []
    
    client.board = mock_board
    client.lists = {
        "Sprint": mock_sprint,
        "In Progress": mock_progress,
        "Done": mock_done,
    }
    client.healthcheck.return_value = True
    client.list_boards.return_value = [mock_board]
    client.set_board.return_value = mock_board
    client.get_board_lists.return_value = client.lists
    client.get_cards_in_list.side_effect = lambda name: client.lists.get(name, MagicMock()).list_cards()
    client.is_card_blocked.return_value = False
    
    return client, mock_card


@pytest.fixture
def mock_config(tmp_path):
    """Create mock config with Trello settings."""
    config_dir = tmp_path / ".paircoder"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    
    config = {
        "project_name": "test-project",
        "version": "2.1",
        "trello": {
            "enabled": True,
            "board_id": "board-123",
            "board_name": "Test Board",
            "lists": {
                "sprint": "Sprint",
                "in_progress": "In Progress",
                "done": "Done",
            }
        }
    }
    
    import yaml
    config_file.write_text(yaml.dump(config))
    
    return config_file, config
```

## 2. Test Auth Module

Create `tools/cli/tests/test_trello_auth.py`:

```python
"""Tests for Trello auth module."""
import pytest
import json
from pathlib import Path
from unittest.mock import patch

from bpsai_pair.trello.auth import (
    store_token,
    load_token,
    clear_token,
    is_connected,
)


class TestTrelloAuth:
    
    def test_store_and_load_token(self, tmp_path):
        """Test storing and loading credentials."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        token_file = tokens_dir / "trello_token.json"
        
        with patch('bpsai_pair.trello.auth.TOKENS_FOLDER', tokens_dir):
            with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
                # Store
                store_token(token="my-token", api_key="my-api-key")
                
                # Verify file created
                assert token_file.exists()
                
                # Load
                data = load_token()
                assert data["token"] == "my-token"
                assert data["api_key"] == "my-api-key"
                assert data["version"] == 2
    
    def test_load_token_missing_file(self, tmp_path):
        """Test loading when no token file exists."""
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', tmp_path / "nonexistent.json"):
            result = load_token()
            assert result is None
    
    def test_clear_token(self, tmp_path):
        """Test clearing credentials."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        tokens_dir.mkdir()
        token_file = tokens_dir / "trello_token.json"
        token_file.write_text('{"token": "test"}')
        
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            clear_token()
            assert not token_file.exists()
    
    def test_is_connected(self, mock_trello_token):
        """Test connection check."""
        assert is_connected() == True
    
    def test_is_not_connected(self, tmp_path):
        """Test connection check when not connected."""
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', tmp_path / "nonexistent.json"):
            assert is_connected() == False
```

## 3. Test CLI Commands

Create `tools/cli/tests/test_trello_commands.py`:

```python
"""Tests for Trello CLI commands."""
import pytest
from click.testing import CliRunner
from typer.testing import CliRunner as TyperRunner
from unittest.mock import patch, MagicMock

from bpsai_pair.trello.commands import app


class TestTrelloCommands:
    
    @pytest.fixture
    def runner(self):
        return TyperRunner()
    
    def test_status_not_connected(self, runner, tmp_path):
        """Test status when not connected."""
        with patch('bpsai_pair.trello.commands.is_connected', return_value=False):
            result = runner.invoke(app, ["status"])
            assert "Not connected" in result.output
    
    def test_status_connected(self, runner, mock_trello_token, mock_config):
        """Test status when connected."""
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.commands.is_connected', return_value=True):
            with patch('bpsai_pair.trello.commands.load_token', return_value={"token": "t", "api_key": "k"}):
                with patch('bpsai_pair.trello.commands.load_config', return_value=config):
                    result = runner.invoke(app, ["status"])
                    assert "Connected" in result.output
    
    def test_boards_list(self, runner, mock_trello_token, mock_trello_client):
        """Test listing boards."""
        client, _ = mock_trello_client
        
        with patch('bpsai_pair.trello.commands.get_client', return_value=client):
            result = runner.invoke(app, ["boards"])
            assert "Test Board" in result.output
    
    def test_use_board(self, runner, mock_trello_token, mock_trello_client, mock_config):
        """Test setting active board."""
        client, _ = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.commands.get_client', return_value=client):
            with patch('bpsai_pair.trello.commands.load_config', return_value=config):
                with patch('bpsai_pair.trello.commands.save_config'):
                    result = runner.invoke(app, ["use-board", "board-123"])
                    assert "Using board" in result.output
```

## 4. Test Task Commands

Create `tools/cli/tests/test_trello_tasks.py`:

```python
"""Tests for Trello task commands."""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from bpsai_pair.trello.task_commands import app


class TestTrelloTaskCommands:
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_task_list(self, runner, mock_trello_client, mock_config):
        """Test listing tasks."""
        client, mock_card = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "Test Task" in result.output
    
    def test_task_show(self, runner, mock_trello_client, mock_config):
        """Test showing task details."""
        client, mock_card = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            with patch('bpsai_pair.trello.task_commands.find_card', return_value=(mock_card, MagicMock())):
                result = runner.invoke(app, ["show", "TRELLO-123"])
                assert "Test Task" in result.output
    
    def test_task_start(self, runner, mock_trello_client, mock_config):
        """Test starting a task."""
        client, mock_card = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            with patch('bpsai_pair.trello.task_commands.find_card', return_value=(mock_card, MagicMock())):
                result = runner.invoke(app, ["start", "TRELLO-123"])
                assert "Started" in result.output
                client.move_card.assert_called()
    
    def test_task_done(self, runner, mock_trello_client, mock_config):
        """Test completing a task."""
        client, mock_card = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            with patch('bpsai_pair.trello.task_commands.find_card', return_value=(mock_card, MagicMock())):
                result = runner.invoke(app, ["done", "TRELLO-123", "--summary", "Finished"])
                assert "Completed" in result.output
    
    def test_task_block(self, runner, mock_trello_client, mock_config):
        """Test blocking a task."""
        client, mock_card = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            with patch('bpsai_pair.trello.task_commands.find_card', return_value=(mock_card, MagicMock())):
                result = runner.invoke(app, ["block", "TRELLO-123", "--reason", "Waiting on API"])
                assert "Blocked" in result.output
    
    def test_task_not_found(self, runner, mock_trello_client, mock_config):
        """Test error when task not found."""
        client, _ = mock_trello_client
        config_file, config = mock_config
        
        with patch('bpsai_pair.trello.task_commands.get_board_client', return_value=(client, config)):
            with patch('bpsai_pair.trello.task_commands.find_card', return_value=(None, None)):
                result = runner.invoke(app, ["show", "TRELLO-999"])
                assert "not found" in result.output
                assert result.exit_code != 0
```

## 5. Integration Test (Optional, requires real Trello)

Create `tools/cli/tests/test_trello_integration.py`:

```python
"""
Integration tests for Trello (requires real credentials).

Skip these in CI unless TRELLO_INTEGRATION_TEST=1 is set.
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("TRELLO_INTEGRATION_TEST") != "1",
    reason="Integration tests require TRELLO_INTEGRATION_TEST=1"
)


class TestTrelloIntegration:
    """Real Trello API tests - run manually."""
    
    def test_real_connection(self):
        """Test actual Trello connection."""
        from bpsai_pair.trello.auth import load_token
        from bpsai_pair.trello.client import TrelloService
        
        creds = load_token()
        assert creds is not None, "No Trello credentials found"
        
        client = TrelloService(api_key=creds["api_key"], token=creds["token"])
        assert client.healthcheck() == True
    
    def test_list_real_boards(self):
        """Test listing real boards."""
        from bpsai_pair.trello.auth import load_token
        from bpsai_pair.trello.client import TrelloService
        
        creds = load_token()
        client = TrelloService(api_key=creds["api_key"], token=creds["token"])
        
        boards = client.list_boards()
        assert len(boards) > 0
```

# Files to Create

| Action | File |
|--------|------|
| Create | `tools/cli/tests/conftest_trello.py` |
| Create | `tools/cli/tests/test_trello_auth.py` |
| Create | `tools/cli/tests/test_trello_commands.py` |
| Create | `tools/cli/tests/test_trello_tasks.py` |
| Create | `tools/cli/tests/test_trello_integration.py` |

# Acceptance Criteria

- [ ] Auth module has >90% test coverage
- [ ] CLI commands have >80% test coverage
- [ ] All tests pass with `pytest tools/cli/tests/test_trello*.py`
- [ ] Tests use mocks (no real Trello calls in CI)
- [ ] Integration tests skipped by default, runnable manually

# Verification

```bash
cd tools/cli

# Run all Trello tests
pytest tests/test_trello*.py -v

# Check coverage
pytest tests/test_trello*.py --cov=bpsai_pair.trello --cov-report=term-missing

# Run integration tests (requires real credentials)
TRELLO_INTEGRATION_TEST=1 pytest tests/test_trello_integration.py -v
```
