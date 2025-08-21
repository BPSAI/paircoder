#!/usr/bin/env bash
set -euo pipefail

REL="release/v0.1.2"
NEWVER="0.1.2"
PKG_DIR="tools/cli"
PKG_NAME="bpsai_pair"
BUNDLE_ROOT="$PKG_DIR/$PKG_NAME/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}"

say(){ printf "[v0.1.2] %s\n" "$*"; }

# 0) ensure git root
[ -d .git ] || { echo "Run from repo root"; exit 1; }

# 1) branch
if git rev-parse --verify --quiet "$REL" >/dev/null; then
  git checkout "$REL"
else
  git checkout -b "$REL"
fi

# 2) paths sanity
[ -d "$BUNDLE_ROOT" ] || { echo "Bundled template not found at $BUNDLE_ROOT"; exit 1; }

# 3) Harden the bundled template

# 3a) Robust new_feature.sh (no-remote friendly, stamps Primary Goal/Phase, no .bak)
mkdir -p "$BUNDLE_ROOT/scripts"
cat > "$BUNDLE_ROOT/scripts/new_feature.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
[new_feature] Usage:
  scripts/new_feature.sh <name> --primary "<Primary Goal>" --phase "<Phase Label>" [--force]

Notes:
  - Creates/switches to branch: feature/<name>
  - Updates context/development.md (Primary Goal, Phase, Context Sync)
  - Skips 'git pull' if no upstream is set (works offline)
USAGE
}

NAME=""; PRIMARY=""; PHASE=""; FORCE=0
while (( "$#" )); do
  case "$1" in
    --primary) PRIMARY="$2"; shift 2;;
    --phase)   PHASE="$2";   shift 2;;
    --force)   FORCE=1;      shift 1;;
    -h|--help) usage; exit 0;;
    *) if [[ -z "$NAME" ]]; then NAME="$1"; shift; else echo "Unknown arg: $1"; usage; exit 2; fi;;
  esac
done

[[ -n "$NAME" && -n "$PRIMARY" && -n "$PHASE" ]] || { echo "[new_feature] ERROR: missing required args"; usage; exit 2; }

if [[ $FORCE -ne 1 ]]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "[new_feature] ERROR: Working tree not clean. Commit or stash changes, or pass --force."
    exit 1
  fi
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
cd "$ROOT"

# Checkout main if present
if git show-ref --verify --quiet refs/heads/main; then
  echo "[new_feature] Checking out main"
  git checkout -q main
  # Pull only if upstream exists
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    echo "[new_feature] Pulling upstream"
    git pull --ff-only || true
  else
    echo "[new_feature] No upstream; skipping pull (local/offline)."
  fi
else
  echo "[new_feature] No local 'main'; using current HEAD."
fi

BR="feature/${NAME}"
echo "[new_feature] Creating/switching to: ${BR}"
if git show-ref --verify --quiet "refs/heads/${BR}"; then
  git checkout -q "${BR}"
else
  git checkout -q -b "${BR}"
fi

mkdir -p context context/directory_notes
DEV="context/development.md"
AGENTS="context/agents.md"
TREE="context/project_tree.md"
touch "$DEV" "$AGENTS" "$TREE"

# Replace cookiecutter token if present, else ensure Primary Goal/Phase headings exist
tmp="$(mktemp)"
if grep -q '{{cookiecutter.primary_goal}}' "$DEV"; then
  sed "s/{{cookiecutter.primary_goal}}/${PRIMARY//\//\\/}/g" "$DEV" > "$tmp" && mv "$tmp" "$DEV"
fi

# Ensure Phase line
if grep -q '^\*\*Phase:\*\*' "$DEV"; then
  perl -0777 -i -pe 's/^\*\*Phase:\*\*.*$/**Phase:** '"${PHASE//\//\\/}"'/m' "$DEV" || true
else
  awk -v PHASE="$PHASE" 'NR==1{print; print ""; print "**Phase:** " PHASE; print ""; next} {print}' "$DEV" > "$tmp" && mv "$tmp" "$DEV"
fi

# Ensure Primary Goal line
if grep -q '^\*\*Primary Goal:\*\*' "$DEV"; then
  perl -0777 -i -pe 's/^\*\*Primary Goal:\*\*.*$/**Primary Goal:** '"${PRIMARY//\//\\/}"'/m' "$DEV" || true
