"""Tests for containment status display in bpsai-pair status command (T29.9)."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bpsai_pair.cli import app


runner = CliRunner()


class TestContainmentStatusDisplay:
    """Tests for containment section in status command output."""

    def test_status_hides_containment_when_not_configured(self):
        """Status should not show containment section when not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            # Create minimal .paircoder structure
            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            # Create state.md
            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            # Create config without containment enabled
            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: false
""")

            # Clear containment env vars to ensure not active
            env_without_containment = {
                k: v for k, v in os.environ.items()
                if not k.startswith("PAIRCODER_CONTAINMENT")
            }
            with patch.dict(os.environ, env_without_containment, clear=True):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    # Containment section should not appear
                    assert "Containment" not in result.output

    def test_status_shows_containment_configured_not_active(self):
        """Status should show containment in yellow when configured but not active."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            # Create config with containment enabled
            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: advisory
  readonly_directories:
    - .claude/skills/
    - tools/cli/security/
  readonly_files:
    - CLAUDE.md
  blocked_directories:
    - .secrets/
  blocked_files:
    - .env
  allow_network:
    - api.anthropic.com
    - github.com
""")

            # Clear containment env var to ensure not active
            with patch.dict(os.environ, {"PAIRCODER_CONTAINMENT": ""}, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    # Should show containment section
                    assert "Containment" in result.output
                    # Should indicate configured but not active
                    assert "CONFIGURED" in result.output or "configured" in result.output.lower()

    def test_status_shows_containment_active(self):
        """Status should show containment in green when active via env var."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: strict
  readonly_directories:
    - .claude/skills/
    - tools/cli/security/
  readonly_files:
    - CLAUDE.md
  blocked_directories:
    - .secrets/
  allow_network:
    - api.anthropic.com
""")

            # Set containment active via env var
            with patch.dict(os.environ, {
                "PAIRCODER_CONTAINMENT": "1",
                "PAIRCODER_CONTAINMENT_CHECKPOINT": "sandbox-20260113-143022"
            }, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    assert "Containment" in result.output
                    # Should show active state
                    assert "ACTIVE" in result.output or "active" in result.output.lower()
                    # Should show checkpoint
                    assert "sandbox-20260113-143022" in result.output

    def test_status_shows_path_counts(self):
        """Status should show correct counts for directories and files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: advisory
  readonly_directories:
    - .claude/skills/
    - tools/cli/security/
    - tools/cli/core/
  readonly_files:
    - CLAUDE.md
    - .paircoder/config.yaml
  blocked_directories:
    - .secrets/
  blocked_files:
    - .env
    - credentials.json
  allow_network:
    - api.anthropic.com
    - github.com
    - api.trello.com
""")

            with patch.dict(os.environ, {"PAIRCODER_CONTAINMENT": "1"}, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    # Should show directory counts (3 readonly + 1 blocked = 4)
                    assert "4" in result.output or "directories" in result.output.lower()
                    # Should show file counts (2 readonly + 2 blocked = 4)
                    assert "files" in result.output.lower()

    def test_status_shows_network_allowlist(self):
        """Status should show network restriction info when active."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: strict
  readonly_directories: []
  readonly_files: []
  allow_network:
    - api.anthropic.com
    - github.com
    - pypi.org
    - api.trello.com
""")

            with patch.dict(os.environ, {"PAIRCODER_CONTAINMENT": "1"}, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    # Should mention network and domain count
                    assert "Network" in result.output or "network" in result.output.lower()
                    assert "4" in result.output or "domains" in result.output.lower()

    def test_status_json_includes_containment(self):
        """Status --json should include containment data when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: strict
  readonly_directories:
    - .claude/skills/
  readonly_files:
    - CLAUDE.md
  blocked_directories:
    - .secrets/
  allow_network:
    - api.anthropic.com
    - github.com
""")

            with patch.dict(os.environ, {
                "PAIRCODER_CONTAINMENT": "1",
                "PAIRCODER_CONTAINMENT_CHECKPOINT": "test-checkpoint"
            }, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status", "--json"])
                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    # Should have containment section
                    assert "containment" in data
                    containment = data["containment"]
                    assert containment["enabled"] is True
                    assert containment["active"] is True
                    assert containment["checkpoint"] == "test-checkpoint"
                    assert containment["mode"] == "strict"
                    assert "readonly_dirs" in containment or "protected_dirs" in containment
                    assert "network_domains" in containment or "allowed_domains" in containment

    def test_status_json_excludes_containment_when_disabled(self):
        """Status --json should not include containment when not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: false
""")

            # Clear containment env vars to ensure not active
            env_without_containment = {
                k: v for k, v in os.environ.items()
                if not k.startswith("PAIRCODER_CONTAINMENT")
            }
            with patch.dict(os.environ, env_without_containment, clear=True):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status", "--json"])
                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    # Should not have containment section (or it should be null/empty)
                    assert "containment" not in data or data.get("containment") is None

    def test_status_shows_protected_paths_preview(self):
        """Status should show a preview of protected paths (not full list)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            git_dir = tmpdir / ".git"
            git_dir.mkdir()

            paircoder_dir = tmpdir / ".paircoder"
            paircoder_dir.mkdir()
            context_dir = paircoder_dir / "context"
            context_dir.mkdir()

            state_file = context_dir / "state.md"
            state_file.write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## What Was Just Done

- Initial setup

## What's Next

1. Continue work
""")

            config_file = paircoder_dir / "config.yaml"
            config_file.write_text("""version: "2.6"
project:
  name: Test Project
  primary_goal: Testing
containment:
  enabled: true
  mode: strict
  readonly_directories:
    - .claude/skills/
    - .claude/agents/
    - tools/cli/security/
  readonly_files:
    - CLAUDE.md
    - AGENTS.md
  blocked_directories: []
  blocked_files:
    - .env
  allow_network:
    - api.anthropic.com
""")

            with patch.dict(os.environ, {"PAIRCODER_CONTAINMENT": "1"}, clear=False):
                with patch("bpsai_pair.commands.core.repo_root", return_value=tmpdir):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 0
                    # Should show at least some protected paths
                    assert ".claude/skills/" in result.output or "Protected" in result.output
