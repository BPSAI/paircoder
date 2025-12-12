"""
YAML parser for Paircoder flows.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml

from .models import Flow, Step, FlowValidationError


class FlowParser:
    """Parse flow definitions from YAML files."""

    def __init__(self, flows_dir: Optional[Path] = None):
        """Initialize parser with flows directory."""
        self.flows_dir = flows_dir

    def parse_file(self, path: Path) -> Flow:
        """Parse a single flow file."""
        if not path.exists():
            raise FlowValidationError(f"Flow file not found: {path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML in {path}: {e}")

        if not data or not isinstance(data, dict):
            raise FlowValidationError(f"Invalid flow file (expected YAML dict): {path}")

        return self._parse_flow_data(data, source_file=str(path))

    def parse_string(self, content: str, source_name: str = "<string>") -> Flow:
        """Parse flow from YAML string."""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML: {e}")

        if not data or not isinstance(data, dict):
            raise FlowValidationError("Invalid flow definition (expected YAML dict)")

        return self._parse_flow_data(data, source_file=source_name)

    def _parse_flow_data(
        self, data: Dict[str, Any], source_file: Optional[str] = None
    ) -> Flow:
        """Parse flow data dictionary into Flow object."""
        # Required fields
        name = data.get("name")
        if not name:
            raise FlowValidationError("Flow must have a 'name' field")

        description = data.get("description", "")

        # Parse steps
        steps_data = data.get("steps", [])
        if not steps_data:
            raise FlowValidationError("Flow must have at least one step")

        steps = []
        for i, step_data in enumerate(steps_data):
            step = self._parse_step(step_data, index=i)
            steps.append(step)

        # Optional fields
        variables = data.get("variables", {})
        version = str(data.get("version", "1"))

        flow = Flow(
            name=name,
            description=description,
            steps=steps,
            variables=variables,
            version=version,
            source_file=source_file,
        )

        # Validate
        errors = flow.validate()
        if errors:
            raise FlowValidationError(
                f"Flow validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return flow

    def _parse_step(self, data: Dict[str, Any], index: int) -> Step:
        """Parse a single step from data dictionary."""
        # Required fields
        step_id = data.get("id")
        if not step_id:
            raise FlowValidationError(f"Step {index + 1} must have an 'id' field")

        action = data.get("action")
        if not action:
            raise FlowValidationError(f"Step '{step_id}' must have an 'action' field")

        # Optional fields
        description = data.get("description")
        inputs = data.get("inputs", {})
        model = data.get("model")
        prompt = data.get("prompt")
        context = data.get("context", {})
        path = data.get("path")
        depends_on = data.get("depends_on")

        # Normalize depends_on to list (handle null, string, or invalid types)
        if depends_on is None:
            depends_on = []
        elif isinstance(depends_on, str):
            depends_on = [depends_on]
        elif not isinstance(depends_on, list):
            depends_on = []  # Coerce invalid types to empty list

        return Step(
            id=step_id,
            action=action,
            description=description,
            inputs=inputs,
            model=model,
            prompt=prompt,
            context=context,
            path=path,
            depends_on=depends_on,
        )

    def list_flows(self) -> List[Dict[str, Any]]:
        """List all available flows in the flows directory."""
        if not self.flows_dir or not self.flows_dir.exists():
            return []

        flows = []
        for path in sorted(self.flows_dir.glob("*.yaml")):
            try:
                flow = self.parse_file(path)
                flows.append({
                    "name": flow.name,
                    "description": flow.description,
                    "steps": len(flow.steps),
                    "file": path.name,
                })
            except FlowValidationError:
                # Include invalid flows with error indicator
                flows.append({
                    "name": path.stem,
                    "description": "(invalid)",
                    "steps": 0,
                    "file": path.name,
                    "error": True,
                })

        # Also check .yml extension
        for path in sorted(self.flows_dir.glob("*.yml")):
            if path.with_suffix(".yaml").exists():
                continue  # Skip if .yaml version exists
            try:
                flow = self.parse_file(path)
                flows.append({
                    "name": flow.name,
                    "description": flow.description,
                    "steps": len(flow.steps),
                    "file": path.name,
                })
            except FlowValidationError:
                flows.append({
                    "name": path.stem,
                    "description": "(invalid)",
                    "steps": 0,
                    "file": path.name,
                    "error": True,
                })

        return flows

    def find_flow(self, name: str) -> Optional[Path]:
        """Find a flow file by name."""
        if not self.flows_dir or not self.flows_dir.exists():
            return None

        # Try exact name first
        for ext in [".yaml", ".yml"]:
            path = self.flows_dir / f"{name}{ext}"
            if path.exists():
                return path

        # Try to find by flow name in file
        for path in self.flows_dir.glob("*.yaml"):
            try:
                flow = self.parse_file(path)
                if flow.name == name:
                    return path
            except FlowValidationError:
                continue

        for path in self.flows_dir.glob("*.yml"):
            try:
                flow = self.parse_file(path)
                if flow.name == name:
                    return path
            except FlowValidationError:
                continue

        return None
