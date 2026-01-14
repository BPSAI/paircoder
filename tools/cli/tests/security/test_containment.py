"""Tests for ContainmentManager class.

Tests the filesystem locking mechanism that prevents writes to protected
directories and files in contained autonomy mode.
"""
import pytest
from pathlib import Path
from unittest.mock import patch
import os


class TestContainmentViolationError:
    """Tests for ContainmentViolationError exception."""

    def test_error_is_exception(self):
        """Test that ContainmentViolationError is an Exception."""
        from bpsai_pair.security.containment import ContainmentViolationError

        error = ContainmentViolationError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"

    def test_error_includes_path_info(self):
        """Test that error can include path information."""
        from bpsai_pair.security.containment import ContainmentViolationError

        error = ContainmentViolationError(
            "Cannot modify locked path: /test/path\n"
            "This path is protected in contained autonomy mode."
        )
        assert "/test/path" in str(error)
        assert "protected" in str(error)


class TestContainmentManagerInit:
    """Tests for ContainmentManager initialization."""

    def test_init_with_config_and_root(self, tmp_path):
        """Test basic initialization."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        assert manager.config is config
        assert manager.project_root == tmp_path.resolve()
        assert manager._active is False

    def test_init_resolves_project_root(self, tmp_path):
        """Test that project root is resolved to absolute path."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        config = ContainmentConfig(enabled=True)
        # Use relative-style path (though tmp_path is absolute, test resolution)
        manager = ContainmentManager(config, subdir)

        assert manager.project_root.is_absolute()

    def test_init_builds_locked_paths(self, tmp_path):
        """Test that locked paths are built on initialization."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create directories and files
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Readonly paths should be built
        assert len(manager._readonly_dirs) > 0 or len(manager._readonly_paths) > 0


class TestIsPathLocked:
    """Tests for is_path_locked() method."""

    def test_locked_file_is_locked(self, tmp_path):
        """Test that a locked file is detected as locked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_path_locked(Path("CLAUDE.md")) is True

    def test_non_locked_file_is_not_locked(self, tmp_path):
        """Test that a non-locked file is not detected as locked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_path_locked(Path("src/main.py")) is False

    def test_file_in_locked_directory_is_locked(self, tmp_path):
        """Test that a file inside a locked directory is detected as locked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_path_locked(Path(".claude/agents/planner.md")) is True

    def test_file_outside_locked_directory_is_not_locked(self, tmp_path):
        """Test that a file outside locked directories is not locked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_path_locked(Path("src/main.py")) is False
        assert manager.is_path_locked(Path(".claude/settings.json")) is False

    def test_nested_file_in_locked_directory(self, tmp_path):
        """Test that deeply nested files in locked dirs are locked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Deeply nested path
        assert manager.is_path_locked(
            Path(".claude/agents/subdir/deeply/nested/file.md")
        ) is True

    def test_absolute_path_handling(self, tmp_path):
        """Test that absolute paths are handled correctly."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Both relative and absolute should work
        assert manager.is_path_locked(Path("CLAUDE.md")) is True
        assert manager.is_path_locked(tmp_path / "CLAUDE.md") is True


class TestSymlinkBypassPrevention:
    """Tests for symlink resolution to prevent bypass attacks."""

    def test_symlink_to_locked_file_is_blocked(self, tmp_path):
        """Test that symlinks pointing to locked files are blocked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create locked file
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("protected content")

        # Create symlink to locked file
        symlink = tmp_path / "link_to_claude.md"
        symlink.symlink_to(claude_md)

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Symlink should be detected as locked
        assert manager.is_path_locked(Path("link_to_claude.md")) is True

    def test_symlink_to_locked_directory_file_is_blocked(self, tmp_path):
        """Test that symlinks pointing into locked directories are blocked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create locked directory with a file
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "planner.md"
        agent_file.write_text("agent config")

        # Create symlink to file in locked directory
        symlink = tmp_path / "link_to_agent.md"
        symlink.symlink_to(agent_file)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Symlink should be detected as locked
        assert manager.is_path_locked(Path("link_to_agent.md")) is True

    def test_symlinked_directory_to_locked_directory(self, tmp_path):
        """Test that directory symlinks pointing to locked dirs are blocked."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create locked directory
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "planner.md").write_text("agent")

        # Create directory symlink
        symlinked_dir = tmp_path / "linked_agents"
        symlinked_dir.symlink_to(agents_dir)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Files accessed through symlinked directory should be blocked
        assert manager.is_path_locked(Path("linked_agents/planner.md")) is True


