"""CLI commands for skill validation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .validator import SkillValidator, find_skills_dir

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
