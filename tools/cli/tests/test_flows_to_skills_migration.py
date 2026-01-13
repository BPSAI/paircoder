"""
Tests for flows → skills migration in planning system.

These tests verify:
1. New plans use 'skills' field (not 'flows')
2. --flow option shows deprecation warning
3. Old plans with 'flows' are still readable
4. Skills are correctly serialized/deserialized
"""

import pytest
import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from bpsai_pair.planning.models import Plan, PlanType, PlanStatus


class TestPlanSkillsField:
    """Test that Plan model correctly handles skills field."""

    def test_plan_with_skills_to_dict(self):
        """Plan with skills should serialize skills, not flows."""
        plan = Plan(
            id="plan-2026-01-test",
            title="Test Plan",
            type=PlanType.FEATURE,
            status=PlanStatus.PLANNED,
            skills=["planning-with-trello"],
        )
        
        data = plan.to_dict()
        
        assert "skills" in data
        assert data["skills"] == ["planning-with-trello"]
        assert "flows" not in data or data.get("flows") == []

    def test_plan_with_flows_only_to_dict(self):
        """Plan with only flows (old style) should serialize flows."""
        plan = Plan(
            id="plan-2025-01-old",
            title="Old Plan",
            type=PlanType.FEATURE,
            status=PlanStatus.PLANNED,
            flows=["design-plan-implement"],
            skills=[],
        )
        
        data = plan.to_dict()
        
        # Should still write flows for backward compat
        assert "flows" in data
        assert data["flows"] == ["design-plan-implement"]
        assert "skills" not in data or data.get("skills") == []

    def test_plan_from_dict_with_skills(self):
        """Plan.from_dict should read skills field."""
        data = {
            "id": "plan-2026-01-new",
            "title": "New Plan",
            "type": "feature",
            "status": "planned",
            "skills": ["planning-with-trello"],
        }
        
        plan = Plan.from_dict(data)
        
        assert plan.skills == ["planning-with-trello"]
        assert plan.flows == []

    def test_plan_from_dict_with_flows_migrates_to_skills(self):
        """Plan.from_dict should migrate flows to skills for old plans."""
        data = {
            "id": "plan-2025-01-old",
            "title": "Old Plan",
            "type": "feature",
            "status": "planned",
            "flows": ["design-plan-implement"],
        }
        
        plan = Plan.from_dict(data)
        
        # Should migrate flows to skills
        assert plan.skills == ["design-plan-implement"]
        # Flows should be cleared when skills present
        assert plan.flows == []

    def test_plan_from_dict_prefers_skills_over_flows(self):
        """If both skills and flows present, skills wins."""
        data = {
            "id": "plan-2026-01-mixed",
            "title": "Mixed Plan",
            "type": "feature",
            "status": "planned",
            "skills": ["new-skill"],
            "flows": ["old-flow"],
        }
        
        plan = Plan.from_dict(data)
        
        assert plan.skills == ["new-skill"]
        assert plan.flows == []  # Cleared because skills present


class TestPlanNewCommand:
    """Test that plan new command uses skills."""

    @pytest.fixture
    def mock_paircoder_dir(self, tmp_path):
        """Create mock .paircoder directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "plans").mkdir()
        return paircoder_dir

    def test_plan_new_creates_skills_not_flows(self, mock_paircoder_dir, monkeypatch):
        """plan new should create plan with skills field."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app
        
        runner = CliRunner()
        
        # Mock find_paircoder_dir
        monkeypatch.setattr(
            "bpsai_pair.planning.commands.find_paircoder_dir",
            lambda: mock_paircoder_dir
        )
        
        result = runner.invoke(app, [
            "plan", "new", "test-plan",
            "--skill", "planning-with-trello",
            "--type", "feature"
        ])
        
        assert result.exit_code == 0
        
        # Find created plan file
        plan_files = list((mock_paircoder_dir / "plans").glob("*.plan.yaml"))
        assert len(plan_files) == 1
        
        # Read and verify
        with open(plan_files[0]) as f:
            data = yaml.safe_load(f)
        
        assert "skills" in data
        assert data["skills"] == ["planning-with-trello"]
        assert "flows" not in data or data.get("flows") == []

    def test_plan_new_with_deprecated_flow_warns(self, mock_paircoder_dir, monkeypatch):
        """Using --flow should show deprecation warning."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app
        
        runner = CliRunner()
        
        monkeypatch.setattr(
            "bpsai_pair.planning.commands.find_paircoder_dir",
            lambda: mock_paircoder_dir
        )
        
        result = runner.invoke(app, [
            "plan", "new", "test-deprecated",
            "--flow", "old-flow-name"
        ])
        
        assert result.exit_code == 0
        assert "deprecated" in result.output.lower()

    def test_plan_new_default_skill(self, mock_paircoder_dir, monkeypatch):
        """plan new without --skill should default to planning-with-trello."""
        from typer.testing import CliRunner
        from bpsai_pair.cli import app
        
        runner = CliRunner()
        
        monkeypatch.setattr(
            "bpsai_pair.planning.commands.find_paircoder_dir",
            lambda: mock_paircoder_dir
        )
        
        result = runner.invoke(app, ["plan", "new", "test-default"])
        
        assert result.exit_code == 0
        
        plan_files = list((mock_paircoder_dir / "plans").glob("*.plan.yaml"))
        with open(plan_files[0]) as f:
            data = yaml.safe_load(f)
        
        assert data["skills"] == ["planning-with-trello"]


class TestBackwardCompatibility:
    """Test that old plans with flows still work."""

    def test_read_old_plan_with_flows(self, tmp_path):
        """Old plans with flows should still be readable."""
        from bpsai_pair.planning.parser import PlanParser
        
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        
        # Create old-style plan with flows
        old_plan_yaml = """
id: plan-2025-01-old-style
title: Old Style Plan
type: feature
status: planned
flows:
  - design-plan-implement
goals:
  - Some goal
"""
        (plans_dir / "plan-2025-01-old-style.plan.yaml").write_text(old_plan_yaml)
        
        parser = PlanParser(plans_dir)
        plan = parser.get_plan_by_id("plan-2025-01-old-style")
        
        assert plan is not None
        assert plan.title == "Old Style Plan"
        # Skills should be populated from flows
        assert plan.skills == ["design-plan-implement"]

    def test_roundtrip_preserves_skills(self, tmp_path):
        """Save then load should preserve skills."""
        from bpsai_pair.planning.parser import PlanParser
        
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        
        # Create plan with skills
        plan = Plan(
            id="plan-2026-01-roundtrip",
            title="Roundtrip Test",
            type=PlanType.FEATURE,
            status=PlanStatus.PLANNED,
            skills=["my-skill"],
        )
        
        parser = PlanParser(plans_dir)
        parser.save(plan)
        
        # Load it back
        loaded = parser.get_plan_by_id("plan-2026-01-roundtrip")
        
        assert loaded.skills == ["my-skill"]
        assert loaded.flows == []
