"""Tests for estimation module."""

import tempfile
from pathlib import Path

import pytest
import yaml

from bpsai_pair.metrics.estimation import (
    EstimationService,
    EstimationConfig,
    HoursEstimate,
    estimate_hours,
    DEFAULT_COMPLEXITY_TO_HOURS,
)
from bpsai_pair.planning.models import Task, TaskStatus


class TestHoursEstimate:
    """Tests for HoursEstimate dataclass."""

    def test_str_representation(self):
        """Test string representation."""
        estimate = HoursEstimate(
            min_hours=1.0,
            expected_hours=2.0,
            max_hours=4.0,
            complexity=25,
            size_band="s",
        )
        assert str(estimate) == "2.0h (S)"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        estimate = HoursEstimate(
            min_hours=0.5,
            expected_hours=1.0,
            max_hours=2.0,
            complexity=10,
            size_band="xs",
        )
        result = estimate.to_dict()
        assert result["min_hours"] == 0.5
        assert result["expected_hours"] == 1.0
        assert result["max_hours"] == 2.0
        assert result["complexity"] == 10
        assert result["size_band"] == "xs"


class TestEstimationConfig:
    """Tests for EstimationConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = EstimationConfig()
        assert "xs" in config.complexity_to_hours
        assert "s" in config.complexity_to_hours
        assert "m" in config.complexity_to_hours
        assert "l" in config.complexity_to_hours
        assert "xl" in config.complexity_to_hours

    def test_from_dict_empty(self):
        """Test from_dict with empty data."""
        config = EstimationConfig.from_dict({})
        assert config.complexity_to_hours == DEFAULT_COMPLEXITY_TO_HOURS

    def test_from_dict_with_overrides(self):
        """Test from_dict with custom values."""
        data = {
            "complexity_to_hours": {
                "xs": {"range": [0, 10], "hours": [0.25, 0.5, 1.0]},
            }
        }
        config = EstimationConfig.from_dict(data)
        # List or tuple are both acceptable
        hours = config.complexity_to_hours["xs"]["hours"]
        assert list(hours) == [0.25, 0.5, 1.0]

    def test_from_dict_simplified_format(self):
        """Test from_dict with simplified list format."""
        data = {
            "complexity_to_hours": {
                "s": [2.0, 3.0, 5.0],
            }
        }
        config = EstimationConfig.from_dict(data)
        assert config.complexity_to_hours["s"]["hours"] == (2.0, 3.0, 5.0)


class TestEstimationService:
    """Tests for EstimationService."""

    def test_default_service(self):
        """Test service with default config."""
        service = EstimationService()
        assert service.config is not None

    def test_get_size_band_xs(self):
        """Test XS band detection."""
        service = EstimationService()
        assert service.get_size_band(0) == "xs"
        assert service.get_size_band(10) == "xs"
        assert service.get_size_band(15) == "xs"

    def test_get_size_band_s(self):
        """Test S band detection."""
        service = EstimationService()
        assert service.get_size_band(16) == "s"
        assert service.get_size_band(25) == "s"
        assert service.get_size_band(30) == "s"

    def test_get_size_band_m(self):
        """Test M band detection."""
        service = EstimationService()
        assert service.get_size_band(31) == "m"
        assert service.get_size_band(40) == "m"
        assert service.get_size_band(50) == "m"

    def test_get_size_band_l(self):
        """Test L band detection."""
        service = EstimationService()
        assert service.get_size_band(51) == "l"
        assert service.get_size_band(65) == "l"
        assert service.get_size_band(75) == "l"

    def test_get_size_band_xl(self):
        """Test XL band detection."""
        service = EstimationService()
        assert service.get_size_band(76) == "xl"
        assert service.get_size_band(90) == "xl"
        assert service.get_size_band(100) == "xl"

    def test_get_size_band_clamping(self):
        """Test complexity clamping to valid range."""
        service = EstimationService()
        assert service.get_size_band(-10) == "xs"
        assert service.get_size_band(150) == "xl"

    def test_estimate_hours_xs(self):
        """Test XS estimate returns valid hours."""
        service = EstimationService()
        estimate = service.estimate_hours(10)
        assert estimate.size_band == "xs"
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_estimate_hours_s(self):
        """Test S estimate returns valid hours."""
        service = EstimationService()
        estimate = service.estimate_hours(25)
        assert estimate.size_band == "s"
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_estimate_hours_m(self):
        """Test M estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(40)
        assert estimate.size_band == "m"
        assert estimate.min_hours == 2.0
        assert estimate.expected_hours == 4.0
        assert estimate.max_hours == 8.0

    def test_estimate_hours_l(self):
        """Test L estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(60)
        assert estimate.size_band == "l"
        assert estimate.min_hours == 4.0
        assert estimate.expected_hours == 8.0
        assert estimate.max_hours == 16.0

    def test_estimate_hours_xl(self):
        """Test XL estimate."""
        service = EstimationService()
        estimate = service.estimate_hours(85)
        assert estimate.size_band == "xl"
        assert estimate.min_hours == 8.0
        assert estimate.expected_hours == 16.0
        assert estimate.max_hours == 32.0

    def test_estimate_hours_for_tasks(self):
        """Test estimating hours for multiple tasks."""
        service = EstimationService()
        tasks = [
            Task(id="TASK-1", title="Small", plan_id="plan-1", complexity=20),
            Task(id="TASK-2", title="Medium", plan_id="plan-1", complexity=40),
            Task(id="TASK-3", title="Large", plan_id="plan-1", complexity=70),
        ]
        estimates = service.estimate_hours_for_tasks(tasks)

        assert "TASK-1" in estimates
        assert "TASK-2" in estimates
        assert "TASK-3" in estimates
        assert estimates["TASK-1"].size_band == "s"
        assert estimates["TASK-2"].size_band == "m"
        assert estimates["TASK-3"].size_band == "l"

    def test_get_total_hours(self):
        """Test total hours calculation."""
        service = EstimationService()
        tasks = [
            Task(id="TASK-1", title="Small", plan_id="plan-1", complexity=20),
            Task(id="TASK-2", title="Medium", plan_id="plan-1", complexity=40),
        ]
        min_total, expected_total, max_total = service.get_total_hours(tasks)

        # Verify order: min <= expected <= max
        assert min_total > 0
        assert min_total <= expected_total
        assert expected_total <= max_total
        # Verify totals are sum of individual estimates
        estimates = service.estimate_hours_for_tasks(tasks)
        assert min_total == sum(e.min_hours for e in estimates.values())
        assert expected_total == sum(e.expected_hours for e in estimates.values())

    def test_format_estimate(self):
        """Test estimate formatting."""
        service = EstimationService()
        estimate = HoursEstimate(
            min_hours=1.0,
            expected_hours=2.0,
            max_hours=4.0,
            complexity=25,
            size_band="s",
        )
        formatted = service.format_estimate(estimate)
        assert formatted == "2.0h (S) [1.0h - 4.0h]"

    def test_from_config_file(self):
        """Test loading from config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "estimation": {
                    "complexity_to_hours": {
                        "xs": {"range": [0, 20], "hours": [0.25, 0.5, 1.0]},
                    }
                }
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            service = EstimationService.from_config_file(config_path)
            estimate = service.estimate_hours(15)
            assert estimate.expected_hours == 0.5

    def test_from_config_file_missing(self):
        """Test loading from missing config file."""
        service = EstimationService.from_config_file(Path("/nonexistent/path"))
        # Should use defaults
        assert service.config is not None