class TestGlobPatternSupport:
    """Tests for glob pattern support in readonly_directories."""

    def test_glob_pattern_star(self, tmp_path):
        """Test that * glob pattern matches directories."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create multiple directories
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        (tmp_path / ".claude" / "commands").mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/*/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # All subdirectories should be locked
        assert manager.is_path_locked(Path(".claude/agents/file.md")) is True
        assert manager.is_path_locked(Path(".claude/skills/file.md")) is True
        assert manager.is_path_locked(Path(".claude/commands/file.md")) is True

    def test_glob_pattern_double_star(self, tmp_path):
        """Test that ** glob pattern matches recursively."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Create nested directories
        deep_dir = tmp_path / "protected" / "deep" / "nested"
        deep_dir.mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=["protected/**/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # All nested paths should be locked
        assert manager.is_path_locked(Path("protected/file.md")) is True
        assert manager.is_path_locked(Path("protected/deep/file.md")) is True
        assert manager.is_path_locked(Path("protected/deep/nested/file.md")) is True


class TestCheckWriteAllowed:
    """Tests for check_write_allowed() method."""

    def test_raises_when_active_and_path_locked(self, tmp_path):
        """Test that exception is raised for locked paths when active."""
        from bpsai_pair.security.containment import (
            ContainmentManager,
            ContainmentViolationError,
        )
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)
        manager.activate()

        with pytest.raises(ContainmentViolationError) as exc_info:
            manager.check_write_allowed(Path("CLAUDE.md"))

        assert "CLAUDE.md" in str(exc_info.value)
        assert "read-only" in str(exc_info.value).lower() or "protected" in str(exc_info.value).lower()

    def test_no_exception_when_inactive(self, tmp_path):
        """Test that no exception is raised when manager is inactive."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)
        # Not activated

        # Should not raise
        manager.check_write_allowed(Path("CLAUDE.md"))

    def test_no_exception_for_non_locked_path(self, tmp_path):
        """Test that no exception is raised for non-locked paths."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)
        manager.activate()

        # Should not raise
        manager.check_write_allowed(Path("src/main.py"))


class TestActivateDeactivate:
    """Tests for activate() and deactivate() methods."""

    def test_activate_sets_active_flag(self, tmp_path):
        """Test that activate() sets the _active flag."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        assert manager._active is False
        manager.activate()
        assert manager._active is True

    def test_deactivate_clears_active_flag(self, tmp_path):
        """Test that deactivate() clears the _active flag."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        manager.activate()
        assert manager._active is True
        manager.deactivate()
        assert manager._active is False

    def test_is_active_property(self, tmp_path):
        """Test that is_active property reflects state."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        assert manager.is_active is False
        manager.activate()
        assert manager.is_active is True
        manager.deactivate()
        assert manager.is_active is False


class TestLockedDirProperty:
    """Tests for the locked directory/path properties."""

    def test_readonly_directories_returns_resolved_paths(self, tmp_path):
        """Test that readonly_directories property returns resolved paths."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        config = ContainmentConfig(
            enabled=True,
            readonly_directories=[".claude/agents/"],
        )
        manager = ContainmentManager(config, tmp_path)

        locked_dirs = manager.readonly_directories
        assert len(locked_dirs) >= 1
        # All paths should be absolute
        for path in locked_dirs:
            assert path.is_absolute()

    def test_readonly_files_returns_resolved_paths(self, tmp_path):
        """Test that readonly_files property returns resolved paths."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        readonly_files = manager.readonly_files
        assert len(readonly_files) >= 1
        # All paths should be absolute
        for path in readonly_files:
            assert path.is_absolute()


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_config(self, tmp_path):
        """Test with empty locked lists."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(enabled=True)
        manager = ContainmentManager(config, tmp_path)

        # Nothing should be locked
        assert manager.is_path_locked(Path("any/file.txt")) is False

    def test_non_existent_locked_directory(self, tmp_path):
        """Test handling of locked directories that don't exist."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Don't create the directory
        config = ContainmentConfig(
            enabled=True,
            readonly_directories=["nonexistent/"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Should still register as locked path (prevents creation)
        assert manager.is_path_locked(Path("nonexistent/file.txt")) is True

    def test_non_existent_locked_file(self, tmp_path):
        """Test handling of locked files that don't exist."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        # Don't create the file
        config = ContainmentConfig(
            enabled=True,
            readonly_files=["nonexistent.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Should still be locked (prevents creation)
        assert manager.is_path_locked(Path("nonexistent.md")) is True

    def test_path_traversal_attempt(self, tmp_path):
        """Test that path traversal attempts don't bypass locks."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("test")

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Path traversal should still resolve to locked file
        assert manager.is_path_locked(Path("subdir/../CLAUDE.md")) is True

    def test_path_outside_project_root(self, tmp_path):
        """Test that paths outside project root are handled safely."""
        from bpsai_pair.security.containment import ContainmentManager
        from bpsai_pair.core.config import ContainmentConfig

        config = ContainmentConfig(
            enabled=True,
            readonly_files=["CLAUDE.md"],
        )
        manager = ContainmentManager(config, tmp_path)

        # Path outside project shouldn't match
        assert manager.is_path_locked(Path("/etc/passwd")) is False
