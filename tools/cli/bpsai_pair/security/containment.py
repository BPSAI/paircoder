"""Containment manager for contained autonomy mode.

This module provides filesystem locking mechanisms that prevent writes to
protected directories and files during contained autonomy sessions.

Note: This is separate from the Docker sandbox system (security.sandbox).
The Docker sandbox provides process isolation, while containment provides
filesystem write protection for autonomous agent sessions.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Set, List

if TYPE_CHECKING:
    from bpsai_pair.core.config import ContainmentConfig


class ContainmentViolationError(Exception):
    """Raised when attempting to modify locked resources.

    This exception indicates that a write operation was attempted on a path
    that is protected in contained autonomy mode.
    """

    pass


class ContainmentManager:
    """Manages filesystem locking for contained autonomy mode.

    This class tracks which directories and files are locked (read-only)
    and provides methods to check if write operations are allowed.

    The manager must be activated for enforcement to take effect.
    When inactive, all write operations are permitted.

    Attributes:
        config: The ContainmentConfig specifying locked paths.
        project_root: The project root directory (resolved to absolute).
        _active: Whether containment is currently enforced.
        _locked_dirs: Set of resolved locked directory paths.
        _locked_paths: Set of resolved locked file paths.
    """

    def __init__(self, config: "ContainmentConfig", project_root: Path) -> None:
        """Initialize the containment manager.

        Args:
            config: The ContainmentConfig specifying locked paths.
            project_root: The project root directory.
        """
        self.config = config
        self.project_root = project_root.resolve()
        self._active = False
        self._locked_dirs: Set[Path] = set()
        self._locked_paths: Set[Path] = set()
        self._build_locked_paths()

    def _build_locked_paths(self) -> None:
        """Build the sets of resolved locked paths.

        Processes the locked_directories and locked_files from the config,
        resolving them to absolute paths and expanding any glob patterns.
        """
        # Process locked directories
        for dir_pattern in self.config.locked_directories:
            # Check if pattern contains glob characters
            if "*" in dir_pattern or "?" in dir_pattern or "[" in dir_pattern:
                # Expand glob pattern
                self._expand_dir_glob(dir_pattern)
            else:
                # Regular path - resolve relative to project root
                path = self.project_root / dir_pattern.rstrip("/")
                self._locked_dirs.add(path.resolve() if path.exists() else path)

        # Process locked files
        for file_path in self.config.locked_files:
            path = self.project_root / file_path
            # Resolve if exists, otherwise keep as-is (prevents creation)
            self._locked_paths.add(path.resolve() if path.exists() else path)

    def _expand_dir_glob(self, pattern: str) -> None:
        """Expand a glob pattern for directories.

        Args:
            pattern: Glob pattern like '.claude/*/' or 'protected/**/'
        """
        # Normalize pattern (remove trailing slash for glob)
        pattern = pattern.rstrip("/")

        # For ** patterns, we need to handle recursively
        if "**" in pattern:
            # Match pattern against existing directories
            base_pattern = pattern.replace("**", "*")
            for match in self.project_root.glob(pattern):
                if match.is_dir():
                    self._locked_dirs.add(match.resolve())
            # Also add the base pattern for non-existent paths
            # This ensures paths like protected/new_dir/file.md are blocked
            base = pattern.split("**")[0].rstrip("/")
            if base:
                base_path = self.project_root / base
                if base_path.exists():
                    self._locked_dirs.add(base_path.resolve())
        else:
            # Single-level glob
            for match in self.project_root.glob(pattern):
                if match.is_dir():
                    self._locked_dirs.add(match.resolve())

    def _resolve_path(self, path: Path) -> Path:
        """Resolve a path to absolute, following symlinks.

        Args:
            path: The path to resolve (can be relative or absolute).

        Returns:
            The resolved absolute path with symlinks followed.
        """
        # Make absolute relative to project root if needed
        if not path.is_absolute():
            path = self.project_root / path

        # Resolve symlinks and normalize the path
        # Use resolve() which follows symlinks
        try:
            return path.resolve()
        except (OSError, RuntimeError):
            # Handle broken symlinks or permission errors
            # Fall back to resolving without following symlinks
            return Path(path).absolute()

    def is_path_locked(self, path: Path) -> bool:
        """Check if a path is within a locked directory or is a locked file.

        This method resolves symlinks to prevent bypass attacks.

        Args:
            path: The path to check (can be relative or absolute).

        Returns:
            True if the path is locked, False otherwise.
        """
        resolved = self._resolve_path(path)

        # Check if path is a locked file
        if resolved in self._locked_paths:
            return True

        # Check for non-existent locked files (relative match)
        for locked_file in self._locked_paths:
            if not locked_file.exists():
                # For non-existent files, check if relative path matches
                rel_locked = locked_file.relative_to(self.project_root) if locked_file.is_relative_to(self.project_root) else locked_file
                try:
                    rel_path = resolved.relative_to(self.project_root)
                    if rel_path == rel_locked:
                        return True
                except ValueError:
                    pass

        # Check if path is within a locked directory
        for locked_dir in self._locked_dirs:
            if resolved == locked_dir:
                return True
            # Check if resolved path is under locked_dir
            try:
                resolved.relative_to(locked_dir)
                return True
            except ValueError:
                pass

        # Handle non-existent locked directories
        for locked_dir in self._locked_dirs:
            if not locked_dir.exists():
                # For non-existent dirs, do relative path comparison
                try:
                    rel_locked = locked_dir.relative_to(self.project_root)
                    rel_path = resolved.relative_to(self.project_root)
                    # Check if rel_path starts with rel_locked
                    rel_locked_parts = rel_locked.parts
                    rel_path_parts = rel_path.parts
                    if len(rel_path_parts) >= len(rel_locked_parts):
                        if rel_path_parts[:len(rel_locked_parts)] == rel_locked_parts:
                            return True
                except ValueError:
                    pass

        # Check for glob pattern matches (for ** patterns)
        for dir_pattern in self.config.locked_directories:
            if "**" in dir_pattern:
                # Check if path would match the pattern
                try:
                    rel_path = resolved.relative_to(self.project_root)
                    pattern = dir_pattern.rstrip("/")
                    # Convert ** to regex-like matching
                    if self._matches_glob_pattern(str(rel_path), pattern):
                        return True
                except ValueError:
                    pass

        return False

    def _matches_glob_pattern(self, path_str: str, pattern: str) -> bool:
        """Check if a path matches a glob pattern.

        Args:
            path_str: The path string to check.
            pattern: The glob pattern.

        Returns:
            True if the path matches the pattern.
        """
        # For ** patterns, check if path starts with the prefix
        if "**" in pattern:
            prefix = pattern.split("**")[0].rstrip("/")
            if prefix:
                return path_str.startswith(prefix + "/") or path_str == prefix
        return fnmatch.fnmatch(path_str, pattern)

    def check_write_allowed(self, path: Path) -> None:
        """Check if writing to a path is allowed.

        Args:
            path: The path to check.

        Raises:
            ContainmentViolationError: If the path is locked and manager is active.
        """
        if not self._active:
            return

        if self.is_path_locked(path):
            raise ContainmentViolationError(
                f"Cannot modify locked path: {path}\n"
                "This path is protected in contained autonomy mode."
            )

    def activate(self) -> None:
        """Activate containment enforcement.

        When active, check_write_allowed() will raise exceptions for locked paths.
        """
        self._active = True

    def deactivate(self) -> None:
        """Deactivate containment enforcement.

        When inactive, check_write_allowed() permits all writes.
        """
        self._active = False

    @property
    def is_active(self) -> bool:
        """Check if containment is currently active.

        Returns:
            True if containment is enforced, False otherwise.
        """
        return self._active

    @property
    def locked_directories(self) -> List[Path]:
        """Get the list of locked directories.

        Returns:
            List of resolved locked directory paths.
        """
        return list(self._locked_dirs)

    @property
    def locked_files(self) -> List[Path]:
        """Get the list of locked files.

        Returns:
            List of resolved locked file paths.
        """
        return list(self._locked_paths)
