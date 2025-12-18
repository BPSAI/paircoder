"""Estimation service for complexity-to-hours and token estimation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from pathlib import Path
import yaml
import logging

if TYPE_CHECKING:
    from ..planning.models import Task

logger = logging.getLogger(__name__)


# Default complexity-to-hours mapping
# Format: complexity_range -> (min_hours, expected_hours, max_hours)
DEFAULT_COMPLEXITY_TO_HOURS = {
    "xs": {"range": (0, 15), "hours": (0.5, 1.0, 2.0)},      # XS - under 2 hours
    "s": {"range": (16, 30), "hours": (1.0, 2.0, 4.0)},      # S - half day
    "m": {"range": (31, 50), "hours": (2.0, 4.0, 8.0)},      # M - full day
    "l": {"range": (51, 75), "hours": (4.0, 8.0, 16.0)},     # L - 1-2 days
    "xl": {"range": (76, 100), "hours": (8.0, 16.0, 32.0)},  # XL - 2-4 days
}


@dataclass
class HoursEstimate:
    """Estimated hours for a task."""
    min_hours: float
    expected_hours: float
    max_hours: float
    complexity: int
    size_band: str  # xs, s, m, l, xl

    def __str__(self) -> str:
        return f"{self.expected_hours:.1f}h ({self.size_band.upper()})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_hours": self.min_hours,
            "expected_hours": self.expected_hours,
            "max_hours": self.max_hours,
            "complexity": self.complexity,
            "size_band": self.size_band,
        }


@dataclass
class TaskComparison:
    """Comparison of estimated vs actual hours for a task."""

    task_id: str
    estimated_hours: float
    actual_hours: float
    completed_at: Optional[datetime] = None

    @property
    def variance_hours(self) -> float:
        """Calculate variance (actual - estimated). Negative means under estimate."""
        return self.actual_hours - self.estimated_hours

    @property
    def variance_percent(self) -> float:
        """Calculate variance as percentage of estimated hours."""
        if self.estimated_hours == 0:
            return 0.0
        return (self.variance_hours / self.estimated_hours) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metrics JSONL storage."""
        return {
            "task_id": self.task_id,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "variance_hours": self.variance_hours,
            "variance_percent": self.variance_percent,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_task(
        cls, task: "Task", actual_hours: float, completed_at: Optional[datetime] = None
    ) -> "TaskComparison":
        """Create comparison from task object and actual hours."""
        return cls(
            task_id=task.id,
            estimated_hours=task.estimated_hours.expected_hours,
            actual_hours=actual_hours,
            completed_at=completed_at or datetime.now(),
        )


@dataclass
class EstimationConfig:
    """Configuration for estimation service."""
    complexity_to_hours: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: DEFAULT_COMPLEXITY_TO_HOURS.copy()
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EstimationConfig":
        """Create from dictionary (e.g., from config.yaml)."""
        mapping = data.get("complexity_to_hours", {})
        if not mapping:
            return cls()

        # Convert from config format to internal format
        converted = {}
        for key, value in mapping.items():
            if isinstance(value, dict):
                converted[key.lower()] = value
            else:
                # Handle simplified format: "xs": [0.5, 1, 2]
                if isinstance(value, list) and len(value) == 3:
                    converted[key.lower()] = {"hours": tuple(value)}

        # Merge with defaults to fill in missing bands
        result = DEFAULT_COMPLEXITY_TO_HOURS.copy()
        for key, value in converted.items():
            if key in result:
                result[key].update(value)
            else:
                result[key] = value

        return cls(complexity_to_hours=result)


class EstimationService:
    """Service for estimating task hours from complexity points."""

    def __init__(self, config: Optional[EstimationConfig] = None):
        self.config = config or EstimationConfig()

    @classmethod
    def from_config_file(cls, config_path: Path) -> "EstimationService":
        """Load estimation config from a YAML file."""
        if not config_path.exists():
            return cls()

        try:
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}

            estimation_data = data.get("estimation", {})
            config = EstimationConfig.from_dict(estimation_data)
            return cls(config)
        except Exception as e:
            logger.warning(f"Failed to load estimation config: {e}")
            return cls()

    def get_size_band(self, complexity: int) -> str:
        """Determine the size band for a complexity score.

        Args:
            complexity: Complexity score (0-100)

        Returns:
            Size band: 'xs', 's', 'm', 'l', or 'xl'
        """
        # Clamp to valid range
        complexity = max(0, min(100, complexity))

        for band, info in self.config.complexity_to_hours.items():
            range_tuple = info.get("range", (0, 0))
            if range_tuple[0] <= complexity <= range_tuple[1]:
                return band

        # Fallback based on standard bands if no range defined
        if complexity <= 15:
            return "xs"
        elif complexity <= 30:
            return "s"
        elif complexity <= 50:
            return "m"
        elif complexity <= 75:
            return "l"
        else:
            return "xl"

    def estimate_hours(self, complexity: int) -> HoursEstimate:
        """Estimate hours from complexity score.

        Args:
            complexity: Complexity score (0-100)

        Returns:
            HoursEstimate with min, expected, and max hours
        """
        # Clamp to valid range
        complexity = max(0, min(100, complexity))

        size_band = self.get_size_band(complexity)
        band_info = self.config.complexity_to_hours.get(
            size_band, DEFAULT_COMPLEXITY_TO_HOURS.get(size_band, {"hours": (1.0, 2.0, 4.0)})
        )
        hours = band_info.get("hours", (1.0, 2.0, 4.0))

        return HoursEstimate(
            min_hours=hours[0],
            expected_hours=hours[1],
            max_hours=hours[2],
            complexity=complexity,
            size_band=size_band,
        )

    def estimate_hours_for_tasks(self, tasks: List[Any]) -> Dict[str, HoursEstimate]:
        """Estimate hours for multiple tasks.

        Args:
            tasks: List of Task objects with 'id' and 'complexity' attributes

        Returns:
            Dict mapping task_id to HoursEstimate
        """
        estimates = {}
        for task in tasks:
            task_id = getattr(task, "id", str(task))
            complexity = getattr(task, "complexity", 30)  # Default to medium
            estimates[task_id] = self.estimate_hours(complexity)
        return estimates

    def get_total_hours(self, tasks: List[Any]) -> Tuple[float, float, float]:
        """Get total estimated hours for a list of tasks.

        Args:
            tasks: List of Task objects with 'complexity' attribute

        Returns:
            Tuple of (min_total, expected_total, max_total) hours
        """
        estimates = self.estimate_hours_for_tasks(tasks)

        min_total = sum(e.min_hours for e in estimates.values())
        expected_total = sum(e.expected_hours for e in estimates.values())
        max_total = sum(e.max_hours for e in estimates.values())

        return min_total, expected_total, max_total

    def format_estimate(self, estimate: HoursEstimate) -> str:
        """Format an estimate for display.

        Args:
            estimate: HoursEstimate to format

        Returns:
            Formatted string like "2.0h (S) [1.0h - 4.0h]"
        """
        return (
            f"{estimate.expected_hours:.1f}h ({estimate.size_band.upper()}) "
            f"[{estimate.min_hours:.1f}h - {estimate.max_hours:.1f}h]"
        )

    def create_comparison(
        self, task: Any, actual_hours: float, completed_at: Optional[datetime] = None
    ) -> TaskComparison:
        """Create a comparison between estimated and actual hours.

        Args:
            task: Task object with 'id' and 'complexity' attributes
            actual_hours: Actual hours spent on the task
            completed_at: Optional completion timestamp

        Returns:
            TaskComparison with variance calculations
        """
        task_id = getattr(task, "id", str(task))
        complexity = getattr(task, "complexity", 30)
        estimate = self.estimate_hours(complexity)

        return TaskComparison(
            task_id=task_id,
            estimated_hours=estimate.expected_hours,
            actual_hours=actual_hours,
            completed_at=completed_at or datetime.now(),
        )

    def format_comparison(self, comparison: TaskComparison) -> str:
        """Format a comparison for display.

        Args:
            comparison: TaskComparison to format

        Returns:
            Formatted string like "Est: 4.0h | Act: 3.5h (-12.5%)"
        """
        sign = "+" if comparison.variance_percent > 0 else ""
        return (
            f"Est: {comparison.estimated_hours:.1f}h | "
            f"Act: {comparison.actual_hours:.1f}h "
            f"({sign}{comparison.variance_percent:.1f}%)"
        )


# Convenience function for quick access
def estimate_hours(complexity: int, config_path: Optional[Path] = None) -> HoursEstimate:
    """Estimate hours for a given complexity score.

    Args:
        complexity: Complexity score (0-100)
        config_path: Optional path to config file

    Returns:
        HoursEstimate with min, expected, and max hours
    """
    if config_path:
        service = EstimationService.from_config_file(config_path)
    else:
        service = EstimationService()

    return service.estimate_hours(complexity)
