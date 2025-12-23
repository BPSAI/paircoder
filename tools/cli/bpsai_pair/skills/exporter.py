"""
Skill Exporter - Export skills to other AI coding tool formats.

Supports:
- Cursor (.cursor/rules/)
- Continue.dev (.continue/context/)
- Windsurf (.windsurfrules)
"""

import re
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""

    CURSOR = "cursor"
    CONTINUE = "continue"
    WINDSURF = "windsurf"


class SkillExporterError(Exception):
    """Error during skill export."""

    pass


def find_project_root() -> Path:
    """Find project root by looking for .paircoder directory."""
    from ..core.ops import find_project_root as _find_project_root

    return _find_project_root()


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from content.

    Args:
        content: Markdown content with frontmatter

    Returns:
        Content without frontmatter
    """
    if not content.startswith("---"):
        return content

    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return content

    # Return content after frontmatter, stripping leading empty lines
    body = "\n".join(lines[end_idx + 1 :])
    return body.lstrip("\n")


def _get_cursor_export_path(project_dir: Path, skill_name: str) -> Path:
    """Get Cursor rules file path.

    Args:
        project_dir: Project root directory
        skill_name: Skill name

    Returns:
        Path to Cursor rules file
    """
    return project_dir / ".cursor" / "rules" / f"{skill_name}.md"


def _get_continue_export_path(project_dir: Path, skill_name: str) -> Path:
    """Get Continue.dev context file path.

    Args:
        project_dir: Project root directory
        skill_name: Skill name

    Returns:
        Path to Continue.dev context file
    """
    return project_dir / ".continue" / "context" / f"{skill_name}.md"


def _get_windsurf_export_path(project_dir: Path) -> Path:
    """Get Windsurf rules file path.

    Args:
        project_dir: Project root directory

    Returns:
        Path to Windsurf rules file
    """
    return project_dir / ".windsurfrules"


def _format_for_cursor(skill_name: str, content: str) -> str:
    """Format skill content for Cursor.

    Args:
        skill_name: Skill name
        content: Original SKILL.md content

    Returns:
        Formatted content for Cursor
    """
    body = _strip_frontmatter(content)

    # Add metadata comment
    header = f"<!-- Exported from bpsai-pair skill: {skill_name} -->\n"
    header += f"<!-- Export date: {datetime.now().strftime('%Y-%m-%d')} -->\n\n"

    return header + body


def _format_for_continue(skill_name: str, content: str) -> str:
    """Format skill content for Continue.dev.

    Args:
        skill_name: Skill name
        content: Original SKILL.md content

    Returns:
        Formatted content for Continue.dev
    """
    body = _strip_frontmatter(content)

    # Add metadata header
    header = f"# Context: {skill_name}\n\n"
    header += f"<!-- Exported from bpsai-pair -->\n\n"

    return header + body


def _format_for_windsurf(skill_name: str, content: str) -> str:
    """Format skill content for Windsurf.

    Args:
        skill_name: Skill name
        content: Original SKILL.md content

    Returns:
        Formatted content for Windsurf
    """
    body = _strip_frontmatter(content)

    # Add section markers
    section = f"\n\n## --- BEGIN SKILL: {skill_name} ---\n\n"
    section += body
    section += f"\n\n## --- END SKILL: {skill_name} ---\n"

    return section


def check_portability(skill_dir: Path) -> List[str]:
    """Check skill for portability issues.

    Args:
        skill_dir: Path to skill directory

    Returns:
        List of warning messages
    """
    warnings = []

    # Check for scripts directory
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists() and any(scripts_dir.iterdir()):
        warnings.append(
            "Skill has scripts/ directory - scripts won't work on other platforms"
        )

    # Check SKILL.md for platform-specific content
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        content = skill_file.read_text()

        # Check for bpsai-pair specific commands
        if "bpsai-pair" in content:
            warnings.append(
                "Skill references bpsai-pair commands - may not work on other platforms"
            )

        # Check for Claude Code specific features
        if "claude code" in content.lower() or "/compact" in content or "/context" in content:
            warnings.append(
                "Skill references Claude Code features - may not work on other platforms"
            )

    return warnings


def export_skill(
    skill_name: str,
    format: ExportFormat,
    skills_dir: Path,
    project_dir: Path,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Export a single skill to target format.

    Args:
        skill_name: Name of skill to export
        format: Target export format
        skills_dir: Path to skills directory
        project_dir: Project root directory
        dry_run: If True, don't create files

    Returns:
        Dict with success status and details

    Raises:
        SkillExporterError: If export fails
    """
    # Validate format
    if isinstance(format, str):
        try:
            format = ExportFormat(format)
        except ValueError:
            raise SkillExporterError(f"Invalid export format: {format}")

    # Find skill
    skill_dir = skills_dir / skill_name
    skill_file = skill_dir / "SKILL.md"

    if not skill_dir.exists() or not skill_file.exists():
        raise SkillExporterError(f"Skill not found: {skill_name}")

    # Read content
    content = skill_file.read_text()

    # Check portability
    warnings = check_portability(skill_dir)

    # Determine output path and format content
    if format == ExportFormat.CURSOR:
        output_path = _get_cursor_export_path(project_dir, skill_name)
        formatted = _format_for_cursor(skill_name, content)
    elif format == ExportFormat.CONTINUE:
        output_path = _get_continue_export_path(project_dir, skill_name)
        formatted = _format_for_continue(skill_name, content)
    elif format == ExportFormat.WINDSURF:
        output_path = _get_windsurf_export_path(project_dir)
        formatted = _format_for_windsurf(skill_name, content)
    else:
        raise SkillExporterError(f"Unsupported format: {format}")

    result = {
        "success": True,
        "skill_name": skill_name,
        "format": format.value,
        "path": str(output_path),
        "warnings": warnings,
    }

    if dry_run:
        result["dry_run"] = True
        result["would_create"] = str(output_path)
        return result

    # Create output
    if format == ExportFormat.WINDSURF:
        # Append to existing file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            existing = output_path.read_text()
            # Check if skill already exported
            if f"BEGIN SKILL: {skill_name}" in existing:
                # Replace existing section
                pattern = rf"## --- BEGIN SKILL: {skill_name} ---.*?## --- END SKILL: {skill_name} ---"
                existing = re.sub(pattern, "", existing, flags=re.DOTALL)
            formatted = existing.rstrip() + formatted
        output_path.write_text(formatted)
    else:
        # Create new file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted)

    result["created"] = str(output_path)
    return result


def export_all_skills(
    format: ExportFormat,
    skills_dir: Path,
    project_dir: Path,
    dry_run: bool = False,
) -> List[Dict[str, Any]]:
    """Export all skills to target format.

    Args:
        format: Target export format
        skills_dir: Path to skills directory
        project_dir: Project root directory
        dry_run: If True, don't create files

    Returns:
        List of result dicts for each skill
    """
    results = []

    if not skills_dir.exists():
        return results

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            try:
                result = export_skill(
                    skill_name=skill_dir.name,
                    format=format,
                    skills_dir=skills_dir,
                    project_dir=project_dir,
                    dry_run=dry_run,
                )
                results.append(result)
            except SkillExporterError as e:
                results.append({
                    "success": False,
                    "skill_name": skill_dir.name,
                    "error": str(e),
                })

    return results
