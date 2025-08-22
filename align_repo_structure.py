#!/usr/bin/env python3
"""
CI & Docs Alignment Patch
Run from repo root:
  python3 scripts/apply_ci_and_docs_patch.py --dry-run   # preview
  python3 scripts/apply_ci_and_docs_patch.py             # apply

What this does:
1) Ensures root AGENTS.md exists and points agents to /context and package dirs.
2) Appends a clear "Windows & Cross‑Platform" section to README.md.
3) Installs/updates a robust cross‑platform GitHub Actions smoke workflow that:
   - Builds the wheel from tools/cli
   - Installs it directly with the runner Python (no venv activation complexity)
   - Runs CLI commands using entry points AND python -m fallback
   - Works on ubuntu/macos/windows
4) Adds/updates .agentpackignore with common noise (dist, build, .venv, etc.)

Idempotent: makes .bak on first write; safe to re‑run.
"""
from __future__ import annotations
import argparse, shutil
from pathlib import Path

ROOT = Path.cwd()
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
AGENT_IGNORE = ROOT / ".agentpackignore"
WF = ROOT / ".github/workflows/cli-smoke.yml"

WIN_SECT = """
## Windows & Cross‑Platform

PairCoder CLI is fully Python‑backed (no Bash required). On Windows use:

```powershell
# Create venv (optional)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the package (from PyPI or local wheel)
pip install bpsai-pair
# or: pip install path\to\dist\bpsai_pair-*.whl

# Use the CLI
bpsai-pair --help
bpsai-pair-init
bpsai-pair feature demo --type refactor --primary "Goal" --phase "Phase 1"
bpsai-pair pack --out agent_pack.tgz
bpsai-pair context-sync --last "A" --next "B" --blockers ""
```

If the entry point is not on PATH for some reason, use the module form:

```powershell
python -m bpsai_pair.cli --help
```
"""

AGENTS_BODY = """
# Agents Guide (Root Entrypoint)

Start here. This repository **is the published package** `bpsai-pair`. Your job is to improve the
CLI, the template bundle, and the docs while following the **PairCoder Context Loop**.

## Where to look (in order)
1. `context/` → Maintainers’ Context Loop (`context/development.md`).
2. `README.md` → Package install & CLI usage.
3. `tools/cli/` → Python package source, with template bundle under
   `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`.

## Do **not** modify
- Built artifacts: `tools/cli/dist/`, `tools/cli/build/`, `*.egg-info/`.
- Template bundle unless change is explicitly a template improvement.

## Context Loop (always keep current)
Update in `context/development.md`:
- **Overall goal is:** one sentence mission
- **Last action was:** what just completed
- **Next action will be:** the next atomic step
- **Blockers:** decisions/issues

## Typical flows
```bash
bpsai-pair feature ops-json \
  --type refactor \
  --primary "Extend pack --json to include sizes" \
  --phase "Phase 2: Portability & CI"

autopack=agent_pack.tgz
bpsai-pair pack --out "$autopack"

bpsai-pair context-sync \
  --last "Added ops.json details" \
  --next "Wire CLI flag" \
  --blockers ""
```
"""

AGENTIGNORE = (
    "# Agent pack exclusions\n"
    ".git/\n.venv/\n__pycache__/\nnode_modules/\n"
    "*.log\n*.tgz\n*.zip\n*.tar.gz\n"
    "tools/cli/dist/\n"
    "tools/cli/build/\n"
    "*.egg-info/\n"
)

