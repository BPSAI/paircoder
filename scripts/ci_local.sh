#!/usr/bin/env bash
set -euo pipefail

# ci_local.sh — opinionated local CI runner across common stacks
# Auto-detects Node.js, Python, and .NET; override with env vars.
# Usage: scripts/ci_local.sh

NODE_FMT_CMD=${NODE_FMT_CMD:-"npm run -s fmt || npx prettier -w ."}
NODE_LINT_CMD=${NODE_LINT_CMD:-"npm run -s lint || npx eslint ."}
NODE_TEST_CMD=${NODE_TEST_CMD:-"npm test --silent || npm run -s test"}
NODE_TYPE_CMD=${NODE_TYPE_CMD:-"npm run -s typecheck || npx tsc -p . --noEmit"}
NODE_AUDIT_CMD=${NODE_AUDIT_CMD:-"npm audit --audit-level=high || true"}

PY_FMT_CMD=${PY_FMT_CMD:-"ruff format . && ruff check ."}
PY_TEST_CMD=${PY_TEST_CMD:-"pytest -q"}
PY_TYPE_CMD=${PY_TYPE_CMD:-"pyright || mypy ."}
PY_AUDIT_CMD=${PY_AUDIT_CMD:-"pip-audit -r requirements.txt || true"}

DOTNET_FMT_CMD=${DOTNET_FMT_CMD:-"dotnet format"}
DOTNET_TEST_CMD=${DOTNET_TEST_CMD:-"dotnet test --nologo"}
DOTNET_AUDIT_CMD=${DOTNET_AUDIT_CMD:-": # no-op (consider dotnet list package --vulnerable)"}

info() { echo "[ci] $*"; }
section() { echo; echo "==== $* ===="; }

has() { command -v "$1" >/dev/null 2>&1; }
exists() { [ -e "$1" ]; }

run_node() {
  if exists package.json; then
    section "Node.js: format/lint/type/test/audit"
    has npm || { info "npm missing, skipping"; return; }
    $NODE_FMT_CMD
    $NODE_LINT_CMD
    if exists tsconfig.json; then
      $NODE_TYPE_CMD
    fi
    $NODE_TEST_CMD
    $NODE_AUDIT_CMD
  fi
}

run_python() {
  if exists pyproject.toml || exists requirements.txt; then
    section "Python: format/lint/type/test/audit"
    if has python -o has python3; then :; else info "python missing, skipping"; return; fi
    # Ensure tools if available
    $PY_FMT_CMD || true
    $PY_TYPE_CMD || true
    $PY_TEST_CMD
    if exists requirements.txt; then
      $PY_AUDIT_CMD || true
    fi
  fi
}

run_dotnet() {
  if ls *.sln *.csproj >/dev/null 2>&1; then
    section ".NET: format/test"
    has dotnet || { info "dotnet missing, skipping"; return; }
    $DOTNET_FMT_CMD || true
    $DOTNET_TEST_CMD
    eval "$DOTNET_AUDIT_CMD"
  fi
}

main() {
  section "Local CI started"
  run_node
  run_python
  run_dotnet
  section "Local CI completed"
}

main "$@"
