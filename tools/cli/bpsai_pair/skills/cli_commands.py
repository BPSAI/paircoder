"""CLI commands for skill validation and installation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .validator import SkillValidator, find_skills_dir
from .installer import (
    install_skill,
    SkillInstallerError,
    SkillSource,
    parse_source,
    get_target_dir,
    extract_skill_name,
)
from .exporter import (
    export_skill,
    export_all_skills,
    check_portability,
    ExportFormat,
    SkillExporterError,
)
from .suggestion import (
    suggest_skills,
    PatternDetector,
    SkillSuggester,
    SkillDraftCreator,
    HistoryParser,
    SkillSuggestionError,
)

console = Console()

skill_app = typer.Typer(
    help="Manage and validate Claude Code skills",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@skill_app.command("validate")
def skill_validate(
    skill_name: Optional[str] = typer.Argument(None, help="Specific skill to validate"),
    fix: bool = typer.Option(False, "--fix", help="Auto-correct simple issues"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Validate skills against Anthropic specs.

    Checks:
    - Frontmatter has only 'name' and 'description' fields
    - Description under 1024 characters
    - 3rd-person voice (warns on 2nd person)
    - File under 500 lines
    - Name matches directory name

    Use --fix to auto-correct simple issues.
    """
    import json

    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    validator = SkillValidator(skills_dir)

    if skill_name:
        # Validate single skill
        skill_dir = skills_dir / skill_name
        if not skill_dir.exists():
            console.print(f"[red]Skill not found: {skill_name}[/red]")
            raise typer.Exit(1)

        if fix:
            fixed = validator.fix_skill(skill_dir)
            if fixed:
                console.print(f"[green]Fixed issues in {skill_name}[/green]")

        result = validator.validate_skill(skill_dir)
        if json_out:
            console.print(json.dumps(result, indent=2))
        else:
            _display_result(skill_name, result)
        raise typer.Exit(0 if result["valid"] else 1)

    # Validate all skills
    results = validator.validate_all()

    if not results:
        console.print("[dim]No skills found in .claude/skills/[/dim]")
        return

    if fix:
        console.print("[cyan]Attempting to fix issues...[/cyan]\n")
        for skill_name_key in results:
            skill_dir = skills_dir / skill_name_key
            fixed = validator.fix_skill(skill_dir)
            if fixed:
                console.print(f"  [green]Fixed: {skill_name_key}[/green]")
        console.print()
        # Re-validate after fixes
        results = validator.validate_all()

    if json_out:
        console.print(json.dumps(results, indent=2))
        return

    console.print(f"\n[bold]Validating {len(results)} skills...[/bold]\n")

    for skill_name_key, result in sorted(results.items()):
        _display_result(skill_name_key, result)

    # Summary
    summary = validator.get_summary(results)
    console.print(f"\n[bold]Summary:[/bold] {summary['passed']} pass, {summary['with_warnings']} warnings, {summary['failed']} errors")

    if summary["failed"] > 0:
        raise typer.Exit(1)


@skill_app.command("list")
def skill_list():
    """List all skills in .claude/skills/."""
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills.append(skill_dir.name)

    if not skills:
        console.print("[dim]No skills found.[/dim]")
        return

    table = Table(title=f"Skills ({len(skills)})")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="dim")

    for skill_name in sorted(skills):
        table.add_row(skill_name, f".claude/skills/{skill_name}/")

    console.print(table)


def _display_result(name: str, result: dict) -> None:
    """Display validation result for a skill.

    Args:
        name: Skill name
        result: Validation result dict
    """
    if result["valid"] and not result["warnings"]:
        console.print(f"[green]\u2705 {name}[/green]")
    elif result["valid"]:
        console.print(f"[yellow]\u26a0\ufe0f  {name}[/yellow]")
        for warning in result["warnings"]:
            console.print(f"   [dim]- {warning}[/dim]")
    else:
        console.print(f"[red]\u274c {name}[/red]")
        for error in result["errors"]:
            console.print(f"   [red]- {error}[/red]")
        for warning in result["warnings"]:
            console.print(f"   [dim]- {warning}[/dim]")


def find_project_root() -> Path:
    """Find project root by looking for .paircoder directory."""
    from ..core.ops import find_project_root as _find_project_root

    return _find_project_root()


