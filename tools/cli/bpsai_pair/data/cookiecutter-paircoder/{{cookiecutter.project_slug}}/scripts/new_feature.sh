#!/usr/bin/env bash
set -euo pipefail

# new_feature.sh — scaffold a feature branch + context updates
# Usage:
#   scripts/new_feature.sh <feature-name> [--primary "<PRIMARY GOAL>"] [--phase "<PHASE 1 GOAL>"] [--force]
# Example:
#   scripts/new_feature.sh auth-di --primary "Decouple auth via DI" --phase "Refactor auth module for DI + tests"

PRIMARY=""
PHASE=""
FORCE=false

err() { echo "[new_feature] ERROR: $*" >&2; exit 1; }
info() { echo "[new_feature] $*"; }

require_git_clean() {
  if ! $FORCE; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
      err "Working tree not clean. Commit or stash changes, or pass --force."
    fi
  fi
}

ensure_repo_root() {
  [ -d .git ] || err "Run from repo root (where .git exists)."
}

project_tree() {
  if command -v tree >/dev/null 2>&1; then
    tree -a -I "node_modules|.git|.venv|dist|build|.mypy_cache|__pycache__|.pytest_cache|.DS_Store" .
  else
    # Fallback using find
    find . -path ./.git -prune -o -path ./node_modules -prune -o -path ./dist -prune -o -path ./build -prune -o -print | sed 's/^\.\///'
  fi
}

FEATURE="${1:-}" || true
shift || true || true

while [ $# -gt 0 ]; do
  case "$1" in
    --primary)
      shift; PRIMARY="${1:-}" || true ;;
    --phase)
      shift; PHASE="${1:-}" || true ;;
    --force)
      FORCE=true ;;
    *) err "Unknown arg: $1" ;;
  esac
  shift || true
done

[ -n "$FEATURE" ] || err "Missing <feature-name>."

ensure_repo_root
require_git_clean

git fetch --all --prune

# Ensure main exists locally
if ! git rev-parse --verify main >/dev/null 2>&1; then
  err "Branch 'main' not found locally."
fi

# Create branch
BRANCH="feature/${FEATURE}"
info "Creating branch: ${BRANCH} from main"

git checkout main
git pull --ff-only

git checkout -b "$BRANCH"

# Context scaffolding
mkdir -p context/directory_notes

# Ensure development.md stub exists
if [ ! -f context/development.md ]; then
  info "Creating context/development.md"
  cat > context/development.md <<'EOF'
# Development Roadmap — <PROJECT NAME>

**Primary Goal:** <PRIMARY GOAL>
**Owner:** <Tech Lead / DRI>
**Last Updated:** <YYYY-MM-DD>

## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: (init)
Next action will be: (init)
Blockers/Risks: (none)
EOF
fi

# Update PRIMARY GOAL if provided
if [ -n "$PRIMARY" ]; then
  info "Stamping PRIMARY GOAL into context/development.md"
  # Replace first occurrence of placeholder line
  perl -0777 -pe "s/\*\*Primary Goal:\*\*.*\n/**Primary Goal:** ${PRIMARY}\n/ if $.==0" -i context/development.md || true
  # Also update Overall goal line in Context Sync
  perl -0777 -pe "s/Overall goal is:.*\n/Overall goal is: ${PRIMARY}\n/" -i context/development.md || true
fi

# Ensure agents.md exists (created manually earlier)
if [ ! -f context/agents.md ]; then
  info "Creating minimal context/agents.md stub (fill with full playbook)."
  cat > context/agents.md <<'EOF'
# Agents Guide — AI Pair Coding Playbook (stub)
Refer to the canonical version and paste it here.
EOF
fi

# Generate project tree snapshot
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p context
info "Refreshing context/project_tree.md"
{
  echo "# Project Tree (snapshot)"
  echo "_Generated: ${TS}_"
  echo
  echo '```'
  project_tree
  echo '```'
} > context/project_tree.md

# Append/update Context Sync block
if ! grep -q "^## Context Sync" context/development.md; then
  cat >> context/development.md <<'EOF'

## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: initialized feature branch and context
Next action will be: <first task>
Blockers/Risks: <if any>
EOF
else
  perl -0777 -pe "s/Last action was:.*\n/Last action was: initialized feature branch and context\n/" -i context/development.md || true
  if [ -n "$PHASE" ]; then
    perl -0777 -pe "s/Next action will be:.*\n/Next action will be: ${PHASE}\n/" -i context/development.md || true
  fi
fi

# Commit
info "Creating initial commit for ${BRANCH}"

git add context || true

git commit -m "chore(context): scaffold ${BRANCH} and refresh project_tree.md"

info "Done. Next: connect your agent to the repo and attach files in /context."
