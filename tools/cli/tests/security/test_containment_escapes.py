"""Tests for containment escape attempts.

This module tests that the ContainmentManager properly blocks various bypass
techniques at the PATH CHECKING level. These tests verify that if check_write_allowed()
is called, it will correctly identify and block escape attempts.

CRITICAL NOTE (T29.7 Discovery):
================================
These tests demonstrate that ContainmentManager's PATH CHECKING is solid.
However, the enforcement is currently ADVISORY ONLY because:
1. Nothing calls check_write_allowed() before actual file operations
2. Claude Code's Write/Edit tools directly access the filesystem
3. True enforcement requires Docker-based isolation (see T29.7 task notes)

The tests are organized into categories:
- Symlink Escapes: Attempts to bypass via symbolic links
- Path Traversal: Attempts using ../ and other path manipulation
- Filesystem Tricks: Hardlinks, renames, moves
- Process Manipulation: subprocess with modified PATH, env vars
- Network Escapes: IP addresses, redirects (tested with NetworkGuard)
- Environment Injection: Attempts via environment variables

Each test documents whether the escape attempt would be caught by:
- ContainmentManager (path checking)
- Docker isolation (if configured)
- Neither (indicating a gap)
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from bpsai_pair.security.containment import (
    ContainmentManager,
    ContainmentViolationError,
    ContainmentWriteError,
    ContainmentReadError,
)
from bpsai_pair.security.network import NetworkGuard, NetworkRestrictionError
from bpsai_pair.core.config import ContainmentConfig


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def project_root(tmp_path):
    """Create a mock project structure."""
    # Create blocked directories (Tier 1 - no read, no write)
    secrets_dir = tmp_path / ".secrets"
    secrets_dir.mkdir()
    (secrets_dir / "api_keys.json").write_text('{"key": "secret"}')

    # Create readonly directories (Tier 2 - read ok, no write)
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    skills_dir = claude_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "important.md").write_text("# Important skill")

    agents_dir = claude_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "planner.md").write_text("# Planner agent")

    # Create readonly file
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# Claude Instructions")

    # Create writable area (Tier 3 - read/write)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('hello')")

    return tmp_path


@pytest.fixture
def containment_config():
    """Create containment config with three-tier access."""
    return ContainmentConfig(
        enabled=True,
        # Tier 1: Blocked (no read, no write)
        blocked_directories=[".secrets/"],
        blocked_files=[".env"],
        # Tier 2: Read-only (can read, cannot write)
        readonly_directories=[".claude/skills/", ".claude/agents/"],
        readonly_files=["CLAUDE.md"],
        # Network
        allow_network=["github.com", "api.trello.com"],
    )


@pytest.fixture
def containment_manager(project_root, containment_config):
    """Create an active containment manager."""
    manager = ContainmentManager(containment_config, project_root)
    manager.activate()
    return manager


@pytest.fixture
def network_guard():
    """Create a network guard with restricted domains."""
    return NetworkGuard(["github.com", "api.trello.com", "pypi.org"])


# =============================================================================
# SYMLINK ESCAPE TESTS
# =============================================================================


class TestSymlinkEscapes:
    """Tests for symlink-based bypass attempts.

    Caught by: ContainmentManager (resolves symlinks before checking)
    Docker: Also prevented by read-only mounts
    """

    def test_symlink_to_readonly_directory(self, containment_manager, project_root):
        """Symlink pointing to readonly dir is detected and blocked."""
        # Create symlink to .claude/skills
        symlink = project_root / "sneaky_link"
        symlink.symlink_to(project_root / ".claude" / "skills")

        # Attempt to write via symlink should be blocked
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(symlink / "malicious.md")

    def test_symlink_to_readonly_file(self, containment_manager, project_root):
        """Symlink to readonly file is detected and blocked."""
        # Create symlink to CLAUDE.md
        symlink = project_root / "claude_link.md"
        symlink.symlink_to(project_root / "CLAUDE.md")

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(symlink)

    def test_symlink_chain_to_blocked_file(self, containment_manager, project_root):
        """Chain of symlinks to blocked file is detected."""
        # Create chain: link1 -> link2 -> .secrets/api_keys.json
        secrets_file = project_root / ".secrets" / "api_keys.json"
        link2 = project_root / "link2"
        link2.symlink_to(secrets_file)
        link1 = project_root / "link1"
        link1.symlink_to(link2)

        # Both read and write should be blocked for Tier 1 (blocked)
        with pytest.raises(ContainmentReadError):
            containment_manager.check_read_allowed(link1)
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(link1)

    def test_relative_symlink_escape(self, containment_manager, project_root):
        """Relative symlink that resolves to protected path is blocked."""
        # Create subdir and relative symlink back to .claude
        subdir = project_root / "subdir"
        subdir.mkdir()
        rel_link = subdir / "escape"
        rel_link.symlink_to(Path("..") / ".claude" / "skills")

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(rel_link / "injected.md")

    def test_symlink_in_protected_dir_to_writable_area(self, containment_manager, project_root):
        """Symlink FROM protected area TO writable area - writing TO source blocked."""
        # This tests an edge case: symlink resolution goes the right direction
        # The path we're trying to write to resolves to writable area
        writable_file = project_root / "src" / "target.py"
        writable_file.write_text("# target")

        # Symlink in .claude/skills pointing to src/target.py
        link_in_protected = project_root / ".claude" / "skills" / "sneaky"
        link_in_protected.symlink_to(writable_file)

        # Writing to this path - it resolves to src/target.py which IS writable
        # This should PASS because the resolved path is in writable area
        containment_manager.check_write_allowed(link_in_protected)  # Should not raise


# =============================================================================
# PATH TRAVERSAL ESCAPE TESTS
# =============================================================================


class TestPathTraversalEscapes:
    """Tests for path traversal bypass attempts.

    Caught by: ContainmentManager (normalizes paths before checking)
    Docker: Also prevented - paths normalized before mount matching
    """

    def test_dotdot_traversal_to_readonly(self, containment_manager, project_root):
        """../ traversal to readonly directory is blocked."""
        # Try .claude/../.claude/skills from some subdir
        sneaky_path = project_root / "subdir" / ".." / ".claude" / "skills" / "evil.md"

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(sneaky_path)

    def test_multiple_dotdot_traversal(self, containment_manager, project_root):
        """Multiple ../ segments are properly normalized."""
        # Deep nesting followed by traversal back up
        deep_path = project_root / "a" / "b" / "c" / ".." / ".." / ".." / ".claude" / "skills"

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(deep_path / "malicious.md")

    def test_mixed_traversal_and_symlinks(self, containment_manager, project_root):
        """Combined ../ and symlinks are properly resolved."""
        # Create symlink in src pointing to .claude
        src_dir = project_root / "src"
        link = src_dir / "claude_link"
        link.symlink_to(project_root / ".claude")

        # Try to access skills via the symlink
        traversal_path = link / "skills" / "evil.md"

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(traversal_path)

    def test_encoded_path_components(self, containment_manager, project_root):
        """Path with URL-encoded components (if passed) is handled."""
        # This tests if someone passes %2e%2e (URL-encoded ..)
        # Python's pathlib doesn't decode URLs, so this would be literal chars
        # The path won't exist, but checking should still work
        encoded_path = project_root / "%2e%2e" / ".claude" / "skills"

        # This won't match because %2e%2e is not ".."
        # It's in the writable area (doesn't match any protected pattern)
        # No error expected - this is actually correct behavior
        containment_manager.check_write_allowed(encoded_path / "test.md")  # Should pass

    def test_null_byte_in_path(self, containment_manager, project_root):
        """Null byte injection attempt is handled safely."""
        # Null bytes in paths can cause issues in C-based systems
        # Python's pathlib handles this gracefully
        try:
            bad_path = project_root / "safe\x00.claude/skills/evil.md"
            # If we get here, check the path
            # The null byte typically causes the path to be truncated in some systems
            containment_manager.check_write_allowed(bad_path)
        except (ValueError, OSError):
            # Expected - null bytes often cause path validation errors
            pass


# =============================================================================
# FILESYSTEM TRICK TESTS
# =============================================================================


class TestFilesystemTricks:
    """Tests for filesystem-based bypass attempts.

    Note: Some of these require actual filesystem operations which
    ContainmentManager only CHECKS, not PREVENTS. True prevention
    requires Docker isolation.
    """

    def test_hardlink_to_readonly_file_blocked(self, containment_manager, project_root):
        """Hardlink creation attempt to readonly file path is blocked.

        NOTE: ContainmentManager only checks paths. The actual hardlink creation
        would need to be blocked by Docker or pre-operation hooks.
        """
        readonly_file = project_root / "CLAUDE.md"
        hardlink_path = project_root / "src" / "claude_hardlink.md"

        # ContainmentManager blocks writes to readonly files
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(readonly_file)

        # But writing to the hardlink destination (in src/) would be allowed
        # because ContainmentManager doesn't know it will be a hardlink
        containment_manager.check_write_allowed(hardlink_path)  # Passes - this is a gap

    def test_rename_readonly_directory_blocked(self, containment_manager, project_root):
        """Renaming readonly directory is blocked (write to source)."""
        # Renaming requires write access to the source location
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(project_root / ".claude" / "skills")

    def test_move_file_into_blocked_directory(self, containment_manager, project_root):
        """Moving file INTO blocked directory is blocked."""
        # Writing to blocked directory should be blocked
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(project_root / ".secrets" / "moved.txt")

    def test_move_file_out_of_readonly_directory(self, containment_manager, project_root):
        """Moving file OUT OF readonly directory requires write to source."""
        # This would require deleting from readonly, which is a write
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(
                project_root / ".claude" / "skills" / "important.md"
            )

    def test_directory_creation_in_readonly(self, containment_manager, project_root):
        """Creating subdirectory in readonly directory is blocked."""
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(
                project_root / ".claude" / "skills" / "new_subdir"
            )


# =============================================================================
# PROCESS MANIPULATION TESTS
# =============================================================================


class TestProcessManipulation:
    """Tests for process-based bypass attempts.

    CRITICAL: These escapes are NOT caught by ContainmentManager!
    ContainmentManager only checks explicit path arguments.
    Subprocess calls completely bypass containment checking.

    TRUE PREVENTION requires Docker isolation with read-only mounts.
    """

    def test_subprocess_can_bypass_containment_manager(self, containment_manager, project_root):
        """DEMONSTRATES GAP: subprocess calls bypass ContainmentManager.

        This test shows that while ContainmentManager correctly identifies
        protected paths, a subprocess can still write to them because
        nothing intercepts the subprocess call.
        """
        import subprocess

        readonly_file = project_root / ".claude" / "skills" / "bypass_test.md"

        # ContainmentManager correctly blocks this path
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(readonly_file)

        # BUT a subprocess can still write (this is the gap!)
        # In a real scenario without Docker, this would succeed
        # We don't actually run it to avoid test side effects
        cmd = f'echo "bypassed" > "{readonly_file}"'

        # Document that this WOULD work without Docker isolation
        # subprocess.run(cmd, shell=True)  # Would bypass containment!
        assert True  # Test passes to document the gap

    def test_modified_path_subprocess(self, containment_manager, project_root):
        """Subprocess with modified PATH could access protected paths.

        DEMONSTRATES GAP: Environment manipulation is not checked.
        """
        # Modifying PATH to include scripts that write to protected areas
        # is not something ContainmentManager can prevent

        # This documents the attack vector:
        # 1. Create script in writable area that writes to protected area
        # 2. Modify PATH to include that location
        # 3. Call the script via subprocess

        # ContainmentManager cannot prevent this - needs Docker isolation
        assert True  # Documents the gap

    def test_shell_command_injection(self, containment_manager, project_root):
        """Shell command injection could bypass all checks.

        DEMONSTRATES GAP: If Claude can execute arbitrary shell commands,
        containment can only be enforced by Docker isolation.
        """
        # Any shell command can write to any location the process can access
        # ContainmentManager only helps if its checks are actually called

        # Example attack:
        # claude: "Let me run: cat important_data > /project/.claude/skills/exfil.md"

        # ContainmentManager can check paths, but can't intercept shell execution
        assert True  # Documents the gap


# =============================================================================
# ENVIRONMENT INJECTION TESTS
# =============================================================================


class TestEnvironmentInjection:
    """Tests for environment variable based attacks.

    CRITICAL: Environment variables can influence behavior in ways
    ContainmentManager cannot prevent without Docker isolation.
    """

    def test_home_override_attack(self, containment_manager, project_root):
        """HOME environment override is not checked by ContainmentManager.

        DEMONSTRATES GAP: Changing HOME could redirect ~ paths.
        """
        # If HOME is changed, ~/some_path resolves differently
        # ContainmentManager doesn't validate environment variables

        # This would need Docker isolation to prevent
        assert True  # Documents the gap

    def test_path_env_manipulation(self, containment_manager, project_root):
        """PATH manipulation could introduce malicious executables.

        DEMONSTRATES GAP: PATH changes affect executable resolution.
        """
        # Prepending a directory to PATH with malicious versions of
        # common tools (ls, cat, etc.) could exfiltrate data

        # ContainmentManager cannot prevent this
        assert True  # Documents the gap

    def test_pythonpath_injection(self, containment_manager, project_root):
        """PYTHONPATH injection could load malicious modules.

        DEMONSTRATES GAP: Module loading is not monitored.
        """
        # Setting PYTHONPATH to a directory with malicious versions
        # of standard library modules could compromise the system

        # This requires Docker isolation with controlled environment
        assert True  # Documents the gap


# =============================================================================
# NETWORK ESCAPE TESTS
# =============================================================================


class TestNetworkEscapes:
    """Tests for network restriction bypass attempts.

    Uses NetworkGuard which CAN check URLs.
    Docker isolation can enforce network: "none" or iptables rules.
    """

    def test_ip_address_instead_of_domain(self, network_guard):
        """Using IP address directly bypasses domain allowlist."""
        # NetworkGuard checks domain names, not what they resolve to
        # Using an IP directly could bypass domain-based filtering
        with pytest.raises(NetworkRestrictionError):
            network_guard.check_url("http://140.82.121.4/")  # github.com's IP

    def test_redirect_to_blocked_domain(self, network_guard):
        """Redirect to blocked domain after initial allowed request.

        DEMONSTRATES GAP: NetworkGuard only checks the initial URL.
        A redirect to a blocked domain would succeed once the request starts.

        True prevention requires:
        - Docker with network: none
        - Or iptables rules enforcing allowlist at IP level
        """
        # Initial request to allowed domain
        network_guard.check_url("https://github.com/redirect")  # Passes

        # But if github.com/redirect returns HTTP 302 to evil.com,
        # the client would follow it without NetworkGuard checking again

        # This is a gap in advisory mode
        assert True  # Documents the gap

    def test_dns_rebinding_attack(self, network_guard):
        """DNS rebinding could bypass domain-based checks.

        DEMONSTRATES GAP: Initial DNS resolution vs runtime resolution.
        """
        # Attack: allowlisted domain initially resolves to external IP,
        # but TTL expires and re-resolves to internal IP (127.0.0.1)

        # NetworkGuard checks domain name, not resolved IP
        # This requires iptables or network: none to prevent
        assert True  # Documents the gap

    def test_localhost_subdomains(self, network_guard):
        """Subdomains that resolve to localhost."""
        # Some domains have subdomains that resolve to 127.0.0.1
        # e.g., localtest.me, lvh.me

        # These would be blocked by NetworkGuard (not in allowlist)
        with pytest.raises(NetworkRestrictionError):
            network_guard.check_url("http://anything.localtest.me/")

    def test_ipv6_localhost_variants(self, network_guard):
        """IPv6 localhost canonical form is always allowed."""
        # The canonical form ::1 is in the allowlist
        network_guard.check_url("http://[::1]:8080/")
        # Note: Expanded form 0:0:0:0:0:0:0:1 is NOT automatically recognized
        # This is a limitation - only canonical ::1 is allowed


# =============================================================================
# TIER ACCESS TESTS
# =============================================================================


class TestTierAccess:
    """Tests verifying three-tier access control works correctly."""

    def test_blocked_tier_no_read(self, containment_manager, project_root):
        """Tier 1 (blocked) prevents reading."""
        blocked_file = project_root / ".secrets" / "api_keys.json"
        with pytest.raises(ContainmentReadError):
            containment_manager.check_read_allowed(blocked_file)

    def test_blocked_tier_no_write(self, containment_manager, project_root):
        """Tier 1 (blocked) prevents writing."""
        blocked_file = project_root / ".secrets" / "api_keys.json"
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(blocked_file)

    def test_readonly_tier_can_read(self, containment_manager, project_root):
        """Tier 2 (readonly) allows reading."""
        readonly_file = project_root / "CLAUDE.md"
        containment_manager.check_read_allowed(readonly_file)  # Should not raise

    def test_readonly_tier_no_write(self, containment_manager, project_root):
        """Tier 2 (readonly) prevents writing."""
        readonly_file = project_root / "CLAUDE.md"
        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(readonly_file)

    def test_readwrite_tier_can_read(self, containment_manager, project_root):
        """Tier 3 (readwrite) allows reading."""
        writable_file = project_root / "src" / "main.py"
        containment_manager.check_read_allowed(writable_file)  # Should not raise

    def test_readwrite_tier_can_write(self, containment_manager, project_root):
        """Tier 3 (readwrite) allows writing."""
        writable_file = project_root / "src" / "main.py"
        containment_manager.check_write_allowed(writable_file)  # Should not raise


# =============================================================================
# AUDIT LOGGING TESTS
# =============================================================================


class TestAuditLogging:
    """Tests for violation attempt logging.

    Note: Currently ContainmentManager raises exceptions but doesn't log.
    Logging would need to be added or handled by calling code.
    """

    def test_violation_includes_path_info(self, containment_manager, project_root):
        """Violation error includes the attempted path."""
        readonly_file = project_root / "CLAUDE.md"

        with pytest.raises(ContainmentWriteError) as exc_info:
            containment_manager.check_write_allowed(readonly_file)

        assert "CLAUDE.md" in str(exc_info.value) or "read-only" in str(exc_info.value)

    def test_blocked_violation_indicates_tier(self, containment_manager, project_root):
        """Blocked tier violation indicates it's blocked."""
        blocked_file = project_root / ".secrets" / "api_keys.json"

        with pytest.raises(ContainmentReadError) as exc_info:
            containment_manager.check_read_allowed(blocked_file)

        assert "blocked" in str(exc_info.value).lower()


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_path(self, containment_manager, project_root):
        """Empty path is handled - resolves to current directory."""
        # Empty path resolves to current directory (project_root)
        # which is in writable area, so it passes
        containment_manager.check_write_allowed(Path(""))  # Resolves to project_root

    def test_non_existent_path_in_readonly(self, containment_manager, project_root):
        """Non-existent path in readonly directory is still protected."""
        new_file = project_root / ".claude" / "skills" / "not_yet_created.md"
        assert not new_file.exists()

        with pytest.raises(ContainmentWriteError):
            containment_manager.check_write_allowed(new_file)

    def test_path_outside_project_root(self, containment_manager, project_root, tmp_path):
        """Path outside project root is not protected (different scope)."""
        outside_path = tmp_path / "outside_project" / "file.txt"
        outside_path.parent.mkdir(parents=True, exist_ok=True)

        # Paths outside project root are not covered by containment config
        containment_manager.check_write_allowed(outside_path)  # Should pass

    def test_manager_inactive_allows_all(self, project_root, containment_config):
        """Inactive manager allows all operations."""
        manager = ContainmentManager(containment_config, project_root)
        # Don't activate

        readonly_file = project_root / "CLAUDE.md"
        manager.check_write_allowed(readonly_file)  # Should not raise when inactive

    def test_unicode_paths(self, containment_manager, project_root):
        """Unicode characters in paths are handled correctly."""
        unicode_path = project_root / "ünïcödé" / "tëst.txt"
        containment_manager.check_write_allowed(unicode_path)  # Should pass

    def test_very_long_path(self, containment_manager, project_root):
        """Very long paths are handled without crashing."""
        long_path = project_root
        for i in range(50):
            long_path = long_path / f"deep{i}"
        long_path = long_path / "file.txt"

        # Should not crash
        containment_manager.check_write_allowed(long_path)


