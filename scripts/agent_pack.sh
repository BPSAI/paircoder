#!/usr/bin/env bash
set -euo pipefail

# agent_pack.sh — bundle approved context for agent upload
# Usage:
#   scripts/agent_pack.sh [output.tgz] [--extra path1 path2 ...]
#   scripts/agent_pack.sh agent_pack.tgz --extra README.md docs/ADR-001.md

OUT="agent_pack.tgz"
EXTRA=()

err() { echo "[agent_pack] ERROR: $*" >&2; exit 1; }
info() { echo "[agent_pack] $*"; }

ensure_repo_root() { [ -d .git ] || err "Run from repo root."; }

# Parse args
if [ $# -gt 0 ]; then
  if [[ "$1" != "--extra" ]]; then
    OUT="$1"; shift || true
  fi
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --extra)
      shift || true
      while [ $# -gt 0 ] && [[ "$1" != --* ]]; do
        EXTRA+=("$1"); shift || true
      done
      ;;
    *) err "Unknown arg: $1" ;;
  esac
done

ensure_repo_root

# Default include set
INCLUDE=(
  context/development.md
  context/agents.md
  context/project_tree.md
)

# Include directory_notes if present
if [ -d context/directory_notes ]; then
  INCLUDE+=(context/directory_notes)
fi

# Add extras
if [ ${#EXTRA[@]} -gt 0 ]; then
  INCLUDE+=("${EXTRA[@]}")
fi

# Validate
for p in "${INCLUDE[@]}"; do
  [ -e "$p" ] || err "Missing path: $p"
done

# Exclusion patterns (optional via .agentpackignore)
EXCL_FILE=.agentpackignore
if [ -f "$EXCL_FILE" ]; then
  info "Using excludes from $EXCL_FILE"
  TAR_EXCLUDE=(--exclude-from "$EXCL_FILE")
else
  TAR_EXCLUDE=(
    --exclude "**/.git*" \
    --exclude "**/node_modules" \
    --exclude "**/dist" \
    --exclude "**/build" \
    --exclude "**/.venv" \
    --exclude "**/__pycache__" \
    --exclude "**/.mypy_cache" \
    --exclude "**/.pytest_cache"
  )
fi

# Pack
info "Packing -> $OUT"

tar -czf "$OUT" "${TAR_EXCLUDE[@]}" "${INCLUDE[@]}"

info "Created $OUT ($(du -h "$OUT" | cut -f1))"
info "Upload this archive to your agent session."
