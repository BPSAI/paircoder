"""Flow format loader for Paircoder-native skills.

Flows are markdown files with YAML front-matter that define reusable
workflows/skills that can be invoked during AI pair-coding sessions.

Flow files are discovered from:
  1. .paircoder/flows/**/*.md (primary location)
  2. flows/**/*.md (fallback location)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Flow:
    """Represents a parsed flow file."""

    name: str
    description: str
    body: str
    path: Path
    tags: list[str] = field(default_factory=list)
    version: str = "1.0"


def parse_flow(path: Path) -> Flow:
    """Parse a flow file with YAML front-matter and markdown body.

    Flow files must have YAML front-matter delimited by '---' lines:

        ---
        name: my-flow
        description: A short description
        tags: [coding, review]
        version: "1.0"
        ---

        # Flow body in markdown

        This is the flow content...

    Args:
        path: Path to the flow markdown file.

    Returns:
        Flow dataclass with parsed metadata and body.

    Raises:
        ValueError: If the file doesn't have valid YAML front-matter.
        FileNotFoundError: If the file doesn't exist.
    """
    content = path.read_text(encoding="utf-8")

    # Check for front-matter delimiters
    if not content.startswith("---"):
        raise ValueError(f"Flow file must start with '---': {path}")

    # Find the closing delimiter
    end_idx = content.find("\n---", 3)
    if end_idx == -1:
        raise ValueError(f"Flow file missing closing '---' delimiter: {path}")

    # Extract and parse YAML front-matter
    yaml_content = content[4:end_idx].strip()
    try:
        metadata = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML front-matter in {path}: {e}") from e

    # Extract markdown body (skip the closing --- and any leading newlines)
    body_start = end_idx + 4  # Skip \n---
    body = content[body_start:].lstrip("\n")

    # Validate required fields
    if "name" not in metadata:
        raise ValueError(f"Flow file missing required 'name' field: {path}")
    if "description" not in metadata:
        raise ValueError(f"Flow file missing required 'description' field: {path}")

    return Flow(
        name=metadata["name"],
        description=metadata["description"],
        body=body,
        path=path,
        tags=metadata.get("tags", []),
        version=str(metadata.get("version", "1.0")),
    )


def discover_flows(root: Path) -> list[Flow]:
    """Discover and parse all flow files in the repository.

    Searches for flow files in order of priority:
      1. .paircoder/flows/**/*.md
      2. flows/**/*.md (fallback)

    If both directories exist, both are searched and flows are merged.
    Duplicate flow names are resolved by preferring .paircoder/flows/.

    Args:
        root: Repository root directory.

    Returns:
        List of parsed Flow objects, sorted by name.
    """
    flows: dict[str, Flow] = {}

    # Search paths in order of priority (lower priority first, higher overwrites)
    search_paths = [
        root / "flows",  # Fallback location
        root / ".paircoder" / "flows",  # Primary location (overwrites fallback)
    ]

    for base_path in search_paths:
        if not base_path.exists():
            continue

        for flow_path in base_path.rglob("*.md"):
            if not flow_path.is_file():
                continue

            try:
                flow = parse_flow(flow_path)
                flows[flow.name] = flow
            except (ValueError, FileNotFoundError):
                # Skip invalid flow files silently during discovery
                # Users can use flow show to get detailed errors
                continue

    # Return sorted by name for deterministic output
    return sorted(flows.values(), key=lambda f: f.name)


def get_flow(root: Path, name: str) -> Optional[Flow]:
    """Get a specific flow by name.

    Args:
        root: Repository root directory.
        name: Name of the flow to retrieve.

    Returns:
        The Flow object if found, None otherwise.
    """
    flows = discover_flows(root)
    for flow in flows:
        if flow.name == name:
            return flow
    return None


def list_flow_names(root: Path) -> list[str]:
    """Get a list of all available flow names.

    Args:
        root: Repository root directory.

    Returns:
        Sorted list of flow names.
    """
    return [flow.name for flow in discover_flows(root)]
