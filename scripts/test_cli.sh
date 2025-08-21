#!/usr/bin/env bash
set -euo pipefail

# test_cli.sh — validates Phase 2 CLI end-to-end without touching main
# What it tests:
#   - CLI entrypoint & commands present
#   - init copies scaffolding (no clobber)
#   - feature creates a branch and commits context
#   - pack creates a tarball with expected files
#   - context-sync updates context loop
#
# It cleans up by deleting the test branch and temp files.
# Re-run safe: generates unique branch and pack names on each run.

RED() { printf "\033[31m%s\033[0m\n" "$*"; }
GRN() { printf "\033[32m%s\033[0m\n" "$*"; }
YLW() { printf "\033[33m%s\033[0m\n" "$*"; }
INFO() { printf "[test] %s\n" "$*"; }
FAIL() { RED "❌ $*"; exit 1; }
PASS() { GRN "✅ $*"; }

ensure_repo_root() {
  [ -d .git ] || FAIL "Run from repo root (where .git exists)."
}

check_cmd() {
  command -v "$1" >/dev/null 2>&1 || FAIL "Command '$1' not found"
}

git_clean_or_warn() {
  if ! git diff --quiet || ! git diff --cached --quiet; then
    YLW "Working tree not clean. This test creates/deletes a temp feature branch but won't touch main."
  fi
}

ensure_repo_root
check_cmd git
check_cmd python

# Use CLI either as installed script or module
if command -v bpsai-pair >/dev/null 2>&1; then
  CLI="bpsai-pair"
else
  CLI="python -m tools.cli.bpsai_pair"
fi

git_clean_or_warn

# Vars
TS="$(date -u +%Y%m%d%H%M%S)"
BR="feature/cli-smoke-${TS}"
PKG="agent_pack_${TS}.tgz"
PRIMARY="Smoke Test Primary Goal ${TS}"
PHASE="Phase 1: Init ${TS}"

# 1) Help
INFO "Checking CLI help…"
$CLI --help >/dev/null 2>&1 || FAIL "CLI --help failed"
PASS "CLI help ok"

# 2) Init (non-destructive copy)
INFO "Running init…"
$CLI init tools/cookiecutter-paircoder >/dev/null 2>&1 || FAIL "init failed"
# Spot-check files now exist (or already existed)
[ -f .editorconfig ] || FAIL ".editorconfig missing after init"
[ -f .gitleaks.toml ] || FAIL ".gitleaks.toml missing after init"
[ -f .pre-commit-config.yaml ] || FAIL ".pre-commit-config.yaml missing after init"
[ -f prompts/roadmap.yml ] || FAIL "prompts/roadmap.yml missing after init"
[ -f scripts/new_feature.sh ] || FAIL "scripts/new_feature.sh missing after init"
[ -f context/development.md ] || FAIL "context/development.md missing after init"
PASS "init ok"

# 3) Feature branch create
INFO "Creating feature branch: ${BR}"
# Ensure main exists locally
git show-ref --verify --quiet refs/heads/main || FAIL "Local branch 'main' not found"
git checkout main >/dev/null 2>&1 || FAIL "Failed to checkout main"
git pull --ff-only || true

$CLI feature "cli-smoke-${TS}" --primary "$PRIMARY" --phase "$PHASE" --force >/dev/null 2>&1 || FAIL "feature command failed"
# Verify branch exists and is current
CURBR="$(git rev-parse --abbrev-ref HEAD)"
[ "$CURBR" = "$BR" ] || FAIL "Expected current branch '$BR', got '$CURBR'"
# Verify context updated & committed
[ -f context/project_tree.md ] || FAIL "context/project_tree.md missing"
git log -1 --pretty=%B | grep -qi "scaffold" || YLW "Last commit message didn't contain 'scaffold' (ok if different template)"

# Check Context Sync updated with 'Next action will be'
grep -q "^Next action will be:" context/development.md || FAIL "Context Sync not found/updated in development.md"
PASS "feature ok"

# 4) Pack
INFO "Packing agent context -> $PKG"
$CLI pack "$PKG" >/dev/null 2>&1 || FAIL "pack failed"
[ -f "$PKG" ] || FAIL "Pack tarball not found: $PKG"
# Quick contents check
tar -tzf "$PKG" | grep -q "context/development.md" || FAIL "Packed tar missing context/development.md"
tar -tzf "$PKG" | grep -q "context/agents.md" || YLW "agents.md not found in pack (ok if not yet added)"
PASS "pack ok"

# 5) Context sync programmatic update
INFO "Updating Context Sync…"
$CLI context-sync --last "CLI smoke test executed" --nxt "Proceed to Phase 3 planning" --blockers "" >/dev/null 2>&1 || FAIL "context-sync failed"
grep -q "Last action was: CLI smoke test executed" context/development.md || FAIL "Context Sync not updated as expected"
PASS "context-sync ok"

# Cleanup: switch back to main and delete test branch
INFO "Cleaning up test branch…"
git checkout main >/dev/null 2>&1 || YLW "Could not checkout main (please do so manually)"
git branch -D "$BR" >/dev/null 2>&1 || YLW "Could not delete temp branch $BR (delete manually if needed)"
rm -f "$PKG"

PASS "All CLI smoke tests passed."
