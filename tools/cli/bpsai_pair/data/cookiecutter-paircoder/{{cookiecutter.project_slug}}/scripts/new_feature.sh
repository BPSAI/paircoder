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