else
  awk -v PG="$PRIMARY" 'NR==1{print; print ""; print "**Primary Goal:** " PG; print ""; next} {print}' "$DEV" > "$tmp" && mv "$tmp" "$DEV"
fi

# Ensure Context Sync section scaffold
if ! grep -q '^## Context Sync' "$DEV"; then
  cat >> "$DEV" <<'EOCS'

## Context Sync (AUTO-UPDATED)

- **Overall goal is:** _(set by feature flow)_
- **Last action was:** _(set by feature flow)_
- **Next action will be:** _(set by feature flow)_
EOCS
fi

git add "$DEV"
git commit -m "feat(context): start ${BR} — Primary Goal: ${PRIMARY} | Phase: ${PHASE}" >/dev/null || true

echo "[new_feature] Branch ready: ${BR}"
echo "[new_feature] Updated ${DEV} with Primary Goal + Phase + Context Sync."
SH
chmod +x "$BUNDLE_ROOT/scripts/new_feature.sh"
say "Updated bundled scripts/new_feature.sh"

# 3b) Improve template ignores
# .gitignore
IGN="$BUNDLE_ROOT/.gitignore"
mkdir -p "$(dirname "$IGN")"
grep -qxF ".venv/" "$IGN" 2>/dev/null || echo ".venv/" >> "$IGN"
grep -qxF "__pycache__/" "$IGN" 2>/dev/null || echo "__pycache__/" >> "$IGN"
grep -qxF "*.pyc" "$IGN" 2>/dev/null || echo "*.pyc" >> "$IGN"
grep -qxF "agent_pack.tgz" "$IGN" 2>/dev/null || echo "agent_pack.tgz" >> "$IGN"
say "Hardened template .gitignore"

# .agentpackignore
API="$BUNDLE_ROOT/.agentpackignore"
cat > "$API" <<'EOPI'
# exclude noisy/large or irrelevant content from agent packs
.git/
.venv/
__pycache__/
node_modules/
dist/
build/
*.log
*.tmp
*.bak
*.tgz
*.tar.gz
*.zip
# add project-specific excludes below
EOPI
say "Refreshed template .agentpackignore"

# 3c) Ensure initial context/development.md does NOT carry raw cookiecutter placeholders
mkdir -p "$BUNDLE_ROOT/context"
cat > "$BUNDLE_ROOT/context/development.md" <<'EOD'
# Development Log

**Phase:** (set by first feature)
**Primary Goal:** (set by first feature)

## Context Sync (AUTO-UPDATED)

- **Overall goal is:** (set by feature)
- **Last action was:** (set by feature)
- **Next action will be:** (set by feature)
EOD
say "Template context/development.md initialized without cookiecutter tokens"

# 4) Bump version in pyproject.toml
PYP="$PKG_DIR/pyproject.toml"
[ -f "$PYP" ] || { echo "Missing $PYP"; exit 1; }
# replace version = "x.y.z"
perl -0777 -i -pe 's/^version\s*=\s*"\d+\.\d+\.\d+"\s*$/version = "'"$NEWVER"'"/m' "$PYP" \
  || sed -i 's/^version *= *".*"/version = "'"$NEWVER"'"/' "$PYP"
say "Bumped version to $NEWVER"

# 5) Build fresh
rm -rf .venv
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel build twine >/dev/null
pushd "$PKG_DIR" >/dev/null
python -m build
popd >/dev/null
twine check "$PKG_DIR"/dist/*

# 6) Commit/tag
git add -A
git commit -m "release: v$NEWVER — hardened new_feature, cleaned template, better ignores"
git tag "v$NEWVER"

say "Ready. To push: git push origin HEAD:$REL --tags"

# 7) Optional upload to TestPyPI if creds present
if [ -n "${TWINE_USERNAME:-}" ] && [ -n "${TWINE_PASSWORD:-}" ] && [ -n "${TWINE_REPOSITORY_URL:-}" ]; then
  say "Uploading to ${TWINE_REPOSITORY_URL}"
  twine upload "$PKG_DIR"/dist/*
else
  say "Skipping upload (set TWINE_* for TestPyPI)."
fi
