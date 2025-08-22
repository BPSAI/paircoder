#!/usr/bin/env bash
set -euo pipefail

# PairCoder Step1+Step2 Patch Applier
# Run from repo root: bash scripts/apply_step1_step2.sh
# This will:
#  - Update CLI UX (init default; context-sync --next alias)
#  - Add friendly missing-script errors
#  - Harden template files + ignores + starter agents.md
#  - Add CI smoke workflow and minimal pytest
#  - Add release.sh helper
#
# Idempotent: safe to re-run. Creates .bak copies before overwriting.

say(){ printf "[patch] %s\n" "$*"; }

ensure_repo_root(){
  if [ ! -d .git ]; then
    echo "Run this script from the repository root (where .git exists)."; exit 1
  fi
}

backup_file(){
  local f="$1"
  if [ -f "$f" ]; then cp -n "$f" "$f.bak" || true; fi
}

write_file(){
  local path="$1"; shift
  local content="$*"
  backup_file "$path"
  mkdir -p "$(dirname "$path")"
  printf "%s" "$content" > "$path"
  git add "$path" 2>/dev/null || true
}

append_unique_line(){
  local file="$1"; local line="$2"
  touch "$file"
  if ! grep -qxF "$line" "$file" 2>/dev/null; then echo "$line" >> "$file"; fi
  git add "$file" 2>/dev/null || true
}

ensure_repo_root

PKG_DIR="tools/cli"
PKG_PY="$PKG_DIR/bpsai_pair"
CLI_PY="$PKG_PY/cli.py"
BUNDLE_DIR="$PKG_PY/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}"

# 0) Guards
[ -d "$PKG_DIR" ] || { echo "Missing $PKG_DIR"; exit 1; }
[ -d "$PKG_PY" ] || { echo "Missing $PKG_PY"; exit 1; }
[ -f "$CLI_PY" ] || { echo "Missing $CLI_PY"; exit 1; }

# 1) CLI updates --------------------------------------------------------------

# 1a) context-sync: add --next alias and auto-create development.md if missing
python3 - "$CLI_PY" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
s = p.read_text()

# Ensure we import typer and Path (should already be present)
if "import typer" not in s:
    s = "import typer\nfrom pathlib import Path\n" + s

# Add '--next' alias to the --nxt option (keep --nxt for back-compat)
s = re.sub(r"--nxt[\"']\),\s*help=", "--nxt','--next'), help=", s)

# For context-sync: if development.md missing, create minimal skeleton instead of raising
s = re.sub(
    r"if not dev\.exists\(\):\s*raise typer\.BadParameter\([^\)]*\)\s*",
    (
        "if not dev.exists():\n"
        "        dev.parent.mkdir(parents=True, exist_ok=True)\n"
        "        dev.write_text('# Development Log\\n\\n**Phase:** (init)\\n**Primary Goal:** (init)\\n\\n## Context Sync (AUTO-UPDATED)\\n\\n- **Overall goal is:**\\n- **Last action was:**\\n- **Next action will be:**\\n- **Blockers:**\\n')\n"
    ),
    s,
    flags=re.S,
)

p.write_text(s)
print(f"Patched {p} (context-sync alias + auto-create dev)")
PY

# 1b) init command default to bundled template when no argument supplied
python3 - "$CLI_PY" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
s = p.read_text()

# Ensure we can call into the bundled init helper
if "from . import init_bundled_cli" not in s:
    s = "from . import init_bundled_cli\n" + s

# Change the init signature to accept optional template arg with default None
s = re.sub(
    r"def\s+init\((.*?)\):",
    "def init(template: str = typer.Argument(None, help='Path to template (optional, defaults to bundled template)')):",
    s,
    flags=re.S,
)

# Make template_path optional and fallback to bundled main when None
s = re.sub(r"template_path\s*=\s*Path\(template\)", "template_path = Path(template) if template else None", s)
s = re.sub(
    r"if not template_path\.exists\(\):\s*raise[\s\S]*?\n",
    (
        "if template_path is None:\n"
        "        return init_bundled_cli.main()\n"
        "    if not template_path.exists():\n"
        "        raise typer.BadParameter(f'Template not found: {template}')\n"
    ),
    s,
)

p.write_text(s)
print(f"Patched {p} (init default to bundled)")
PY

# 1c) Friendly errors when required scripts are missing for feature/pack
python3 - "$CLI_PY" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()

def inject_guard(src: str, fn_name: str, script_name: str) -> str:
    # Insert just after function signature
    pat = re.compile(rf"def\s+{fn_name}\\(.*?\\):")
    m = pat.search(src)
    if not m:
        return src
    insert_at = m.end()
    guard = (
        f"\n    script = root / 'scripts' / '{script_name}'\n"
        f"    if not script.exists():\n"
        f"        raise typer.BadParameter(\"Scaffolding not found. Run 'bpsai-pair-init' (or 'bpsai-pair init') first.\")\n"
    )
    return src[:insert_at] + guard + src[insert_at:]

s = inject_guard(s, "feature", "new_feature.sh")
s = inject_guard(s, "pack", "agent_pack.sh")

p.write_text(s)
print(f"Patched {p} (guards for missing scripts)")
PY

say "CLI hardening complete"

# 2) Template hygiene ---------------------------------------------------------
DEV_TPL="# Development Log\n\n**Phase:** (set by first feature)\n**Primary Goal:** (set by first feature)\n\n## Context Sync (AUTO-UPDATED)\n\n- **Overall goal is:** (set by feature)\n- **Last action was:** (set by feature)\n- **Next action will be:** (set by feature)\n- **Blockers:** (set by feature)\n"
write_file "$BUNDLE_DIR/context/development.md" "$DEV_TPL"

