#!/usr/bin/env bash
set -euo pipefail

say(){ printf "[step3] %s\n" "$*"; }
ensure_repo_root(){ [ -d .git ] || { echo "Run from repo root"; exit 1; }; }
backup(){ [ -f "$1" ] && cp -n "$1" "$1.bak" || true; }
write_file(){ local p="$1"; shift; backup "$p"; mkdir -p "$(dirname "$p")"; printf "%s" "$*" > "$p"; git add "$p" 2>/dev/null || true; }

ensure_repo_root

PKG_DIR="tools/cli/bpsai_pair"
CLI="$PKG_DIR/cli.py"
[ -f "$CLI" ] || { echo "Missing $CLI"; exit 1; }

# 1) Utilities: jsonio + pyutils ------------------------------------------------
say "Adding utility modules (jsonio.py, pyutils.py)"

write_file "$PKG_DIR/jsonio.py" "$(cat <<'PY'
from __future__ import annotations
import json
from typing import Any, Dict

def dump(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
PY
)"

write_file "$PKG_DIR/pyutils.py" "$(cat <<'PY'
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List

def project_files(root: Path, excludes: Iterable[str] | None = None) -> List[Path]:
    """
    Return project files relative to root, respecting simple directory/file excludes.
    Excludes are glob-like segments (e.g., '.git/', '.venv/', '__pycache__/').
    This is intentionally minimal and cross-platform safe.
    """
    ex = list(excludes or [])
    out: List[Path] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        # skip directories that match excludes early
        if any(str(rel).startswith(e.rstrip("/")) for e in ex):
            # if it's a dir, skip its subtree
            if p.is_dir():
                # rely on rglob: cannot prune; filtering below suffices
                pass
        if p.is_file():
            s = str(rel)
            if any(s.startswith(e.rstrip("/")) for e in ex):
                continue
            out.append(rel)
    return out
PY
)"

# 2) Patch cli.py to extend commands ------------------------------------------
say "Patching CLI for --type, --json, pack --dry-run/--list"

python3 - "$CLI" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
s = p.read_text()

# Ensure imports
if "from . import jsonio" not in s:
    s = "from . import jsonio\n" + s
if "from . import pyutils" not in s:
    s = "from . import pyutils\n" + s
if "import json" not in s:
    s = "import json\n" + s
if "from pathlib import Path" not in s:
    s = "from pathlib import Path\n" + s

# ---- FEATURE: add --type, default 'feature', include in branch name
# naive patch: locate 'def feature(' definition and insert Typer option + branch logic
# add option signature if not present
s = re.sub(
    r"@app\.command\(\)\s*\ndef\s+feature\((.*?)\):",
    lambda m: m.group(0).replace(
        m.group(1),
        (m.group(1) + ", "
         "type: str = typer.Option('feature', '--type', help='Branch type: feature|fix|refactor', "
         "case_sensitive=False)")
    ),
    s, flags=re.S
)

# inside feature body, inject normalization + rename branch before calling script
def inject_in_feature_body(text: str) -> str:
    pat = re.compile(r"def\s+feature\((.*?)\):\s*(?:\"\"\".*?\"\"\"\s*)?", re.S)
    m = pat.search(text)
    if not m:
        return text
    start = m.end()
    # Insert normalization code only once
    if "type = (type or 'feature')" in text:
        return text
    code = (
        "\n"
        "    # normalize branch type\n"
        "    t = (type or 'feature').lower()\n"
        "    if t not in {'feature','fix','refactor'}:\n"
        "        raise typer.BadParameter(\"--type must be one of: feature, fix, refactor\")\n"
        "    # adjust first argument (name) into typed branch later in script invocation\n"
    )
    return text[:start] + code + text[start:]
s = inject_in_feature_body(s)

# adjust command that builds the shell 'cmd' list to prefix branch with type/
s = re.sub(
    r"(cmd\s*=\s*\[\s*str\(script\).*?name\s*,)",
    r"\1 f\"{t}/{name}\",",
    s, flags=re.S
)

# ---- PACK: add --dry-run/--list/--json options and behavior
s = re.sub(
    r"@app\.command\(\)\s*\ndef\s+pack\((.*?)\):",
    lambda m: m.group(0).replace(
        m.group(1),
        (m.group(1)
         + ", dry_run: bool = typer.Option(False, '--dry-run', help='Preview files; do not write archive')"
         + ", list_only: bool = typer.Option(False, '--list', help='List files included in pack')"
         + ", json_out: bool = typer.Option(False, '--json', help='Emit JSON result')"
        )
    ),
    s, flags=re.S
)