WF_YML = """name: cli-smoke
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  smoke:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        py: ['3.10', '3.11', '3.12']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.py }}
      - name: Build wheel
        run: |
          python -m pip install --upgrade pip build
          python -m build tools/cli
      - name: Install package
        run: |
          python -m pip install --upgrade pip
          python -m pip install tools/cli/dist/*.whl
      - name: Smoke test (wheel entrypoint)
        shell: bash
        run: |
          set -euxo pipefail
          tmp=$(python - <<'PY'\nimport tempfile, pathlib; d=tempfile.mkdtemp(); print(d)\nPY
          )
          cd "$tmp"
          git init .
          echo "# Smoke" > README.md
          git add . && git commit -m "init"

          # Use entry point first
          bpsai-pair --help
          bpsai-pair-init
          git add -A && git commit -m "adopt scaffolding"
          bpsai-pair feature demo --type refactor --primary "Goal" --phase "Phase 1"
          bpsai-pair pack --out agent_pack.tgz
          bpsai-pair context-sync --last "Did A" --next "Do B" --blockers ""
      - name: Smoke test (python -m fallback)
        run: |
          tmp=$(python - <<'PY'\nimport tempfile, pathlib; d=tempfile.mkdtemp(); print(d)\nPY
          )
          cd "$tmp"
          git init .
          echo "# Module Smoke" > README.md
          git add . && git commit -m "init"

          python -m bpsai_pair.cli --help
          python -m bpsai_pair.cli init
          git add -A && git commit -m "adopt scaffolding"
          python -m bpsai_pair.cli feature demo --type refactor --primary "Goal" --phase "Phase 1"
          python -m bpsai_pair.cli pack --out agent_pack.tgz
          python -m bpsai_pair.cli context-sync --last "Did A" --next "Do B" --blockers ""
"""


def backup(p: Path):
    b = p.with_suffix(p.suffix + ".bak")
    if p.exists() and not b.exists():
        shutil.copy2(p, b)


def write_if_missing(path: Path, content: str, dry: bool):
    if path.exists():
        return False
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup(path)
        path.write_text(content)
    return True


def append_once(path: Path, content: str, marker: str, dry: bool):
    text = path.read_text() if path.exists() else ""
    if marker in text:
        return False
    if not dry:
        backup(path)
        path.write_text(text + ("\n\n" if text and not text.endswith("\n") else "") + content)
    return True


def ensure_agents_md(dry: bool):
    created = write_if_missing(AGENTS, AGENTS_BODY.strip()+"\n", dry)
    print(f"[ci-docs] {'CREATED' if created else 'OK'}: {AGENTS}")


def ensure_readme_windows(dry: bool):
    if not README.exists():
        print("[ci-docs] SKIP: README.md not found")
        return
    changed = append_once(README, WIN_SECT.strip()+"\n", "Windows & Cross‑Platform", dry)
    print(f"[ci-docs] {'APPENDED' if changed else 'OK'}: README Windows note")


def ensure_agentpackignore(dry: bool):
    changed = False
    if not AGENT_IGNORE.exists():
        if not dry:
            AGENT_IGNORE.write_text(AGENTIGNORE)
        changed = True
    else:
        txt = AGENT_IGNORE.read_text()
        for line in ["tools/cli/dist/", "tools/cli/build/", "*.egg-info/"]:
            if line not in txt:
                txt += ("\n" if not txt.endswith("\n") else "") + line + "\n"
                changed = True
        if changed and not dry:
            backup(AGENT_IGNORE)
            AGENT_IGNORE.write_text(txt)
    print(f"[ci-docs] {'UPDATED' if changed else 'OK'}: .agentpackignore")


def ensure_workflow(dry: bool):
    wrote = False
    if not WF.exists():
        wrote = True
        if not dry:
            WF.parent.mkdir(parents=True, exist_ok=True)
            WF.write_text(WF_YML)
    else:
        # Overwrite with latest content (keeps behavior deterministic)
        wrote = True
        if not dry:
            backup(WF)
            WF.write_text(WF_YML)
    print(f"[ci-docs] {'WROTE' if wrote else 'OK'}: {WF}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if not (ROOT/'.git').exists():
        print('[ci-docs] ERROR: run from repo root (missing .git)')
        return 1

    ensure_agents_md(args.dry_run)
    ensure_readme_windows(args.dry_run)
    ensure_agentpackignore(args.dry_run)
    ensure_workflow(args.dry_run)

    print('[ci-docs] Done. Review git status and commit.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
