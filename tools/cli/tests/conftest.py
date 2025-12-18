"""Pytest configuration and shared fixtures for bpsai_pair tests."""
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

# Add the package directory to Python path
package_dir = Path(__file__).parent.parent
sys.path.insert(0, str(package_dir))


# =============================================================================
# Git Repository Fixtures
# =============================================================================

@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository.

    Returns:
        Path to the repository root
    """
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # Create initial commit
    (repo / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)

    return repo


@pytest.fixture
def initialized_repo(temp_repo):
    """Create a repo with PairCoder initialized (v2.1 structure).

    Returns:
        Path to the repository root with .paircoder initialized
    """
    # Create v2.1 structure
    context_dir = temp_repo / ".paircoder" / "context"
    context_dir.mkdir(parents=True)
    (temp_repo / ".paircoder" / "plans").mkdir()
    (temp_repo / ".paircoder" / "tasks").mkdir()
    (temp_repo / ".paircoder" / "flows").mkdir()

    (context_dir / "development.md").write_text("""# Development Log

**Phase:** Phase 1
**Primary Goal:** Test Goal

## Context Sync (AUTO-UPDATED)

Overall goal is: Test Goal
Last action was: Init
Next action will be: Test
Blockers: None
""")
    (context_dir / "project.md").write_text("# Test Project\n\nA test project.")
    (context_dir / "state.md").write_text("# Current State\n\nNo active tasks.")
    (context_dir / "workflow.md").write_text("# Workflow\n\nStandard workflow.")

    # Create config
    (temp_repo / ".paircoder" / "config.yaml").write_text("""version: "2.1"
project:
  name: TestProject
""")

    return temp_repo


# =============================================================================
# PairCoder Directory Fixtures
# =============================================================================

@pytest.fixture
def paircoder_dir(tmp_path):
    """Create standard .paircoder directory structure.

    Returns:
        Path to the .paircoder directory
    """
    pc_dir = tmp_path / ".paircoder"
    pc_dir.mkdir()
    (pc_dir / "context").mkdir()
    (pc_dir / "tasks").mkdir()
    (pc_dir / "plans").mkdir()
    (pc_dir / "flows").mkdir()

    # Create a .git directory to simulate a git repo
    (tmp_path / ".git").mkdir()

    return pc_dir


@pytest.fixture
def paircoder_dir_with_config(paircoder_dir):
    """Create .paircoder directory with basic config.

    Returns:
        Path to the .paircoder directory with config.yaml
    """
    config_content = """version: "2.1"
project:
  name: TestProject
  description: A test project
"""
    (paircoder_dir / "config.yaml").write_text(config_content)
    return paircoder_dir


# =============================================================================
# Trello Fixtures
# =============================================================================

@pytest.fixture
def mock_trello_module():
    """Mock the py-trello module.

    Yields:
        Tuple of (mock_client_class, mock_client_instance)
    """
    mock_client_class = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance

    with patch.dict('sys.modules', {'trello': MagicMock(TrelloClient=mock_client_class)}):
        yield mock_client_class, mock_client_instance


@pytest.fixture
def mock_trello_service():
    """Create a mock TrelloService with common defaults.

    Returns:
        Mock TrelloService instance
    """
    service = Mock()
    service.board = Mock()
    service.lists = {}

    # Common return values
    service.get_custom_fields.return_value = []
    service.get_labels.return_value = []
    service.set_effort_field.return_value = True
    service.find_card_with_prefix.return_value = (None, None)
    service.get_checklist_by_name.return_value = None
    service.ensure_label_exists.return_value = Mock(id="label123")
    service.add_label_to_card.return_value = True

    # Card creation
    mock_card = Mock()
    mock_card.id = "card123"
    mock_card.name = "Test Card"
    mock_card.short_id = 123
    service.create_card_with_custom_fields.return_value = mock_card

    return service


@pytest.fixture
def mock_trello_card():
    """Create a mock Trello card with common attributes.

    Returns:
        Mock card object
    """
    card = Mock()
    card.id = "card123"
    card.name = "[TASK-001] Test task"
    card.short_id = 123
    card.description = "Test description"
    card.url = "https://trello.com/c/card123"
    card.checklists = []
    card.labels = []

    mock_list = Mock()
    mock_list.name = "In Progress"
    card.get_list.return_value = mock_list

    return card


@pytest.fixture
def mock_trello_task():
    """Create a mock task for Trello sync tests.

    Returns:
        Mock task object
    """
    task = Mock()
    task.id = "TASK-001"
    task.title = "Test task"
    task.body = ""
    task.status = Mock()
    task.status.value = "pending"
    task.priority = "P1"
    task.complexity = 30
    task.tags = []
    task.plan = None
    task.sprint = None
    task.objective = "Test objective"
    task.depends_on = []
    task.due_date = None
    return task


# =============================================================================
# MCP Server Fixtures
# =============================================================================

@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server that captures registered tools.

    Returns:
        Mock server with tool registration capability
    """
    server = MagicMock()
    registered_tools = {}

    def tool_decorator():
        def decorator(func):
            registered_tools[func.__name__] = func
            return func
        return decorator

    server.tool = tool_decorator
    server._registered_tools = registered_tools
    return server