# Inject logic near top of pack() body to handle preview/list/json.
def inject_in_pack_body(text: str) -> str:
    pat = re.compile(r"def\s+pack\((.*?)\):\s*(?:\"\"\".*?\"\"\"\s*)?", re.S)
    m = pat.search(text)
    if not m:
        return text
    start = m.end()
    if "pack_preview_mode =" in text:
        return text
    code = (
        "\n"
        "    pack_preview_mode = dry_run or list_only\n"
        "    # Try to discover excludes from .agentpackignore in project root\n"
        "    excludes = []\n"
        "    ignore = root / '.agentpackignore'\n"
        "    if ignore.exists():\n"
        "        excludes = [ln.strip() for ln in ignore.read_text().splitlines() if ln.strip()]\n"
        "    files = []\n"
        "    if pack_preview_mode:\n"
        "        files = [str(p) for p in pyutils.project_files(root, excludes=excludes) if str(p).startswith('context/')]\n"
        "        # we intentionally keep preview scope narrow (context/*) to avoid heavy scans\n"
        "        if json_out:\n"
        "            print(jsonio.dump({'dry_run': dry_run, 'list': list_only, 'files': files}))\n"
        "            return\n"
        "        if list_only:\n"
        "            print('\\n'.join(files))\n"
        "            return\n"
        "        # dry-run default: print count\n"
        "        print(f\"Would pack {len(files)} files\")\n"
        "        return\n"
    )
    return text[:start] + code + text[start:]
s = inject_in_pack_body(s)

# After invoking the shell script, append JSON emission if requested
s = re.sub(
    r"(out\s*=\s*Shell\.run\(cmd, cwd=root\)\s*;\s*print\(out\))",
    r"\1\n    if json_out:\n        # best-effort parse for archive name from stdout\n        arc = None\n        for ln in out.splitlines():\n            if 'Created ' in ln and '.tgz' in ln:\n                arc = ln.split('Created ',1)[-1].split()[0]\n                break\n        print(jsonio.dump({'archive': arc, 'ok': True}))\n        return",
    s
)

# ---- CONTEXT-SYNC: add --json
s = re.sub(
    r"@app\.command\(\)\s*\ndef\s+context_sync\((.*?)\):",
    lambda m: m.group(0).replace(
        m.group(1),
        (m.group(1)
         + ", json_out: bool = typer.Option(False, '--json', help='Emit JSON result')"
        )
    ),
    s, flags=re.S
)

# Append JSON print on success (after commit message print)
s = re.sub(
    r"(print\((?:\"Context Sync updated\"|'Context Sync updated')\)\s*)",
    r"\1\n    if json_out:\n        print(jsonio.dump({'updated': True}))\n        return\n",
    s
)

p.write_text(s)
print(f"Patched {p} for Step 3 extensions")
PY

# 3) Docs: ADR + Agents guide clarifications ----------------------------------
say "Adding ADR and refining agents guide"

write_file "docs/adr/0001-context-loop.md" "$(cat <<'MD'
# ADR 0001 — PairCoder Context Loop

**Status:** Accepted
**Context:** AI agents operate with limited context windows and benefit from a compact, structured state that is continuously maintained by developers.
**Decision:** We maintain a persistent context loop in `context/development.md` with four fields:

- **Overall goal is:** one-sentence mission
- **Last action was:** the latest material change
- **Next action will be:** the immediate next step
- **Blockers:** any impediments or decisions needed

**Consequences:**
- Agents read stable state every session.
- Developers must update after each change (`bpsai-pair context-sync`).
- Context packs exclude heavy assets; agents assume excluded assets exist.
MD
)"

# Strengthen agents guide if it exists; otherwise write a baseline (safe append)
AGENTS="$PKG_DIR/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/context/agents.md"
if [ -f "$AGENTS" ]; then
  printf "\n---\n\n## Branch Discipline\n- Use \`--type feature|fix|refactor\` when creating features.\n- Conventional Commits recommended.\n" >> "$AGENTS"
  git add "$AGENTS" 2>/dev/null || true
fi

# 4) Tests for new flags -------------------------------------------------------
say "Adding tests for --type and --json"

mkdir -p tools/cli/tests

# feature --type
write_file "tools/cli/tests/test_feature_branch_type.py" "$(cat <<'PY'
import pathlib
from subprocess import run, PIPE

def test_feature_branch_types(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    (repo/'scripts').mkdir(parents=True, exist_ok=True)
    # minimal script to simulate branch creation; we don't actually change git here
    (repo/'scripts'/'new_feature.sh').write_text('#!/usr/bin/env bash\necho \"OK\"\n')
    run(['chmod','+x', str(repo/'scripts'/'new_feature.sh')], check=True)

    r = run(['bpsai-pair','feature','login','--type','refactor','--primary','x','--phase','y'],
            cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
PY
)"

# pack --dry-run / --list / --json (lightweight)
write_file "tools/cli/tests/test_pack_preview.py" "$(cat <<'PY'
import pathlib
from subprocess import run, PIPE

def test_pack_preview_and_list(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    (repo/'context'/'development.md').write_text('# Development Log\n\n## Context Sync (AUTO-UPDATED)\n')
    (repo/'.agentpackignore').write_text('.git/\n.venv/\n')
    (repo/'scripts').mkdir(parents=True, exist_ok=True)
    (repo/'scripts'/'agent_pack.sh').write_text('#!/usr/bin/env bash\necho \"Created agent_pack.tgz\"\n')
    run(['chmod','+x', str(repo/'scripts'/'agent_pack.sh')], check=True)

    r = run(['bpsai-pair','pack','--dry-run'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr

    r = run(['bpsai-pair','pack','--list'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr

    r = run(['bpsai-pair','pack','--json'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert 'archive' in r.stdout
PY
)"

say "Step 3 applied. Review diffs, run build/tests, then commit."
