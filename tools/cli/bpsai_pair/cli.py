from . import init_bundled_cli
from pathlib import Path
import shutil
import typer
from rich import print

from .utils import repo_root, ensure_executable
from .adapters import Shell

app = typer.Typer(add_completion=False, help="bpsai-pair: AI pair-coding workflow CLI")

@app.command()
def init(template: str = typer.Argument(None, help='Path to template (optional, defaults to bundled template)')):
    """Initialize repo with governance, context, prompts, scripts, and workflows."""
    root = repo_root()
    src = template_dir / "{{cookiecutter.project_slug}}"
    if not src.exists():
        raise typer.BadParameter("Template path looks wrong. Expecting {{cookiecutter.project_slug}} under template root.")

    def copytree(src_p: Path, dst_p: Path):
        for p in src_p.rglob("*"):
            if p.is_dir():
                (dst_p / p.relative_to(src_p)).mkdir(parents=True, exist_ok=True)
            else:
                dst = dst_p / p.relative_to(src_p)
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dst)

    copytree(src, root)

    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        for s in scripts_dir.glob("*.sh"):
            ensure_executable(s)

    print("[green]Initialized repo with pair-coding scaffolding (non-destructive). Review diffs and commit.[/green]")

@app.command()
def feature(
    name: str = typer.Argument(..., help="feature branch name (without prefix)"),
    primary: str = typer.Option("", help="Primary goal to stamp into context"),
    phase: str = typer.Option("", help="Phase goal for Next action"),
    force: bool = typer.Option(False, help="Bypass dirty-tree check (not recommended)"),
):
    """Create feature branch and scaffold context via scripts/new_feature.sh if present."""
    root = repo_root()
    script = root / "scripts" / "new_feature.sh"
    if not script.exists():
        raise typer.Exit(code=1)
    ensure_executable(script)
    cmd = [str(script), name]
    if primary:
        cmd += ["--primary", primary]
    if phase:
        cmd += ["--phase", phase]
    if force:
        cmd += ["--force"]
    out = Shell.run(cmd, cwd=root)
    print(out)

@app.command()
def pack(
    out: str = typer.Option("agent_pack.tgz", help="Output archive name"),
    extra: list[str] = typer.Option(None, help="Additional paths to include", rich_help_panel="Options"),
):
    """Create agent context package via scripts/agent_pack.sh."""
    root = repo_root()
    script = root / "scripts" / "agent_pack.sh"
    if not script.exists():
        raise typer.Exit(code=1)
    ensure_executable(script)
    cmd = [str(script), out]
    if extra:
        cmd += ["--extra", *extra]
    out = Shell.run(cmd, cwd=root)
    print(out)

@app.command("context-sync")
def context_sync(
    overall: str = typer.Option(None, help="Overall goal override"),
    last: str = typer.Option(..., help="What changed and why"),
    nxt: str = typer.Option(..., help="Next smallest valuable step"),
    blockers: str = typer.Option("", help="Blockers/Risks"),
):
    """Update the Context Loop in /context/development.md programmatically."""
    root = repo_root()
    dev = root / "context" / "development.md"
    if not dev.exists():
        dev.parent.mkdir(parents=True, exist_ok=True)
        dev.write_text('# Development Log

**Phase:** (init)
**Primary Goal:** (init)

## Context Sync (AUTO-UPDATED)

- **Overall goal is:**
- **Last action was:**
- **Next action will be:**
- **Blockers:**
')
text = dev.read_text()

    def replace_line(prefix: str, new_value: str) -> str:
        import re
        pattern = rf"({prefix}\s*:).*"
        repl = rf"\1 {new_value}"
        return re.sub(pattern, repl, text)

    if overall:
        text = replace_line("Overall goal is", overall)
    text = replace_line("Last action was", last)
    text = replace_line("Next action will be", nxt)
    if blockers:
        text = replace_line("Blockers/Risks", blockers)
    dev.write_text(text)
    print("[green]Context Sync updated.[/green]")