AGENTS_TPL="# Agents Guide\n\nThis project uses a **Context Loop**. Always keep these fields current:\n\n- **Overall goal is:** Single-sentence mission\n- **Last action was:** What just completed\n- **Next action will be:** The very next step\n- **Blockers:** Known issues or decisions needed\n\n### Working Rules for Agents\n- Do not modify or examine ignored directories (see \`.agentpackignore\`). Assume large assets exist even if excluded.\n- Prefer minimal, reversible changes.\n- After committing code, run \`bpsai-pair context-sync\` to update the loop.\n- Request a new context pack when the tree or docs change significantly.\n\n### Context Pack\nRun \`bpsai-pair pack --out agent_pack.tgz\` and upload to your session.\n"
write_file "$BUNDLE_DIR/context/agents.md" "$AGENTS_TPL"

append_unique_line "$BUNDLE_DIR/.gitignore" ".venv/"
append_unique_line "$BUNDLE_DIR/.gitignore" "__pycache__/"
append_unique_line "$BUNDLE_DIR/.gitignore" "*.pyc"
append_unique_line "$BUNDLE_DIR/.gitignore" "agent_pack.tgz"

AGENT_IGNORE_CONTENT="# Default agent pack exclusions\n.git/\n.venv/\n__pycache__/\nnode_modules/\ndist/\nbuild/\n*.log\n*.bak\n*.tgz\n*.tar.gz\n*.zip\n"
write_file "$BUNDLE_DIR/.agentpackignore" "$AGENT_IGNORE_CONTENT"

say "Template hygiene complete"

# 3) CI smoke workflow --------------------------------------------------------
SMOKE_YML="""name: cli-smoke
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  smoke:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ '3.10', '3.11', '3.12' ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Build wheel
        run: |
          python -m pip install --upgrade pip build
          python -m build tools/cli
      - name: Install wheel
        run: |
          python -m pip install tools/cli/dist/*.whl
      - name: Run smoke in temp repo
        run: |
          set -euo pipefail
          tmp=$(mktemp -d)
          cd "$tmp"
          git init .
          echo "# Smoke" > README.md
          git add . && git commit -m "init"
          python -m venv v && . v/bin/activate
          python -m pip install --upgrade pip
          pip install $GITHUB_WORKSPACE/tools/cli/dist/*.whl
          bpsai-pair-init
          git add -A && git commit -m "adopt scaffolding"
          bpsai-pair feature demo --primary "Goal" --phase "Phase 1"
          bpsai-pair pack --out agent_pack.tgz
          bpsai-pair context-sync --last "Did A" --next "Do B" --blockers ""
"""
write_file ".github/workflows/cli-smoke.yml" "$SMOKE_YML"

say "CI smoke workflow added"

# 4) Minimal pytest for context-sync logic -----------------------------------
TEST_INIT="""import pathlib
from subprocess import run, PIPE

def test_context_sync_updates(tmp_path: pathlib.Path):
    repo = tmp_path
    run(['git','init','.'], cwd=repo, check=True)
    (repo/'context').mkdir(parents=True, exist_ok=True)
    dev = repo/'context'/'development.md'
    dev.write_text('# Development Log\n\n**Phase:** X\n**Primary Goal:** Y\n\n## Context Sync (AUTO-UPDATED)\n\n- **Overall goal is:**\n- **Last action was:**\n- **Next action will be:**\n- **Blockers:**\n')
    run(['git','add','-A'], cwd=repo, check=True)
    run(['git','commit','-m','init'], cwd=repo, check=True)
    r = run(['bpsai-pair','context-sync','--last','A','--next','B','--blockers','C'], cwd=repo, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
    t = dev.read_text()
    assert "Last action was: A" in t
    assert "Next action will be: B" in t
    assert "Blockers: C" in t
"""
write_file "tools/cli/tests/test_context_sync.py" "$TEST_INIT"

say "Minimal pytest added"

# 5) Release helper script ----------------------------------------------------
RELEASE_SH="""#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "Usage: scripts/release.sh --version X.Y.Z [--repo testpypi|pypi]"; }
VER=""; REPO="pypi"
while (( "$#" )); do
  case "$1" in
    --version) VER="$2"; shift 2;;
    --repo) REPO="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg $1"; usage; exit 1;;
  esac
done
[ -n "$VER" ] || { usage; exit 1; }

sed -i "s/^version = \".*\"/version = \"$VER\"/" tools/cli/pyproject.toml
python -m pip install --upgrade pip build twine
rm -rf tools/cli/dist
python -m build tools/cli
twine check tools/cli/dist/*
if [ "$REPO" = "testpypi" ]; then
  [ -n "${TWINE_USERNAME:-}" ] && [ -n "${TWINE_PASSWORD:-}" ] || { echo "Set TWINE creds"; exit 1; }
  export TWINE_REPOSITORY_URL="https://test.pypi.org/legacy/"
fi
twine upload tools/cli/dist/*
(git checkout -b "release/v$VER" || git checkout "release/v$VER") || true
git add -A && git commit -m "chore(release): $VER" || true
git tag -a "v$VER" -m "PairCoder CLI $VER" || true
echo "Push: git push origin release/v$VER --tags"
"""
write_file "scripts/release.sh" "$RELEASE_SH"
chmod +x scripts/release.sh

say "Release helper added"

say "All Step1+Step2 changes applied. Review diffs, then commit."
