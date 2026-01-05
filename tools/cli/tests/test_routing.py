"""Tests for model routing configuration.

Location: tools/cli/tests/core/test_routing_config.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch

from bpsai_pair.core.routing import (
    RoutingLevel,
    RoutingConfig,
    EnforcementConfig,
    get_model_for_task,
)


class TestRoutingLevel:
    """Tests for RoutingLevel dataclass."""
    
    def test_from_dict(self):
        """Should create RoutingLevel from dict."""
        data = {"max_score": 40, "model": "claude-haiku-4-5"}
        level = RoutingLevel.from_dict(data)
        
        assert level.max_score == 40
        assert level.model == "claude-haiku-4-5"
    
    def test_from_dict_defaults(self):
        """Should use defaults for missing keys."""
        level = RoutingLevel.from_dict({})
        
        assert level.max_score == 100
        assert level.model == "claude-sonnet-4-5"


class TestRoutingConfig:
    """Tests for RoutingConfig."""
    
    def test_from_dict_empty(self):
        """Should handle empty config."""
        config = RoutingConfig.from_dict({})
        
        assert config.by_complexity == {}
        assert config.overrides == {}
    
    def test_from_dict_full(self):
        """Should parse full config."""
        data = {
            "by_complexity": {
                "trivial": {"max_score": 20, "model": "claude-haiku-4-5"},
                "moderate": {"max_score": 60, "model": "claude-sonnet-4-5"},
            },
            "overrides": {
                "security": "claude-opus-4-5",
            }
        }
        config = RoutingConfig.from_dict(data)
        
        assert len(config.by_complexity) == 2
        assert config.by_complexity["trivial"].max_score == 20
        assert config.overrides["security"] == "claude-opus-4-5"
    
    def test_get_model_for_complexity_trivial(self):
        """Should return correct model for trivial tasks."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "trivial": {"max_score": 20, "model": "claude-haiku-4-5"},
                "moderate": {"max_score": 60, "model": "claude-sonnet-4-5"},
                "complex": {"max_score": 100, "model": "claude-opus-4-5"},
            }
        })
        
        assert config.get_model_for_complexity(10) == "claude-haiku-4-5"
        assert config.get_model_for_complexity(20) == "claude-haiku-4-5"
    
    def test_get_model_for_complexity_moderate(self):
        """Should return correct model for moderate tasks."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "trivial": {"max_score": 20, "model": "claude-haiku-4-5"},
                "moderate": {"max_score": 60, "model": "claude-sonnet-4-5"},
                "complex": {"max_score": 100, "model": "claude-opus-4-5"},
            }
        })
        
        assert config.get_model_for_complexity(30) == "claude-sonnet-4-5"
        assert config.get_model_for_complexity(60) == "claude-sonnet-4-5"
    
    def test_get_model_for_complexity_complex(self):
        """Should return correct model for complex tasks."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "trivial": {"max_score": 20, "model": "claude-haiku-4-5"},
                "moderate": {"max_score": 60, "model": "claude-sonnet-4-5"},
                "complex": {"max_score": 100, "model": "claude-opus-4-5"},
            }
        })
        
        assert config.get_model_for_complexity(80) == "claude-opus-4-5"
        assert config.get_model_for_complexity(100) == "claude-opus-4-5"
    
    def test_get_model_for_complexity_exceeds_max(self):
        """Should return most capable model for scores exceeding max."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "simple": {"max_score": 50, "model": "claude-haiku-4-5"},
            }
        })
        
        # Score exceeds max, should return the highest level's model
        assert config.get_model_for_complexity(100) == "claude-haiku-4-5"
    
    def test_get_model_for_complexity_empty_config(self):
        """Should return default when no complexity levels defined."""
        config = RoutingConfig()
        
        assert config.get_model_for_complexity(50) == "claude-sonnet-4-5"
    
    def test_get_model_for_task_type(self):
        """Should return override for task type."""
        config = RoutingConfig.from_dict({
            "overrides": {
                "security": "claude-opus-4-5",
                "architecture": "claude-opus-4-5",
            }
        })
        
        assert config.get_model_for_task_type("security") == "claude-opus-4-5"
        assert config.get_model_for_task_type("architecture") == "claude-opus-4-5"
    
    def test_get_model_for_task_type_no_override(self):
        """Should return None when no override exists."""
        config = RoutingConfig()
        
        assert config.get_model_for_task_type("feature") is None
    
    def test_get_model_type_override_takes_precedence(self):
        """Task type override should take precedence over complexity."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "trivial": {"max_score": 100, "model": "claude-haiku-4-5"},
            },
            "overrides": {
                "security": "claude-opus-4-5",
            }
        })
        
        # Even trivial complexity security task should use opus
        model = config.get_model(complexity=10, task_type="security")
        assert model == "claude-opus-4-5"
    
    def test_get_model_falls_back_to_complexity(self):
        """Should fall back to complexity when no type override."""
        config = RoutingConfig.from_dict({
            "by_complexity": {
                "trivial": {"max_score": 30, "model": "claude-haiku-4-5"},
                "complex": {"max_score": 100, "model": "claude-sonnet-4-5"},
            },
            "overrides": {
                "security": "claude-opus-4-5",
            }
        })
        
        # Feature task uses complexity routing
        model = config.get_model(complexity=50, task_type="feature")
        assert model == "claude-sonnet-4-5"


class TestEnforcementConfig:
    """Tests for EnforcementConfig."""
    
    def test_from_dict_defaults(self):
        """Should use correct defaults."""
        config = EnforcementConfig.from_dict({})
        
        assert config.state_machine is False
        assert config.strict_mode is True
        assert config.require_ac_verification is True
        assert config.require_budget_check is True
    
    def test_from_dict_custom(self):
        """Should parse custom values."""
        data = {
            "state_machine": True,
            "strict_mode": False,
            "require_ac_verification": False,
            "require_budget_check": False,
        }
        config = EnforcementConfig.from_dict(data)
        
        assert config.state_machine is True
        assert config.strict_mode is False
        assert config.require_ac_verification is False
        assert config.require_budget_check is False


class TestGetModelForTask:
    """Tests for get_model_for_task helper."""
    
    def test_uses_config(self, tmp_path):
        """Should load config and return model."""
        config_file = tmp_path / ".paircoder" / "config.yaml"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("""
routing:
  by_complexity:
    simple:
      max_score: 50
      model: claude-haiku-4-5
    complex:
      max_score: 100
      model: claude-opus-4-5
""")
        
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=config_file.parent):
            model = get_model_for_task(complexity=30)
        
        assert model == "claude-haiku-4-5"
    
    def test_returns_default_without_config(self, tmp_path):
        """Should return default model when no config."""
        with patch("bpsai_pair.core.ops.find_paircoder_dir", return_value=None):
            model = get_model_for_task(complexity=50)
        
        # Should return default
        assert "claude" in model.lower()
