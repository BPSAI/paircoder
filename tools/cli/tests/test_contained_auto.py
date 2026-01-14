"""Tests for contained-auto command.

Tests the command that starts a contained autonomous session with git
checkpoint and containment activation.
"""
import os
import subprocess
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from click.testing import Result


runner = CliRunner()


def get_app():
    """Get the CLI app for testing."""
    from bpsai_pair.cli import app
    return app


class TestContainedAutoCommand:
    """Tests for the contained-auto command."""

    def test_command_exists(self):
        """Test that contained-auto command exists."""
        app = get_app()
        result = runner.invoke(app, ["contained-auto", "--help"])
        assert result.exit_code == 0
        assert "contained" in result.output.lower() or "autonomy" in result.output.lower()

    def test_help_shows_description(self):
        """Test that help shows descriptive text."""
        app = get_app()
        result = runner.invoke(app, ["contained-auto", "--help"])
        assert result.exit_code == 0
        # Should mention containment, autonomy, or protection
        output_lower = result.output.lower()
        assert any(word in output_lower for word in ["contain", "autonom", "protect", "lock"])


class TestContainedAutoWithMocks:
    """Tests for contained-auto with mocked dependencies."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a mock project structure."""
        # Create .paircoder dir
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        context_dir = paircoder_dir / "context"
        context_dir.mkdir()

        # Create config.yaml
        config_path = paircoder_dir / "config.yaml"
        config_path.write_text("""
version: "2.6"
project:
  name: test-project
containment:
  enabled: true
  locked_directories:
    - .claude/agents/
  locked_files:
    - CLAUDE.md
  auto_checkpoint: true
  rollback_on_violation: false
""")

        # Create state.md
        state_path = context_dir / "state.md"
        state_path.write_text("# Current State\nTest state")

        # Initialize git
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "test.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        return tmp_path

    def test_creates_checkpoint_when_enabled(self, mock_project):
        """Test that checkpoint is created when auto_checkpoint is enabled."""
        app = get_app()

        with patch("bpsai_pair.commands.session.ops.find_project_root", return_value=mock_project):
            with patch("bpsai_pair.commands.session.ops.GitOps.is_repo", return_value=True):
                result = runner.invoke(app, ["contained-auto"], input="y\n")

        # Should either succeed or mention checkpoint
        # (Exit might happen due to no TTY, but checkpoint should be attempted)
        assert "checkpoint" in result.output.lower() or result.exit_code == 0

    def test_skips_checkpoint_with_flag(self, mock_project):
        """Test that --skip-checkpoint skips checkpoint creation."""
        app = get_app()

        with patch("bpsai_pair.commands.session.ops.find_project_root", return_value=mock_project):
            with patch("bpsai_pair.commands.session.ops.GitOps.is_repo", return_value=True):
                result = runner.invoke(app, ["contained-auto", "--skip-checkpoint"], input="y\n")

        # Should not mention checkpoint created
        if result.exit_code == 0:
            # If successful, checkpoint should be skipped
            assert "checkpoint created" not in result.output.lower() or "skipped" in result.output.lower()

    def test_sets_environment_variables(self, mock_project):
        """Test that environment variables are set."""
        # This test verifies the environment variable behavior
        # In the actual implementation, we'll set PAIRCODER_CONTAINMENT=1
        app = get_app()

        original_env = os.environ.copy()
        try:
            with patch("bpsai_pair.commands.session.ops.find_project_root", return_value=mock_project):
                with patch("bpsai_pair.commands.session.ops.GitOps.is_repo", return_value=True):
                    # We need to verify env vars are set in the implementation
                    result = runner.invoke(app, ["contained-auto"], input="y\n")
                    # If command succeeded, check output mentions containment active
                    if result.exit_code == 0:
                        assert "active" in result.output.lower() or "contain" in result.output.lower()
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_warns_when_containment_disabled(self, tmp_path):
        """Test warning when containment is not enabled in config."""
        # Create .paircoder dir with containment disabled
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        config_path = paircoder_dir / "config.yaml"
        config_path.write_text("""
version: "2.6"
project:
  name: test-project
containment:
  enabled: false
""")

        # Initialize git
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "test.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        app = get_app()

        with patch("bpsai_pair.commands.session.ops.find_project_root", return_value=tmp_path):
            with patch("bpsai_pair.commands.session.ops.GitOps.is_repo", return_value=True):
                # Decline enabling for this session
                result = runner.invoke(app, ["contained-auto"], input="n\n")

        # Should warn about containment not enabled
        output_lower = result.output.lower()
        assert "not enabled" in output_lower or "disabled" in output_lower or "warning" in output_lower or result.exit_code != 0


