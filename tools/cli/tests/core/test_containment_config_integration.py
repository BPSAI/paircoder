"""Tests for ContainmentConfig integration with config loading."""
import pytest
from pathlib import Path
import yaml


class TestContainmentConfigIntegration:
    """Tests for containment config loading and integration."""

    def test_config_without_containment_uses_defaults(self, tmp_path):
        """Test that config without containment section uses defaults."""
        from bpsai_pair.core.config import Config, ContainmentConfig

        # Create config without containment section
        config_dir = tmp_path / ".paircoder"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
version: 2.6
project:
  name: TestProject
  primary_goal: Test
workflow:
  main_branch: main
""")

        config = Config.load(tmp_path)

        # Should have default containment config
        assert hasattr(config, 'containment')
        assert isinstance(config.containment, ContainmentConfig)
        assert config.containment.enabled is False
        assert config.containment.auto_checkpoint is True

    def test_config_with_containment_section_loads(self, tmp_path):
        """Test that config with containment section loads correctly."""
        from bpsai_pair.core.config import Config

        config_dir = tmp_path / ".paircoder"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
version: 2.6
project:
  name: TestProject
  primary_goal: Test
workflow:
  main_branch: main
containment:
  enabled: true
  readonly_directories:
    - /etc
    - /usr
  readonly_files:
    - /etc/passwd
  allow_network:
    - example.com
  auto_checkpoint: false
  rollback_on_violation: true
""")

        config = Config.load(tmp_path)

        assert config.containment.enabled is True
        assert config.containment.readonly_directories == ["/etc", "/usr"]
        assert config.containment.readonly_files == ["/etc/passwd"]
        assert config.containment.allow_network == ["example.com"]
        assert config.containment.auto_checkpoint is False
        assert config.containment.rollback_on_violation is True

    def test_config_with_partial_containment_merges_defaults(self, tmp_path):
        """Test that partial containment config uses defaults for missing keys."""
        from bpsai_pair.core.config import Config, DEFAULT_CONTAINMENT_NETWORK_ALLOWLIST

        config_dir = tmp_path / ".paircoder"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
version: 2.6
project:
  name: TestProject
  primary_goal: Test
containment:
  enabled: true
""")

        config = Config.load(tmp_path)

        assert config.containment.enabled is True
        assert config.containment.readonly_directories == []  # default
        assert config.containment.auto_checkpoint is True  # default
        assert config.containment.allow_network == DEFAULT_CONTAINMENT_NETWORK_ALLOWLIST

    def test_invalid_containment_config_raises_error(self, tmp_path):
        """Test that invalid containment config raises error."""
        from bpsai_pair.core.config import Config

        config_dir = tmp_path / ".paircoder"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
version: 2.6
project:
  name: TestProject
  primary_goal: Test
containment:
  enabled: true
  allow_network:
    - https://example.com
""")

        with pytest.raises(ValueError, match="protocol"):
            Config.load(tmp_path)


class TestPresetContainmentConfig:
    """Tests for containment config in presets."""

    def test_preset_includes_containment_section(self):
        """Test that preset generates config with containment section."""
        from bpsai_pair.core.presets import get_preset

        preset = get_preset("minimal")
        config = preset.to_config_dict("Test", "Build software")

        assert "containment" in config
        assert config["containment"]["enabled"] is False
        # Presets use locked_directories (mapped to readonly_directories on load)
        assert "locked_directories" in config["containment"]
        assert "allow_network" in config["containment"]

    def test_preset_containment_has_sensible_defaults(self):
        """Test that preset containment section has sensible defaults."""
        from bpsai_pair.core.presets import get_preset

        preset = get_preset("minimal")
        config = preset.to_config_dict("Test", "Build software")

        containment = config["containment"]
        assert containment["enabled"] is False
        assert containment["auto_checkpoint"] is True
        assert containment["rollback_on_violation"] is False

        # Should have default network allowlist
        assert "api.anthropic.com" in containment["allow_network"]
        assert "github.com" in containment["allow_network"]


class TestCookiecutterContainmentConfig:
    """Tests for containment config in cookiecutter template."""

    def test_cookiecutter_template_has_containment_section(self):
        """Test that cookiecutter template includes containment section."""
        from pathlib import Path

        template_path = Path(__file__).parent.parent.parent / "bpsai_pair" / "data" / "cookiecutter-paircoder" / "{{cookiecutter.project_slug}}" / ".paircoder" / "config.yaml"

        if not template_path.exists():
            pytest.skip("Cookiecutter template not found")

        # Read as text since it contains Jinja2 templating syntax
        content = template_path.read_text()

        # Check that containment section exists in template
        assert "containment:" in content
        assert "enabled:" in content
        # Template uses locked_directories (mapped to readonly_directories on load)
        assert "locked_directories:" in content
        assert "allow_network:" in content

    def test_cookiecutter_containment_defaults(self):
        """Test that cookiecutter containment section has correct defaults."""
        from pathlib import Path

        template_path = Path(__file__).parent.parent.parent / "bpsai_pair" / "data" / "cookiecutter-paircoder" / "{{cookiecutter.project_slug}}" / ".paircoder" / "config.yaml"

        if not template_path.exists():
            pytest.skip("Cookiecutter template not found")

        # Read as text since it contains Jinja2 templating syntax
        content = template_path.read_text()

        # Find the containment section (top-level, not security.sandbox)
        # Check for key containment settings
        assert "enabled: false" in content
        assert "auto_checkpoint: true" in content

        # Should lock important config files by default
        assert ".claude/skills/" in content or ".claude" in content


class TestValidateContainmentConfig:
    """Tests for containment config validation."""

    def test_validate_recognizes_containment_section(self, tmp_path):
        """Test that validate_config recognizes containment section."""
        from bpsai_pair.core.config import validate_config

        config_dir = tmp_path / ".paircoder"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("""
version: 2.6
project:
  name: TestProject
  primary_goal: Test
workflow:
  main_branch: main
pack:
  default_name: pack.tgz
flows:
  enabled: []
routing:
  by_complexity: {}
trello:
  enabled: false
estimation:
  complexity_to_hours: {}
metrics:
  enabled: true
hooks:
  enabled: true
security:
  allowlist_path: .paircoder/security/allowlist.yaml
containment:
  enabled: true
""")

        result = validate_config(tmp_path)

        # Should be valid with containment section
        assert "containment" not in result.missing_sections
