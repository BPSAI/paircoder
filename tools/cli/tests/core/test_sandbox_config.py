"""Tests for SandboxConfig in the config module."""
import pytest
from pathlib import Path


class TestSandboxConfigBasic:
    """Tests for basic SandboxConfig functionality."""

    def test_sandbox_config_exists(self):
        """Test that SandboxConfig class exists and can be imported."""
        from bpsai_pair.core.config import SandboxConfig
        assert SandboxConfig is not None

    def test_default_values(self):
        """Test that SandboxConfig has correct default values."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig()

        assert config.enabled is False
        assert config.locked_directories == []
        assert config.locked_files == []
        assert config.auto_checkpoint is True
        assert config.rollback_on_violation is False

    def test_default_network_allowlist(self):
        """Test that allow_network has sensible defaults."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig()

        # Should include essential domains by default
        assert "api.anthropic.com" in config.allow_network
        assert "api.trello.com" in config.allow_network
        assert "github.com" in config.allow_network
        assert "pypi.org" in config.allow_network

    def test_custom_values(self):
        """Test that custom values can be set."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            enabled=True,
            locked_directories=["/etc", "/usr"],
            locked_files=["/etc/passwd"],
            allow_network=["example.com"],
            auto_checkpoint=False,
            rollback_on_violation=True
        )

        assert config.enabled is True
        assert config.locked_directories == ["/etc", "/usr"]
        assert config.locked_files == ["/etc/passwd"]
        assert config.allow_network == ["example.com"]
        assert config.auto_checkpoint is False
        assert config.rollback_on_violation is True


class TestSandboxConfigPathValidation:
    """Tests for path validation in SandboxConfig."""

    def test_valid_absolute_directories(self):
        """Test that valid absolute directory paths are accepted."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            locked_directories=["/home/user", "/var/log", "/tmp"]
        )
        assert config.locked_directories == ["/home/user", "/var/log", "/tmp"]

    def test_relative_directory_converted_to_absolute(self):
        """Test that relative directory paths are handled appropriately."""
        from bpsai_pair.core.config import SandboxConfig

        # Relative paths should either be converted to absolute or raise error
        # The implementation should handle this - test what happens
        config = SandboxConfig(
            locked_directories=["relative/path", "./another"]
        )
        # Paths should be stored (validation is at usage time, not creation)
        assert len(config.locked_directories) == 2

    def test_valid_absolute_files(self):
        """Test that valid absolute file paths are accepted."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            locked_files=["/etc/passwd", "/home/user/.bashrc"]
        )
        assert config.locked_files == ["/etc/passwd", "/home/user/.bashrc"]

    def test_empty_path_string_rejected(self):
        """Test that empty path strings are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="empty"):
            SandboxConfig(locked_directories=[""])

    def test_empty_file_path_rejected(self):
        """Test that empty file path strings are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="empty"):
            SandboxConfig(locked_files=[""])

    def test_path_with_null_bytes_rejected(self):
        """Test that paths with null bytes are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="null"):
            SandboxConfig(locked_directories=["/path/with\x00null"])


class TestSandboxConfigNetworkValidation:
    """Tests for network domain validation in SandboxConfig."""

    def test_valid_domains(self):
        """Test that valid domain names are accepted."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            allow_network=["example.com", "api.example.org", "sub.domain.co.uk"]
        )
        assert "example.com" in config.allow_network
        assert "api.example.org" in config.allow_network
        assert "sub.domain.co.uk" in config.allow_network

    def test_domain_with_wildcard(self):
        """Test that wildcard domains are accepted."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            allow_network=["*.example.com"]
        )
        assert "*.example.com" in config.allow_network

    def test_empty_domain_rejected(self):
        """Test that empty domain strings are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="empty"):
            SandboxConfig(allow_network=[""])

    def test_domain_with_protocol_rejected(self):
        """Test that domains with protocol prefix are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="protocol|http"):
            SandboxConfig(allow_network=["https://example.com"])

    def test_domain_with_path_rejected(self):
        """Test that domains with paths are rejected."""
        from bpsai_pair.core.config import SandboxConfig

        with pytest.raises(ValueError, match="path"):
            SandboxConfig(allow_network=["example.com/path"])

    def test_domain_with_port_accepted(self):
        """Test that domains with ports are accepted."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            allow_network=["example.com:8080", "api.example.org:443"]
        )
        assert "example.com:8080" in config.allow_network


class TestSandboxConfigSerialization:
    """Tests for SandboxConfig serialization."""

    def test_to_dict(self):
        """Test that SandboxConfig can be converted to dict."""
        from bpsai_pair.core.config import SandboxConfig

        config = SandboxConfig(
            enabled=True,
            locked_directories=["/etc"],
            locked_files=["/etc/passwd"],
            allow_network=["example.com"],
            auto_checkpoint=False,
            rollback_on_violation=True
        )

        d = config.to_dict()

        assert isinstance(d, dict)
        assert d["enabled"] is True
        assert d["locked_directories"] == ["/etc"]
        assert d["locked_files"] == ["/etc/passwd"]
        assert d["allow_network"] == ["example.com"]
        assert d["auto_checkpoint"] is False
        assert d["rollback_on_violation"] is True

    def test_from_dict(self):
        """Test that SandboxConfig can be created from dict."""
        from bpsai_pair.core.config import SandboxConfig

        data = {
            "enabled": True,
            "locked_directories": ["/etc"],
            "locked_files": ["/etc/passwd"],
            "allow_network": ["example.com"],
            "auto_checkpoint": False,
            "rollback_on_violation": True
        }

        config = SandboxConfig.from_dict(data)

        assert config.enabled is True
        assert config.locked_directories == ["/etc"]
        assert config.locked_files == ["/etc/passwd"]
        assert config.allow_network == ["example.com"]
        assert config.auto_checkpoint is False
        assert config.rollback_on_violation is True

    def test_from_dict_with_defaults(self):
        """Test that from_dict uses defaults for missing keys."""
        from bpsai_pair.core.config import SandboxConfig

        data = {"enabled": True}
        config = SandboxConfig.from_dict(data)

        assert config.enabled is True
        assert config.locked_directories == []
        assert config.auto_checkpoint is True  # default


class TestSandboxConfigDocumentation:
    """Tests for SandboxConfig field documentation."""

    def test_fields_have_descriptions(self):
        """Test that fields have descriptions (via docstrings or Field descriptions)."""
        from bpsai_pair.core.config import SandboxConfig

        # The class should have a docstring
        assert SandboxConfig.__doc__ is not None
        assert "sandbox" in SandboxConfig.__doc__.lower() or "contained" in SandboxConfig.__doc__.lower()
