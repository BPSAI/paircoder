from . import pyutils
from . import jsonio
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
, type: str = typer.Option('feature', '--type', help='Branch type: feature|fix|refactor', case_sensitive=False)):
    """Create feature branch and scaffold context via scripts/new_feature.sh if present."""
    
    # normalize branch type
    t = (type or 'feature').lower()
    if t not in {'feature','fix','refactor'}:
        raise typer.BadParameter("--type must be one of: feature, fix, refactor")
    # adjust first argument (name) into typed branch later in script invocation
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
, dry_run: bool = typer.Option(False, '--dry-run', help='Preview files; do not write archive'), list_only: bool = typer.Option(False, '--list', help='List files included in pack'), json_out: bool = typer.Option(False, '--json', help='Emit JSON result')):
    """Create agent context package via scripts/agent_pack.sh."""
    
    pack_preview_mode = dry_run or list_only
    # Try to discover excludes from .agentpackignore in project root
    excludes = []
    ignore = root / '.agentpackignore'
    if ignore.exists():
        excludes = [ln.strip() for ln in ignore.read_text().splitlines() if ln.strip()]
    files = []
    if pack_preview_mode:
        files = [str(p) for p in pyutils.project_files(root, excludes=excludes) if str(p).startswith('context/')]
        # we intentionally keep preview scope narrow (context/*) to avoid heavy scans
        if json_out:
            print(jsonio.dump({'dry_run': dry_run, 'list': list_only, 'files': files}))
            return
        if list_only:
            print('\n'.join(files))
            return
        # dry-run default: print count
        print(f"Would pack {len(files)} files")
        return
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
