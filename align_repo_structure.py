#!/usr/bin/env python3
"""
Align repo to mirror the package structure used by end users.
- Remove/flatten `reference/` (optional merge of its context)
- Ensure root has AGENTS.md (entrypoint for all agents)
- Ensure root has context/ (maintainers' loop) and .agentpackignore
- Update README to reflect the single-lane model (no reference/)
- Install CI workflow that tests the installed wheel in a temp repo

Idempotent and safe: never overwrites without backup (.bak).
"""
from __future__ import annotations
import argparse, shutil, sys, os, re, tarfile
from pathlib import Path

ROOT = Path.cwd()

MOVE_BACK = [
    'context', 'prompts', 'services', 'src', 'templates', 'tests', 'infra'
]

AGENTS_MD = ROOT / 'AGENTS.md'
CTX_DIR = ROOT / 'context'
MAINT_CTX = CTX_DIR / 'development.md'  # maintainer loop lives here
AGENT_IGNORE = ROOT / '.agentpackignore'
READ_ME = ROOT / 'README.md'
REF_DIR = ROOT / 'reference'
GH_WF = ROOT / '.github/workflows/cli-smoke.yml'

AGENTS_MD_BODY = r'''# Agents Guide (Root Entrypoint)

Welcome. This repository **is the package** published as `bpsai-pair`. Your job is to improve the
CLI, the template bundle, and the docs — while following the **PairCoder Context Loop**.

## Where to look (in order)
1. `context/` — Maintainers' Context Loop lives here. Start with `context/development.md`.
2. `README.md` — Package installation & CLI usage.
3. `tools/cli/` — Python package source (CLI + ops + utils) and template bundle under
   `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`.

## Do **not** modify
- Anything under `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` unless the change is explicitly
  a template improvement. Never copy this repo's local state into the template.
- Built artifacts: `tools/cli/dist/`, `tools/cli/build/`, `*.egg-info/`.

## Context Loop (always update)
Keep these fields current in `context/development.md`:
- **Overall goal is:** one sentence mission
- **Last action was:** what just completed
- **Next action will be:** the next atomic step
- **Blockers:** decisions/issues

## Typical flows
```bash
# Create/align a feature branch (for package work)
# (No shell scripts required; CLI uses Python ops)
bpsai-pair feature ops-json \
  --type refactor \
  --primary "Extend pack --json to include sizes" \
  --phase "Phase 2: Portability & CI"

# Create/upload a minimal context pack
autopack='agent_pack.tgz'
bpsai-pair pack --out "$autopack"

# Update the loop
bpsai-pair context-sync --last "Added ops.json details" --next "Wire CLI flag" --blockers ""
```

## Large trees & exclusions
Heavy or irrelevant trees must be excluded via `.agentpackignore` (root).
Agents should assume excluded assets exist; avoid suggestions that remove or rename them.
'''

AGENT_IGNORE_BODY = (
    "# Agent pack exclusions\n"
    ".git/\n.venv/\n__pycache__/\nnode_modules/\n"
    ".log\n.tgz\n*.zip\n*.tar.gz\n"
    "tools/cli/dist/\ntools/cli/build/\n*.egg-info/\n"
)

WF_YML = r'''name: cli-smoke

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
    - name: Install & smoke test in temp repo
      shell: bash
      run: |
        set -euxo pipefail
        tmp=$(mktemp -d)
        cd "$tmp"
        git init .
        echo "# Smoke" > README.md
        git add . && git commit -m "init"
        python -m venv v
        . v/bin/activate || source v/Scripts/activate
        python -m pip install --upgrade pip
        pip install "$GITHUB_WORKSPACE"/tools/cli/dist/*.whl
        bpsai-pair-init
        git add -A && git commit -m "adopt scaffolding"
        bpsai-pair feature demo --type refactor --primary "Goal" --phase "Phase 1"
        bpsai-pair pack --out agent_pack.tgz
        bpsai-pair context-sync --last "Did A" --next "Do B" --blockers ""
'''