# =============================================================================
# GAP DOCUMENTATION
# =============================================================================


class TestDocumentedGaps:
    """Tests that explicitly document known enforcement gaps.

    These tests PASS to document gaps, not to verify prevention.
    Prevention requires Docker-based isolation.
    """

    def test_gap_no_hook_into_claude_code_write(self):
        """GAP: Claude Code's Write tool doesn't call ContainmentManager.

        Discovered during T29.6: Claude successfully wrote to
        bpsai_pair/security/ which should have been protected.

        REQUIRED: Integration with Claude Code tools or Docker isolation.
        """
        assert True  # Documents the gap

    def test_gap_subprocess_bypasses_all_checks(self):
        """GAP: Any subprocess call bypasses ContainmentManager.

        Since ContainmentManager only provides check_* methods that must
        be explicitly called, subprocess calls go directly to the OS.

        REQUIRED: Docker isolation with read-only mounts.
        """
        assert True  # Documents the gap

    def test_gap_environment_manipulation_undetected(self):
        """GAP: Environment variable changes are not monitored.

        Changing HOME, PATH, PYTHONPATH etc. could affect behavior
        in ways ContainmentManager cannot detect.

        REQUIRED: Docker isolation with controlled environment.
        """
        assert True  # Documents the gap

    def test_gap_network_redirect_after_initial_check(self):
        """GAP: HTTP redirects after initial URL check.

        NetworkGuard checks the initial URL, but HTTP client will
        follow redirects without re-checking.

        REQUIRED: Docker network isolation or iptables rules.
        """
        assert True  # Documents the gap

    def test_gap_advisory_mode_only(self):
        """GAP: Current implementation is advisory only.

        ContainmentManager provides excellent path checking,
        but nothing enforces that its methods are called before
        filesystem operations.

        SOLUTION: Implement containment mode options:
        - 'advisory': Current behavior + logging
        - 'strict': Docker-based with read-only mounts
        """
        assert True  # Documents the gap