@skill_app.command("install")
def skill_install(
    source: str = typer.Argument(..., help="Source URL or local path to skill"),
    project: bool = typer.Option(False, "--project", help="Install to project .claude/skills/"),
    personal: bool = typer.Option(False, "--personal", help="Install to ~/.claude/skills/"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Install with different name"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing skill"),
):
    """Install a skill from URL or local path.

    Examples:

        # Install from local path
        bpsai-pair skill install ~/my-skills/custom-review

        # Install from GitHub
        bpsai-pair skill install https://github.com/user/repo/tree/main/.claude/skills/skill

        # Install with different name
        bpsai-pair skill install ./my-skill --name renamed-skill

        # Install to personal directory
        bpsai-pair skill install ./my-skill --personal

        # Overwrite existing skill
        bpsai-pair skill install ./my-skill --force
    """
    try:
        # Parse source to show what we're doing
        source_type, parsed = parse_source(source)
        skill_name = name or extract_skill_name(source)

        console.print(f"\n[bold]Installing skill: {skill_name}[/bold]")

        if source_type == SkillSource.PATH:
            console.print(f"  Source: [dim]{parsed}[/dim]")
        else:
            console.print(f"  Source: [dim]{source}[/dim]")

        # If neither --project nor --personal specified, prompt (non-interactive defaults to project)
        if not project and not personal:
            # Default to project installation
            project = True

        # Get target directory for display
        target_dir = get_target_dir(project=project, personal=personal)
        console.print(f"  Target: [dim]{target_dir}[/dim]\n")

        console.print("[cyan]Downloading...[/cyan]" if source_type == SkillSource.URL else "[cyan]Copying...[/cyan]")

        # Install
        result = install_skill(
            source,
            project=project,
            personal=personal,
            name=name,
            force=force,
        )

        console.print("[cyan]Validating...[/cyan]")
        console.print("  [green]\u2713[/green] Frontmatter valid")
        console.print("  [green]\u2713[/green] Description under 1024 chars")
        console.print("  [green]\u2713[/green] No conflicts with existing skills" if not force else "  [yellow]\u2713[/yellow] Overwrote existing skill")

        console.print(f"\n[green]\u2705 Installed {result['skill_name']} to {result['installed_to']}/[/green]")

    except SkillInstallerError as e:
        console.print(f"\n[red]\u274c Installation failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]\u274c Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@skill_app.command("export")
def skill_export(
    skill_name: Optional[str] = typer.Argument(None, help="Skill to export (or use --all)"),
    format: str = typer.Option("cursor", "--format", "-f", help="Export format: cursor, continue, windsurf"),
    all_skills: bool = typer.Option(False, "--all", "-a", help="Export all skills"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be created without creating"),
):
    """Export skills to other AI coding tool formats.

    Supported formats:
    - cursor: Export to .cursor/rules/
    - continue: Export to .continue/context/
    - windsurf: Export to .windsurfrules

    Examples:

        # Export single skill to Cursor
        bpsai-pair skill export my-skill --format cursor

        # Export all skills to Continue.dev
        bpsai-pair skill export --all --format continue

        # Dry run to see what would be created
        bpsai-pair skill export my-skill --format windsurf --dry-run
    """
    if not skill_name and not all_skills:
        console.print("[red]Error: Specify a skill name or use --all[/red]")
        raise typer.Exit(1)

    # Parse format
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        console.print(f"[red]Error: Invalid format '{format}'. Use: cursor, continue, windsurf[/red]")
        raise typer.Exit(1)

    # Get directories
    try:
        skills_dir = find_skills_dir()
        project_dir = find_project_root()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print("[yellow]Dry run mode - no files will be created[/yellow]\n")

    try:
        if all_skills:
            console.print(f"[bold]Exporting all skills to {format}...[/bold]\n")
            results = export_all_skills(
                format=export_format,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=dry_run,
            )

            if not results:
                console.print("[dim]No skills found to export.[/dim]")
                return

            success_count = sum(1 for r in results if r.get("success"))
            for result in results:
                if result.get("success"):
                    path_key = "would_create" if dry_run else "path"
                    console.print(f"  [green]\u2713[/green] {result['skill_name']} → {result.get(path_key, 'N/A')}")
                    for warning in result.get("warnings", []):
                        console.print(f"    [yellow]⚠ {warning}[/yellow]")
                else:
                    console.print(f"  [red]\u274c {result['skill_name']}: {result.get('error', 'Unknown error')}[/red]")

            console.print(f"\n[bold]Exported {success_count}/{len(results)} skills[/bold]")

        else:
            console.print(f"[bold]Exporting {skill_name} to {format}...[/bold]\n")

            # Check portability first
            skill_dir = skills_dir / skill_name
            if skill_dir.exists():
                warnings = check_portability(skill_dir)
                for warning in warnings:
                    console.print(f"[yellow]⚠ {warning}[/yellow]")
                if warnings:
                    console.print()

            result = export_skill(
                skill_name=skill_name,
                format=export_format,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=dry_run,
            )

            if dry_run:
                console.print(f"[dim]Would create: {result.get('would_create')}[/dim]")
            else:
                console.print(f"[green]\u2705 Exported to {result.get('path')}[/green]")

    except SkillExporterError as e:
        console.print(f"\n[red]\u274c Export failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]\u274c Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@skill_app.command("suggest")
def skill_suggest(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    create: Optional[int] = typer.Option(None, "--create", "-c", help="Create draft for suggestion N"),
    min_occurrences: int = typer.Option(3, "--min", "-m", help="Minimum pattern occurrences"),
):
    """Analyze session history and suggest new skills.

    Scans recent workflow patterns and suggests skills that could automate
    frequently repeated command sequences.

    Examples:

        # Show suggestions
        bpsai-pair skill suggest

        # Output as JSON
        bpsai-pair skill suggest --json

        # Create draft for first suggestion
        bpsai-pair skill suggest --create 1

        # Require at least 5 occurrences
        bpsai-pair skill suggest --min 5
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

    console.print("[cyan]Analyzing session patterns...[/cyan]\n")

    # Get suggestions
    suggestions = suggest_skills(
        history_dir=history_dir,
        skills_dir=skills_dir,
        min_occurrences=min_occurrences,
    )

    if json_out:
        output = {
            "suggestions": suggestions,
            "total": len(suggestions),
        }
        console.print(json.dumps(output, indent=2))
        return

    if not suggestions:
        console.print("[dim]No patterns found that would benefit from a skill.[/dim]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  - Patterns need at least 3 occurrences by default")
        console.print("  - Try using --min to lower the threshold")
        console.print("  - More session history helps detect patterns")
        return

    console.print(f"[bold]Suggested Skills ({len(suggestions)}):[/bold]\n")

    for i, suggestion in enumerate(suggestions, 1):
        name = suggestion.get("name", "unknown")
        confidence = suggestion.get("confidence", 0)
        description = suggestion.get("description", "")
        occurrences = suggestion.get("occurrences", 0)
        estimated_savings = suggestion.get("estimated_savings", "")
        overlaps = suggestion.get("overlaps_with", [])

        # Confidence indicator
        if confidence >= 80:
            conf_style = "green"
        elif confidence >= 60:
            conf_style = "yellow"
        else:
            conf_style = "dim"

        console.print(f"[bold]{i}. {name}[/bold] [{conf_style}](confidence: {confidence}%)[/{conf_style}]")
        console.print(f"   [dim]{description}[/dim]")
        console.print(f"   Pattern occurrences: {occurrences}")
        if estimated_savings:
            console.print(f"   Estimated savings: {estimated_savings}")
        if overlaps:
            console.print(f"   [yellow]⚠ May overlap with: {', '.join(overlaps)}[/yellow]")
        console.print()

    # Handle --create option
    if create is not None:
        if create < 1 or create > len(suggestions):
            console.print(f"[red]Invalid suggestion number. Choose 1-{len(suggestions)}[/red]")
            raise typer.Exit(1)

        suggestion = suggestions[create - 1]
        console.print(f"[cyan]Creating draft for: {suggestion['name']}[/cyan]")

        try:
            creator = SkillDraftCreator(skills_dir=skills_dir)
            result = creator.create_draft(suggestion)

            if result["success"]:
                console.print(f"[green]\u2705 Created draft: {result['path']}[/green]")

                validation = result.get("validation", {})
                if validation.get("valid"):
                    console.print("   [green]\u2713[/green] Passes validation")
                else:
                    console.print("   [yellow]\u26a0[/yellow] Review validation warnings")
                    for error in validation.get("errors", []):
                        console.print(f"      [red]{error}[/red]")

        except SkillSuggestionError as e:
            console.print(f"[red]\u274c Failed to create draft: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[dim]Use --create N to create a draft for suggestion N[/dim]")
