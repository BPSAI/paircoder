"""
Flow Parser (v2)

Supports both legacy .flow.yml and new .flow.md (YAML frontmatter + Markdown) formats.

The new .flow.md format:
```
---
name: design-plan-implement
version: 1
description: >
  Turn a feature request into a validated design...
when_to_use:
  - feature_request
  - large_refactor
roles:
  navigator: { primary: true }
  driver: { primary: true }
triggers:
  - feature_request
tags:
  - design
  - planning
---

# Flow Title

## Phase 1 - Design

Instructions here...
```
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

import yaml


# Regex to match YAML frontmatter
FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?(.*)$",
    re.DOTALL
)


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Parse YAML frontmatter from a document.
    
    Args:
        content: Full file content with optional YAML frontmatter
        
    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    match = FRONTMATTER_PATTERN.match(content)
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2).strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            frontmatter = {}
        return frontmatter, body
    return {}, content


@dataclass
class FlowRole:
    """Role definition within a flow."""
    name: str
    primary: bool = False
    description: str = ""
    
    @classmethod
    def from_dict(cls, name: str, data) -> "FlowRole":
        if isinstance(data, dict):
            return cls(
                name=name,
                primary=data.get("primary", False),
                description=data.get("description", ""),
            )
        elif isinstance(data, bool):
            return cls(name=name, primary=data)
        return cls(name=name)


@dataclass
class FlowStep:
    """A step within a flow."""
    id: str
    role: str
    summary: str
    checklist: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    gates: list[str] = field(default_factory=list)
    subflow: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "FlowStep":
        return cls(
            id=data.get("id", ""),
            role=data.get("role", ""),
            summary=data.get("summary", ""),
            checklist=data.get("checklist", []),
            outputs=data.get("outputs", []),
            gates=data.get("gates", []),
            subflow=data.get("subflow"),
        )


@dataclass
class Flow:
    """
    Represents a workflow definition.
    
    Supports both .flow.yml and .flow.md formats.
    """
    name: str
    version: int = 1
    description: str = ""
    when_to_use: list[str] = field(default_factory=list)
    roles: list[FlowRole] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    requires: dict = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    do_not_proceed_if: list[str] = field(default_factory=list)
    steps: list[FlowStep] = field(default_factory=list)
    body: str = ""  # Markdown body for .flow.md files
    source_path: Optional[Path] = None
    format: str = "yaml"  # "yaml" or "md"
    
    @property
    def primary_roles(self) -> list[FlowRole]:
        """Get roles marked as primary."""
        return [r for r in self.roles if r.primary]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }
        
        if self.when_to_use:
            result["when_to_use"] = self.when_to_use
        if self.roles:
            result["roles"] = {
                r.name: {"primary": r.primary, "description": r.description}
                for r in self.roles
            }
        if self.triggers:
            result["triggers"] = self.triggers
        if self.tags:
            result["tags"] = self.tags
        if self.requires:
            result["requires"] = self.requires
        if self.preconditions:
            result["preconditions"] = self.preconditions
        if self.do_not_proceed_if:
            result["do_not_proceed_if"] = self.do_not_proceed_if
        if self.steps:
            result["steps"] = [
                {
                    "id": s.id,
                    "role": s.role,
                    "summary": s.summary,
                    "checklist": s.checklist,
                    "outputs": s.outputs,
                    "gates": s.gates,
                    "subflow": s.subflow,
                }
                for s in self.steps
            ]
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict, body: str = "", 
                  source_path: Optional[Path] = None,
                  format: str = "yaml") -> "Flow":
        """Create Flow from dictionary."""
        # Parse roles
        roles_data = data.get("roles", {})
        roles = []
        if isinstance(roles_data, dict):
            for name, role_data in roles_data.items():
                roles.append(FlowRole.from_dict(name, role_data))
        
        # Parse triggers
        triggers = data.get("triggers", [])
        if isinstance(triggers, list):
            # Handle list of dicts with "on" key
            triggers = [
                t.get("on", t) if isinstance(t, dict) else t
                for t in triggers
            ]
        
        # Parse steps
        steps_data = data.get("steps", [])
        steps = [FlowStep.from_dict(s) for s in steps_data if isinstance(s, dict)]
        
        return cls(
            name=data.get("name", ""),
            version=data.get("version", 1),
            description=data.get("description", ""),
            when_to_use=data.get("when_to_use", []),
            roles=roles,
            triggers=triggers,
            tags=data.get("tags", []),
            requires=data.get("requires", {}),
            preconditions=data.get("preconditions", []),
            do_not_proceed_if=data.get("do_not_proceed_if", []),
            steps=steps,
            body=body,
            source_path=source_path,
            format=format,
        )


class FlowParser:
    """
    Parser for flow files.
    
    Supports:
    - .flow.yml - Pure YAML format (legacy)
    - .flow.md - YAML frontmatter + Markdown body (v2)
    """
    
    def __init__(self, flows_dir: Path):
        """
        Initialize parser with flows directory.
        
        Args:
            flows_dir: Path to .paircoder/flows/
        """
        self.flows_dir = Path(flows_dir)
    
    def list_flows(self) -> list[Path]:
        """
        List all flow files in the directory.
        
        Supports both .flow.yml and .flow.md extensions.
        """
        if not self.flows_dir.exists():
            return []
        
        flows = []
        
        # Find .flow.yml files (legacy)
        flows.extend(self.flows_dir.glob("*.flow.yml"))
        
        # Find .flow.md files (v2)
        flows.extend(self.flows_dir.glob("*.flow.md"))
        
        # Deduplicate by name (prefer .flow.md over .flow.yml)
        seen_names = {}
        for flow_path in flows:
            # Extract base name without extension
            name = flow_path.stem.replace(".flow", "")
            
            # Prefer .flow.md over .flow.yml
            if name in seen_names:
                if flow_path.suffix == ".md":
                    seen_names[name] = flow_path
            else:
                seen_names[name] = flow_path
        
        return sorted(seen_names.values())
    
    def parse(self, flow_path: Path) -> Optional[Flow]:
        """
        Parse a single flow file.
        
        Handles both .flow.yml and .flow.md formats.
        """
        try:
            content = flow_path.read_text(encoding="utf-8")
            
            if flow_path.suffix == ".md" or flow_path.name.endswith(".flow.md"):
                # Parse as YAML frontmatter + Markdown
                frontmatter, body = parse_frontmatter(content)
                if not frontmatter:
                    return None
                return Flow.from_dict(
                    frontmatter, 
                    body=body, 
                    source_path=flow_path,
                    format="md"
                )
            else:
                # Parse as pure YAML
                data = yaml.safe_load(content)
                if not data:
                    return None
                return Flow.from_dict(
                    data, 
                    source_path=flow_path,
                    format="yaml"
                )
        except (yaml.YAMLError, OSError) as e:
            print(f"Error parsing flow {flow_path}: {e}")
            return None
    
    def parse_all(self) -> list[Flow]:
        """Parse all flows in the directory."""
        flows = []
        for flow_path in self.list_flows():
            flow = self.parse(flow_path)
            if flow:
                flows.append(flow)
        return flows
    
    def get_flow_by_name(self, name: str) -> Optional[Flow]:
        """
        Find and parse a flow by name.
        
        Args:
            name: Flow name (e.g., "design-plan-implement")
        """
        # Try .flow.md first (preferred)
        md_path = self.flows_dir / f"{name}.flow.md"
        if md_path.exists():
            return self.parse(md_path)
        
        # Try .flow.yml (legacy)
        yml_path = self.flows_dir / f"{name}.flow.yml"
        if yml_path.exists():
            return self.parse(yml_path)
        
        # Search all flows
        for flow in self.parse_all():
            if flow.name == name:
                return flow
        
        return None
    
    def get_flows_by_trigger(self, trigger: str) -> list[Flow]:
        """
        Get all flows that match a trigger.
        
        Args:
            trigger: Trigger name (e.g., "feature_request")
        """
        matching = []
        for flow in self.parse_all():
            if trigger in flow.triggers:
                matching.append(flow)
        return matching
    
    def format_flow_list(self) -> str:
        """Format a human-readable list of flows."""
        flows = self.parse_all()
        
        if not flows:
            return "No flows found."
        
        lines = [f"Found {len(flows)} flow(s):", ""]
        
        for flow in flows:
            format_badge = "[MD]" if flow.format == "md" else "[YML]"
            lines.append(f"• {flow.name} {format_badge}")
            if flow.description:
                # Truncate description
                desc = flow.description[:60]
                if len(flow.description) > 60:
                    desc += "..."
                lines.append(f"  {desc}")
            if flow.tags:
                lines.append(f"  Tags: {', '.join(flow.tags)}")
            lines.append("")
        
        return "\n".join(lines)


# ============================================================================
# CLI Integration
# ============================================================================

def flow_list_command(flows_dir: Path) -> str:
    """
    Implementation for `bpsai-pair flow list` command.
    
    Returns formatted string of all flows.
    """
    parser = FlowParser(flows_dir)
    return parser.format_flow_list()


def flow_show_command(flows_dir: Path, name: str) -> str:
    """
    Implementation for `bpsai-pair flow show <name>` command.
    
    Returns formatted flow details or error message.
    """
    parser = FlowParser(flows_dir)
    flow = parser.get_flow_by_name(name)
    
    if not flow:
        return f"Flow not found: {name}"
    
    lines = [
        f"# {flow.name}",
        "",
        f"**Version:** {flow.version}",
        f"**Format:** {flow.format.upper()}",
        "",
    ]
    
    if flow.description:
        lines.extend([flow.description, ""])
    
    if flow.when_to_use:
        lines.append("## When to Use")
        for item in flow.when_to_use:
            lines.append(f"- {item}")
        lines.append("")
    
    if flow.roles:
        lines.append("## Roles")
        for role in flow.roles:
            primary = " (primary)" if role.primary else ""
            lines.append(f"- **{role.name}**{primary}")
            if role.description:
                lines.append(f"  {role.description}")
        lines.append("")
    
    if flow.triggers:
        lines.append(f"**Triggers:** {', '.join(flow.triggers)}")
        lines.append("")
    
    if flow.tags:
        lines.append(f"**Tags:** {', '.join(flow.tags)}")
        lines.append("")
    
    if flow.body:
        lines.extend(["---", "", flow.body])
    
    return "\n".join(lines)
