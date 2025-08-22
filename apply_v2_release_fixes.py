#!/usr/bin/env python3
"""
PairCoder v2.0 release fixes (idempotent)

Run from repo root:
  python3 scripts/apply_v2_release_fixes.py --dry-run   # preview
  python3 scripts/apply_v2_release_fixes.py             # apply

What this does:
- Bump tools/cli/pyproject.toml to version 0.2.0
- Install a portable GitHub Actions smoke matrix (ubuntu/macos/windows; py 3.10–3.12)
- Ensure smoke workflow creates/uses a `main` branch before CLI steps
- Update README: remove outdated reference/ mentions; add concise notes about --type fix/refactor,
  add "What the smoke test proves" section, ensure troubleshooting includes git branch -M main
- Ensure AGENTS.md at repo root has clear directions for agents (root entrypoint -> /context -> package dirs)
- Append CHANGELOG.md entry for 0.2.0

All writes are backed up once as <file>.bak if not already present. Re-running is safe.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path.cwd()

# ---------------------------- utils ----------------------------

def say(msg: str):
    print(f"[v2-fixes] {msg}")

def ensure_repo_root():
    if not (ROOT / ".git").exists():
        raise SystemExit("Run from repository root (where .git exists)")

def backup_once(p: Path):
    if p.exists():
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            bak.write_bytes(p.read_bytes())

def write_text(p: Path, content: str, dry: bool):
    backup_once(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    if dry:
        say(f"DRY: would write {p}")
    else:
        p.write_text(content, encoding="utf-8")
        say(f"WROTE: {p}")

def replace_regex(p: Path, pattern: str, repl: str, dry: bool, flags=re.MULTILINE):
    if not p.exists():
        return False
    s = p.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, s, flags=flags)
    if n:
        if dry:
            say(f"DRY: {p} replace {n} occurrence(s) of /{pattern}/")
        else:
            backup_once(p)
            p.write_text(new, encoding="utf-8")
            say(f"UPDATED: {p} ({n} change(s))")
        return True
    return False

def append_once(p: Path, marker: str, block: str, dry: bool):
    cur = p.read_text(encoding="utf-8") if p.exists() else ""
    if marker in cur:
        return False
    if dry:
        say(f"DRY: would append block to {p} (marker: {marker})")
    else:
        backup_once(p)
        with p.open("a", encoding="utf-8") as f:
            f.write("\n\n" + block.rstrip() + "\n")
        say(f"APPENDED: {p} ({marker})")
    return True

# ---------------------------- content ----------------------------

PYPROJECT = ROOT / "tools/cli/pyproject.toml"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
CHANGELOG = ROOT / "CHANGELOG.md"
WF = ROOT / ".github/workflows/cli-smoke.yml"

WF_YAML = r"""name: cli-smoke

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  smoke:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [ '3.10', '3.11', '3.12' ]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Build wheel
        shell: bash
        run: |
          set -euxo pipefail
          python -m pip install --upgrade pip build
          python -m build tools/cli

      - name: Install wheel
        shell: bash
        run: |
          set -euxo pipefail
          pip install tools/cli/dist/*.whl

      - name: Smoke (entrypoint)
        shell: bash
        run: |
          set -euxo pipefail
          tmp=$(mktemp -d)
          cd "$tmp"
          git init .
          # Ensure main exists to match CLI expectations
          git branch -M main
          echo "# Smoke" > README.md
          git add . && git commit -m "init"
          bpsai-pair-init
          git add -A && git commit -m "adopt scaffolding"
          bpsai-pair feature demo --type refactor --primary "Goal" --phase "Phase 1"
          bpsai-pair pack --out agent_pack.tgz
          bpsai-pair context-sync --last "Did A" --next "Do B" --blockers ""

      - name: Smoke (python -m fallback)
        shell: bash
        run: |
          set -euxo pipefail
          tmp=$(mktemp -d)
          cd "$tmp"
          git init .
          git branch -M main
          echo "# Smoke m" > README.md
          git add . && git commit -m "init"
          python -m bpsai_pair.cli init
          git add -A && git commit -m "adopt scaffolding (m)"
          python -m bpsai_pair.cli feature demo --type refactor --primary "Goal" --phase "Phase 1"
          python -m bpsai_pair.cli pack --out agent_pack.tgz
          python -m bpsai_pair.cli context-sync --last "Did A" --next "Do B" --blockers ""
"""

AGENTS_MD = """# Agents Guide (entrypoint)

Start here, then follow pointers:

1. Read `/context/development.md` – maintain the **Context Loop** after each meaningful change:
   - **Overall goal is:** …
   - **Last action was:** …
   - **Next action will be:** …
   - **Blockers:** …
2. Read `/context/agents.md` for rules and boundaries.
3. Do **not** modify cookiecutter sources under `tools/cli/bpsai_pair/data/` unless you are explicitly evolving the template. For product code and docs, update files in repo root (`/src`, `/services`, `/tests`, `/context`, `/templates`).
4. Prefer minimal, reversible changes; commit small diffs and run `bpsai-pair context-sync` to keep the loop fresh.
"""

README_TWEAKS = {
    # Remove stale mention of a dedicated reference/ directory
    r"(?s)## Reference Project\n.*?## Getting Started": "## Getting Started",
}

README_APPEND_MARKER_1 = "[USAGE_TYPES_SECTION]"
README_APPEND_BLOCK_1 = """
### Branch types
You can create feature, fix, or refactor branches via:
```bash
bpsai-pair feature <name> --type feature   # default
bpsai-pair feature <name> --type fix
bpsai-pair feature <name> --type refactor
```
"""

README_APPEND_MARKER_2 = "[SMOKE_PROVES_SECTION]"
README_APPEND_BLOCK_2 = """
### What the smoke test proves
The CI workflow builds the wheel, installs it, and runs the golden path:

1. `bpsai-pair-init` – adopt scaffolding (non-destructive)
2. `bpsai-pair feature demo --type refactor` – create a working branch and update context
3. `bpsai-pair pack --out agent_pack.tgz` – produce a context pack for agents
4. `bpsai-pair context-sync --last … --next …` – update the Context Loop and commit
"""

README_TROUBLE_MARK = "[TROUBLE_BRANCH_MAIN]"
README_TROUBLE_BLOCK = """
> **Tip (branches):** If your local git defaults to `master`, run `git branch -M main` once after `git init` so CLI commands that expect `main` work out of the box.
"""

CHANGELOG_BLOCK = """
## 0.2.0
- Cross-platform CLI (no Bash required) – core actions implemented in Python
- Portable CI smoke matrix (Ubuntu, macOS, Windows; Python 3.10–3.12)
- `feature --type` supports `feature|fix|refactor`
- Improved docs: root `AGENTS.md`, branch types, smoke proof narrative, troubleshooting
- Template/data hygiene and clearer agent boundaries
"""

# ---------------------------- main ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ensure_repo_root()

    # 1) bump pyproject version to 0.2.0
    if PYPROJECT.exists():
        replaced = replace_regex(
            PYPROJECT,
            r"^version\s*=\s*\"[0-9]+\.[0-9]+\.[0-9]+\"",
            'version = "0.2.0"',
            args.dry_run,
        )
        if not replaced:
            say("pyproject version already 0.2.0 or pattern not found")
    else:
        say("WARN: tools/cli/pyproject.toml not found")

    # 2) write workflow yaml
    write_text(WF, WF_YAML, args.dry_run)

    # 3) AGENTS.md (root) ensure exists and contains guidance
    if AGENTS.exists():
        append_once(AGENTS, "Prefer minimal, reversible changes", AGENTS_MD, args.dry_run)
    else:
        write_text(AGENTS, AGENTS_MD, args.dry_run)

    # 4) README tweaks
    if README.exists():
        for pat, repl in README_TWEAKS.items():
            replace_regex(README, pat, repl, args.dry_run, flags=re.MULTILINE)
        append_once(README, README_APPEND_MARKER_1, README_APPEND_BLOCK_1, args.dry_run)
        append_once(README, README_APPEND_MARKER_2, README_APPEND_BLOCK_2, args.dry_run)
        append_once(README, README_TROUBLE_MARK, README_TROUBLE_BLOCK, args.dry_run)
    else:
        say("WARN: README.md not found")

    # 5) CHANGELOG
    if CHANGELOG.exists():
        append_once(CHANGELOG, "## 0.2.0", CHANGELOG_BLOCK, args.dry_run)
    else:
        write_text(CHANGELOG, CHANGELOG_BLOCK, args.dry_run)

    say("Done. Review git diff, run tests, then commit and push.")

if __name__ == "__main__":
    main()