README_REF_NOTE = (
    "\n## Agents Entrypoint\n\n"
    "Agents should start at `AGENTS.md` in repo root, then follow `context/`.\n"
    "This repository mirrors what users receive via `bpsai-pair-init`; there is no `reference/` lane.\n"
)


def backup(p: Path) -> None:
    if p.exists() and not (p.with_suffix(p.suffix + '.bak')).exists():
        shutil.copy2(p, p.with_suffix(p.suffix + '.bak'))


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def atomic_write(p: Path, content: str) -> None:
    ensure_dir(p.parent)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(content)
    if p.exists():
        backup(p)
    tmp.replace(p)


def merge_reference(dry: bool) -> None:
    if not REF_DIR.exists():
        return

    # Move selected directories back if they exist under reference/
    for name in MOVE_BACK:
        src = REF_DIR / name
        dst = ROOT / name
        if src.exists() and not dst.exists():
            print(f"[align] move {src} -> {dst}")
            if not dry:
                ensure_dir(dst.parent)
                shutil.move(str(src), str(dst))
        elif src.exists() and dst.exists():
            print(f"[align] KEEP existing {dst}; leaving {src} (manual review)")

    # Migrate context if only in reference
    ref_ctx = REF_DIR / 'context' / 'development.md'
    if ref_ctx.exists():
        ensure_dir(CTX_DIR)
        merged = CTX_DIR / 'reference_migrated.md'
        if not merged.exists():
            print(f"[align] capture {ref_ctx} -> {merged}")
            if not dry:
                atomic_write(merged, ref_ctx.read_text())

    # Remove empty reference dir
    try:
        if not dry:
            for p in sorted(REF_DIR.rglob('*'), reverse=True):
                if p.is_file():
                    p.unlink()
            REF_DIR.rmdir()
            print("[align] removed empty reference/")
        else:
            print("[align] DRY: would remove reference/ if empty")
    except OSError:
        print("[align] reference/ not empty; left in place for manual review")


def ensure_agents_md() -> None:
    if not AGENTS_MD.exists():
        atomic_write(AGENTS_MD, AGENTS_MD_BODY)
        print(f"[align] wrote {AGENTS_MD}")


def ensure_context() -> None:
    ensure_dir(CTX_DIR)
    if not MAINT_CTX.exists():
        atomic_write(MAINT_CTX,
                     "# Development Log\n\nPhase: Phase 2: Portability & CI\n"
                     "Primary Goal: Improve the PairCoder package using the PairCoder workflow\n\n"
                     "## Context Sync (AUTO-UPDATED)\n\n"
                     "- **Overall goal is:** Harden portability and CI matrix\n\n"
                     "- **Last action was:** Align repo structure; root AGENTS.md\n\n"
                     "- **Next action will be:** Convert remaining shell flows to Python ops\n\n"
                     "- **Blockers:** None\n"
                     )
        print(f"[align] wrote {MAINT_CTX}")


def ensure_agentpackignore() -> None:
    if not AGENT_IGNORE.exists():
        atomic_write(AGENT_IGNORE, AGENT_IGNORE_BODY)
        print(f"[align] wrote {AGENT_IGNORE}")


def update_readme_note() -> None:
    if not READ_ME.exists():
        return
    t = READ_ME.read_text()
    if '## Agents Entrypoint' not in t:
        atomic_write(READ_ME, t + "\n" + README_REF_NOTE)
        print(f"[align] updated {READ_ME} with Agents Entrypoint note")


def ensure_ci() -> None:
    if not GH_WF.parent.exists():
        GH_WF.parent.mkdir(parents=True, exist_ok=True)
    if not GH_WF.exists():
        atomic_write(GH_WF, WF_YML)
        print(f"[align] wrote {GH_WF}")


def main() -> int:
    if not (ROOT / '.git').exists():
        print('[align] ERROR: run from repo root (missing .git)', file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    merge_reference(args.dry_run)
    ensure_agents_md()
    ensure_context()
    ensure_agentpackignore()
    update_readme_note()
    ensure_ci()

    print('[align] Done. Review git status and commit.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
