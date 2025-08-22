#!/usr/bin/env bash
set -euo pipefail

RED(){ printf "\033[31m%s\033[0m\n" "$*"; }
GRN(){ printf "\033[32m%s\033[0m\n" "$*"; }
YLW(){ printf "\033[33m%s\033[0m\n" "$*"; }
INFO(){ printf "[test] %s\n" "$*"; }
FAIL(){ RED "❌ $*"; exit 1; }
PASS(){ GRN "✅ $*"; }

[ -d .git ] || FAIL "Run from repo root."

# Prefer venv entry point if available
if [ -x ".venv/bin/bpsai-pair" ]; then
  CLI=".venv/bin/bpsai-pair"
  RUN(){ "$CLI" "$@"; }
else
  # Fallback to module exec with PYTHONPATH=.
  RUN(){ PYTHONPATH=. .venv/bin/python -m tools.cli.bpsai_pair "$@"; }
fi

# Warn if tree is dirty (but continue)
if ! git diff --quiet || ! git diff --cached --quiet; then
  YLW "Working tree not clean. Test uses a temp feature branch; it won't touch main."
fi

# 1) Help
INFO "Checking CLI help…"
RUN --help >/dev/null 2>cli_help.err || { cat cli_help.err; rm -f cli_help.err; FAIL "CLI --help failed"; }
rm -f cli_help.err
PASS "CLI help ok"

# 2) Init (non-destructive)
INFO "Running init…"
RUN init tools/cookiecutter-paircoder >/dev/null
[ -f .editorconfig ] || FAIL ".editorconfig missing after init"
[ -f .gitleaks.toml ] || FAIL ".gitleaks.toml missing after init"
[ -f .pre-commit-config.yaml ] || FAIL ".pre-commit-config.yaml missing after init"
[ -f prompts/roadmap.yml ] || FAIL "prompts/roadmap.yml missing after init"
[ -f scripts/new_feature.sh ] || FAIL "scripts/new_feature.sh missing after init"
[ -f context/development.md ] || FAIL "context/development.md missing after init"
PASS "init ok"

# 3) Feature
TS="$(date -u +%Y%m%d%H%M%S)"
SHORT="cli-smoke-${TS}"
BR="feature/${SHORT}"
PRIMARY="Smoke Test Primary Goal ${TS}"
PHASE="Phase 1: Init ${TS}"

git show-ref --verify --quiet refs/heads/main || FAIL "Local branch 'main' not found"
git checkout main >/dev/null 2>&1 || FAIL "Failed to checkout main"
git pull --ff-only || true

INFO "Creating feature branch: ${BR}"
RUN feature "$SHORT" --primary "$PRIMARY" --phase "$PHASE" --force >/dev/null
CURBR="$(git rev-parse --abbrev-ref HEAD)"
[ "$CURBR" = "$BR" ] || FAIL "Expected to be on '$BR', got '$CURBR'"
[ -f context/project_tree.md ] || FAIL "context/project_tree.md missing"
grep -q "^Next action will be:" context/development.md || FAIL "Context Sync not updated"
PASS "feature ok"

# 4) Pack
PKG="agent_pack_${TS}.tgz"
INFO "Packing -> $PKG"
RUN pack "$PKG" >/dev/null
[ -f "$PKG" ] || FAIL "Pack tarball not found: $PKG"
tar -tzf "$PKG" | grep -q "context/development.md" || FAIL "Pack missing context/development.md"
PASS "pack ok"

# 5) Context-sync
INFO "Context sync update…"
RUN context-sync --last "CLI smoke test executed" --nxt "Proceed to Phase 3 planning" --blockers "" >/dev/null
grep -q "Last action was: CLI smoke test executed" context/development.md || FAIL "Context Sync not updated"
PASS "context-sync ok"

# Cleanup
INFO "Cleaning up…"
git checkout main >/dev/null 2>&1 || YLW "Could not checkout main"
git branch -D "$BR" >/dev/null 2>&1 || YLW "Could not delete temp branch $BR"
rm -f "$PKG"

P
