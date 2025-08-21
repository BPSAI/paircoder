# PairCoder — AI‑Augmented Pair Programming Framework

PairCoder gives teams a **drop‑in, repo‑native toolkit** for pairing with AI coding agents (GPT‑5, Claude, etc.). It standardizes governance, persists project memory in `/context`, and ships a small CLI to orchestrate the workflow (init → roadmap → feature branches → context loop).

> **Scope:** This repo is the **core package/CLI** (Phases 0–2). Any optional UI or external integrations (e.g., Trello Codex) should live in separate repos and *consume* this core.

---

## ✨ What you get

* **Context as Memory** — canonical state in `/context/*.md` (roadmap, agents guide, project tree).
* **Disciplined Loop** — agents update `Overall/Last/Next/Blockers` on every action.
* **Governance** — CONTRIBUTING, PR template, CODEOWNERS, SECURITY.
* **Quality Gates** — pre‑commit (ruff/prettier/markdownlint), secret scanning (gitleaks), CI workflows.
* **CLI (`bpsai-pair`)** — `init`, `feature`, `pack`, `context-sync`.
* **Cookiecutter** — `/tools/cookiecutter-paircoder` to bootstrap new repos.

---

## Requirements

* Git, Python 3.9+
* (Recommended) local virtualenv
* Optional: Node (if your repo includes JS/TS), Docker (for future integration tests)
* `gitleaks` binary for local secret scans (install via your package manager)

---

## Install (local venv recommended)

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
# Editable install of the CLI
python -m pip install -e tools/cli
```

> On Debian/Ubuntu with PEP 668 (externally managed), a venv avoids system‑pip errors.

---

## Quickstart

### 1) Initialize scaffolding (non‑destructive)

Copies governance, prompts, context files into the repo **only if missing**.

```bash
bpsai-pair init tools/cookiecutter-paircoder
```

### 2) Create a feature branch and scaffold context

```bash
bpsai-pair feature login-system \
  --primary "Implement login with DI seam" \
  --phase   "Phase 1: Scaffolding & tests"
```

This creates `feature/login-system`, refreshes `context/project_tree.md`, and updates the Context Sync block in `context/development.md`.

### 3) Package context for an agent

```bash
bpsai-pair pack agent_pack.tgz
```

### 4) Update the Context Sync block programmatically

```bash
bpsai-pair context-sync \
  --last "Generated roadmap" \
  --nxt  "Kick off Phase 1" \
  --blockers ""
```

> **Fallback (no entry point yet):** `PYTHONPATH=. .venv/bin/python -m tools.cli.bpsai_pair --help`

---

## Repository layout

```
context/          # Development roadmap, agents guide, project tree snapshot
prompts/          # Prompt assets (roadmap, deep_research, implementation)
scripts/          # Shell helpers (new_feature.sh, agent_pack.sh, etc.)
tools/cli/        # Typer-based CLI (bpsai-pair)
tools/cookiecutter-paircoder/   # Cookiecutter template for new repos
.github/workflows/              # CI & project_tree refresh
```

---

## The Context Loop (required discipline)

Append or update this block in `context/development.md` after each meaningful action (humans **and** agents):

```
## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: <what changed and why>
Next action will be: <smallest valuable step with owner>
Blockers/Risks: <if any>
```

The CLI’s `context-sync` command keeps this current.

---

## Pre‑commit & gitleaks

Install once and enable hooks:

```bash
pip install pre-commit
pre-commit install
```

Run secret scan locally (non‑blocking in pre‑commit config):

```bash
gitleaks detect --no-banner --redact --config .gitleaks.toml
```

---

## CI workflows

* **CI:** `.github/workflows/ci.yml` runs format/lint/type/tests for Node & Python projects.
* **Project tree refresh:** `.github/workflows/project_tree.yml` (daily) updates `context/project_tree.md` and commits if changed.

---

## Smoke test (one‑pass)

Save as `scripts/test_cli.sh`, make executable, then run to validate end‑to‑end without touching `main` (creates a temp branch and cleans up).

```bash
#!/usr/bin/env bash
set -euo pipefail

RED(){ printf "\033[31m%s\033[0m\n" "$*"; }
GRN(){ printf "\033[32m%s\033[0m\n" "$*"; }
YLW(){ printf "\033[33m%s\033[0m\n" "$*"; }
INFO(){ printf "[test] %s\n" "$*"; }
FAIL(){ RED "❌ $*"; exit 1; }
PASS(){ GRN "✅ $*"; }

[ -d .git ] || FAIL "Run from repo root."

# Prefer venv entry point
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

PASS "All CLI smoke tests passed."
```

Run it:

```bash
. .venv/bin/activate
chmod +x scripts/test_cli.sh
scripts/test_cli.sh
```

---

## Troubleshooting

* **PEP 668 / system pip blocked** → create and use a local venv (`python3 -m venv .venv; . .venv/bin/activate`).
* **`bpsai-pair` not found** → use module form: `PYTHONPATH=. .venv/bin/python -m tools.cli.bpsai_pair --help`.
* **`Local branch 'main' not found` in tests** → create/track `main` locally (`git fetch; git checkout -b main origin/main`).
* **Dirty working tree** → commit/stash before running `scripts/test_cli.sh` to keep noise minimal.

---

## Roadmap & versioning

* **v0.1.0** — Ship core package/CLI.
* **v0.2.0** — Template var substitution at init; JSON output mode; path‑filtered CI.
* **v0.3.0** — Public Python API mirroring CLI for integrators (e.g., Trello agent imports instead of shelling out).

Separate repos that *consume* this core:

* **paircoder‑ui** — BYO‑key local web UI wrapping `bpsai-pair`.

---

## Contributing

See **CONTRIBUTING.md**. Use Conventional Commits. Keep diffs small & reversible. Always update the Context Sync block.

---

## Security

See **SECURITY.md**. No secrets in repo or agent packs (`.agentpackignore` covers common paths). Use redacted fixtures/synthetic data.