# =============================================================================
# Security Module Fixtures
# =============================================================================

@pytest.fixture
def secret_scanner():
    """Create a SecretScanner instance.

    Returns:
        SecretScanner instance
    """
    from bpsai_pair.security.secrets import SecretScanner
    return SecretScanner()


@pytest.fixture
def secret_scanner_with_allowlist(tmp_path):
    """Create a SecretScanner with an allowlist config.

    Returns:
        Tuple of (SecretScanner, allowlist_path)
    """
    from bpsai_pair.security.secrets import SecretScanner, AllowlistConfig

    allowlist_path = tmp_path / "allowlist.yaml"
    allowlist_path.write_text("""
patterns:
  - "EXAMPLE"
  - "test_.*"
files:
  - "*.test.py"
  - "conftest.py"
""")

    allowlist = AllowlistConfig.from_yaml(allowlist_path)
    scanner = SecretScanner(allowlist=allowlist)
    return scanner, allowlist_path


@pytest.fixture
def dependency_scanner():
    """Create a DependencyScanner instance.

    Returns:
        DependencyScanner instance
    """
    from bpsai_pair.security.dependencies import DependencyScanner
    return DependencyScanner()


@pytest.fixture
def dependency_scanner_with_cache(tmp_path):
    """Create a DependencyScanner with custom cache directory.

    Returns:
        DependencyScanner instance with cache in tmp_path
    """
    from bpsai_pair.security.dependencies import DependencyScanner
    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()
    return DependencyScanner(cache_dir=cache_dir)


# =============================================================================
# Flow Fixtures
# =============================================================================

@pytest.fixture
def sample_flow_file(tmp_path):
    """Create a sample flow file.

    Returns:
        Path to the flow file
    """
    flows_dir = tmp_path / ".paircoder" / "flows"
    flows_dir.mkdir(parents=True)

    flow_content = """---
name: test-flow
description: A test flow
triggers:
  - test
  - debug
steps:
  - id: step1
    name: First Step
    action: echo "Step 1"
  - id: step2
    name: Second Step
    action: echo "Step 2"
    depends_on: [step1]
---

# Test Flow

This is a test flow for unit testing.

## Steps

1. First Step - Initial action
2. Second Step - Depends on first step
"""
    flow_file = flows_dir / "test.flow.md"
    flow_file.write_text(flow_content)
    return flow_file


@pytest.fixture
def sample_skill_file(tmp_path):
    """Create a sample skill file.

    Returns:
        Path to the skill file
    """
    skills_dir = tmp_path / ".paircoder" / "skills"
    skills_dir.mkdir(parents=True)

    skill_content = """---
name: test-skill
description: A test skill
triggers:
  - test
  - debug
---

# Test Skill

This is a test skill for unit testing.
"""
    skill_file = skills_dir / "test.skill.md"
    skill_file.write_text(skill_content)
    return skill_file


# =============================================================================
# Task/Plan Fixtures
# =============================================================================

@pytest.fixture
def basic_task_file(paircoder_dir):
    """Create a basic task file for general testing.

    Note: For MCP-specific tests, use sample_task_file from conftest_mcp.py

    Returns:
        Path to the task file
    """
    task_content = """---
id: TASK-001
title: Test Task
status: pending
priority: P1
complexity: 30
plan: test-plan
sprint: sprint-1
tags:
  - test
  - backend
depends_on: []
---

# Test Task

## Objective

This is a test task objective.

## Acceptance Criteria

- [ ] First criterion
- [ ] Second criterion
- [ ] Third criterion

## Implementation Notes

Some implementation notes here.
"""
    task_file = paircoder_dir / "tasks" / "TASK-001.task.md"
    task_file.write_text(task_content)
    return task_file


@pytest.fixture
def basic_plan_file(paircoder_dir):
    """Create a basic plan file for general testing.

    Note: For MCP-specific tests, use sample_plan_file from conftest_mcp.py

    Returns:
        Path to the plan file
    """
    plan_content = """---
id: plan-test-feature
title: Test Feature Plan
status: in_progress
type: feature
created: 2025-01-01
sprints:
  - id: sprint-1
    name: Sprint 1
    status: active
---

# Test Feature Plan

## Goals

1. Implement test feature
2. Add unit tests
3. Document the feature

## Tasks

- TASK-001: Test Task
"""
    plan_file = paircoder_dir / "plans" / "plan-test-feature.plan.yaml"
    plan_file.write_text(plan_content)
    return plan_file


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def change_to_tmp(tmp_path, monkeypatch):
    """Change working directory to tmp_path for the test.

    Returns:
        The tmp_path that is now the current directory
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for command execution tests.

    Yields:
        The mock object
    """
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
        yield mock_run