class TestEstimateHoursFunction:
    """Tests for the estimate_hours convenience function."""

    def test_basic_usage(self):
        """Test basic function usage."""
        estimate = estimate_hours(30)
        assert estimate.size_band == "s"
        # Verify valid estimate structure
        assert estimate.min_hours > 0
        assert estimate.min_hours <= estimate.expected_hours
        assert estimate.expected_hours <= estimate.max_hours

    def test_with_config_file(self):
        """Test with config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "estimation": {
                    "complexity_to_hours": {
                        "s": {"range": [16, 30], "hours": [2.0, 3.0, 6.0]},
                    }
                }
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            estimate = estimate_hours(25, config_path)
            assert estimate.expected_hours == 3.0


class TestTaskEstimatedHours:
    """Tests for Task.estimated_hours property."""

    def test_estimated_hours_property(self):
        """Test that Task has estimated_hours property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            complexity=25,
        )
        estimate = task.estimated_hours
        assert estimate.size_band == "s"
        # Just verify it returns an estimate with the right band
        assert estimate.expected_hours > 0

    def test_estimated_hours_str_property(self):
        """Test estimated_hours_str property."""
        task = Task(
            id="TASK-1",
            title="Test Task",
            plan_id="plan-1",
            complexity=25,
        )
        # Format should be like "X.Xh (S)"
        assert "h (S)" in task.estimated_hours_str

    def test_different_complexities(self):
        """Test different complexity values."""
        xs_task = Task(id="T1", title="XS", plan_id="p", complexity=10)
        xl_task = Task(id="T2", title="XL", plan_id="p", complexity=90)

        assert xs_task.estimated_hours.size_band == "xs"
        assert xl_task.estimated_hours.size_band == "xl"
        assert xs_task.estimated_hours.expected_hours < xl_task.estimated_hours.expected_hours
