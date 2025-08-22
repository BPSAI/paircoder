from __future__ import annotations

from pathlib import Path
import shutil
import json
import typer
from rich import print

from . import init_bundled_cli
from . import pyutils
from . import jsonio
from .utils import repo_root, ensure_executable
from .adapters import Shell

app = typer.Typer(add_completion=False, help="bpsai-pair: AI pair-coding workflow CLI")


# -----------------------------------------------------------------------------
# init
# -----------------------------------------------------------------------------
@app.command()
def init(
    template: str = typer.Argument(
        None, help="Path to template (optional, defaults to bundled template)"
    )
):
    """Initialize repo with governance, context, prompts, scripts, and workflows."""
    root = repo_root()

    # If no template provided, use bundled initializer.
    if template is None:
        return init_bundled_cli.main()

    template_dir = Path(template)
    src = template_dir / "{{cookiecutter.project_slug}}"
    if not src.exists():
        raise typer.BadParameter(
            "Template path looks wrong. Expecting {{cookiecutter.project_slug}} under template root."
        )

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

    print(
        "[green]Initialized repo with pair-coding scaffolding (non-destructive). Review diffs and commit.[/green]"
    )


# -----------------------------------------------------------------------------
# feature
# -----------------------------------------------------------------------------
@app.command()
def feature(
    name: str = typer.Argument(..., help="feature branch name (without prefix)"),
    primary: str = typer.Option("", help="Primary goal to stamp into context"),
    phase: str = typer.Option("", help="Phase goal for Next action"),
    force: bool = typer.Option(False, help="Bypass dirty-tree check (not recommended)"),
    type: str = typer.Option(
        "feature",
        "--type",
        help="Branch type: feature|fix|refactor",
        case_sensitive=False,
    ),
):
    """Create feature branch and scaffold context via scripts/new_feature.sh if present."""
    # normalize branch type
    t = (type or "feature").lower()
    if t not in {"feature", "fix", "refactor"}:
        raise typer.BadParameter("--type must be one of: feature, fix, refactor")

    root = repo_root()
    script = root / "scripts" / "new_feature.sh"
    if not script.exists():
        raise typer.BadParameter(
            "Scaffolding not found. Run 'bpsai-pair-init' (or 'bpsai-pair init') first."
        )
    ensure_executable(script)

    name_with_prefix = f"{t}/{name}"
    cmd = [str(script), name_with_prefix]
    if primary:
        cmd += ["--primary", primary]
    if phase:
        cmd += ["--phase", phase]
    if force:
        cmd += ["--force"]

    out = Shell.run(cmd, cwd=root)
    print(out)


# -----------------------------------------------------------------------------
# pack
# -----------------------------------------------------------------------------
@app.command()
def pack(
    out: str = typer.Option("agent_pack.tgz", help="Output archive name"),
    extra: list[str] | None = typer.Option(None, help="Additional paths to include"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview files; do not write archive"
    ),
    list_only: bool = typer.Option(
        False, "--list", help="List files included in pack"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON result"),
):
    """Create agent context package via scripts/agent_pack.sh."""
    root = repo_root()

    # Preview / list modes implemented in Python for speed & reliability.
    if dry_run or list_only:
        excludes: list[str] = []
        ignore = root / ".agentpackignore"
        if ignore.exists():
            excludes = [
                ln.strip() for ln in ignore.read_text().splitlines() if ln.strip()
            ]
        # We restrict to context/* to keep previews lightweight and predictable.
        files = [
            str(p)
            for p in pyutils.project_files(root, excludes=excludes)
            if str(p).startswith("context/")
        ]
        if json_out:
            print(jsonio.dump({"dry_run": dry_run, "list": list_only, "files": files}))
            return
        if list_only:
            print("\n".join(files))
            return
        print(f"Would pack {len(files)} files")
        return

    # Otherwise, delegate archiving to the shell script.
    script = root / "scripts" / "agent_pack.sh"
    if not script.exists():
        raise typer.BadParameter(
            "Scaffolding not found. Run 'bpsai-pair-init' (or 'bpsai-pair init') first."
        )
    ensure_executable(script)
    cmd = [str(script), out]
    if extra:
        cmd += ["--extra", *extra]

    res = Shell.run(cmd, cwd=root)
    print(res)
    if json_out:
        archive = None
        for ln in res.splitlines():
            if "Created " in ln and ".tgz" in ln:
                archive = ln.split("Created ", 1)[-1].split()[0]
                break
        print(jsonio.dump({"archive": archive, "ok": True}))


# -----------------------------------------------------------------------------
# context-sync
# -----------------------------------------------------------------------------
@app.command("context-sync")
def context_sync(
    overall: str = typer.Option(None, help="Overall goal override"),
    last: str = typer.Option(..., help="What changed and why"),
    nxt: str = typer.Option(
        ..., "--nxt", "--next", help="Next smallest valuable step"
    ),
    blockers: str = typer.Option("", help="Blockers/Risks"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON result"),
):
    """Update the Context Loop in /context/development.md programmatically."""
    root = repo_root()
    dev = root / "context" / "development.md"

    if not dev.exists():
        dev.parent.mkdir(parents=True, exist_ok=True)
        dev.write_text(
            "# Development Log\n\n"
            "**Phase:** (init)\n"
            "**Primary Goal:** (init)\n\n"
            "## Context Sync (AUTO-UPDATED)\n\n"
            "- **Overall goal is:**\n"
            "- **Last action was:**\n"
            "- **Next action will be:**\n"
            "- **Blockers:**\n"
        )

    text = dev.read_text()

    def replace_line(prefix: str, new_value: str, blob: str) -> str:
        import re

        pattern = rf"({prefix}\s*:).*"
        repl = rf"\1 {new_value}"
        return re.sub(pattern, repl, blob)

    if overall:
        text = replace_line("Overall goal is", overall, text)
    text = replace_line("Last action was", last, text)
    text = replace_line("Next action will be", nxt, text)
    if blockers:
        text = replace_line("Blockers", blockers, text)

    dev.write_text(text)
    print("[green]Context Sync updated.[/green]")
    if json_out:
        print(jsonio.dump({"updated": True}))