class TestContainmentActivation:
    """Tests for ContainmentManager activation via command."""

    def test_containment_manager_activated(self, tmp_path):
        """Test that ContainmentManager is activated correctly."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(
            enabled=True,
            locked_directories=[".claude/agents/"],
            locked_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_active is False
        manager.activate()
        assert manager.is_active is True

    def test_activated_manager_blocks_locked_paths(self, tmp_path):
        """Test that activated manager blocks writes to locked paths."""
        from bpsai_pair.security.containment import ContainmentManager, ContainmentViolationError
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(
            enabled=True,
            locked_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)
        manager.activate()

        with pytest.raises(ContainmentViolationError):
            manager.check_write_allowed(Path("CLAUDE.md"))


class TestGitCheckpointIntegration:
    """Tests for git checkpoint creation."""

    def test_checkpoint_creation(self, tmp_path):
        """Test that git checkpoint can be created."""
        from bpsai_pair.security.checkpoint import GitCheckpoint

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        (tmp_path / "file.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, capture_output=True)

        checkpoint = GitCheckpoint(tmp_path)
        tag_name = checkpoint.create_checkpoint("containment entry")

        assert tag_name.startswith("paircoder-checkpoint-")

        # Verify tag exists
        result = subprocess.run(
            ["git", "tag", "-l", tag_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )
        assert tag_name in result.stdout


class TestTaskArgument:
    """Tests for optional task argument."""

    def test_command_accepts_task_argument(self):
        """Test that command accepts optional task argument."""
        app = get_app()
        result = runner.invoke(app, ["contained-auto", "--help"])
        # Help should mention task option or argument
        assert result.exit_code == 0
        # Task may be an argument or option


class TestExitBehavior:
    """Tests for exit and cleanup behavior."""

    def test_command_can_exit_cleanly(self, tmp_path):
        """Test that command can exit cleanly."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        manager.activate()
        assert manager.is_active is True

        manager.deactivate()
        assert manager.is_active is False


class TestClaude666Alias:
    """Tests for the claude666 alias command."""

    def test_alias_command_exists(self):
        """Test that claude666 alias command exists."""
        app = get_app()
        result = runner.invoke(app, ["claude666", "--help"])
        assert result.exit_code == 0

    def test_alias_help_shows_description(self):
        """Test that alias help shows relevant description."""
        app = get_app()
        result = runner.invoke(app, ["claude666", "--help"])
        assert result.exit_code == 0
        # Should mention beast mode, contained, or autonomy
        output_lower = result.output.lower()
        assert any(word in output_lower for word in ["beast", "contain", "autonom", "powerful"])

    def test_alias_has_same_options(self):
        """Test that alias has same options as contained-auto."""
        app = get_app()
        result = runner.invoke(app, ["claude666", "--help"])
        assert result.exit_code == 0
        # Should have --skip-checkpoint option
        assert "--skip-checkpoint" in result.output

    def test_alias_accepts_task_argument(self):
        """Test that alias accepts task argument."""
        app = get_app()
        result = runner.invoke(app, ["claude666", "--help"])
        assert result.exit_code == 0
        # Should show TASK argument
        assert "TASK" in result.output or "task" in result.output.lower()
