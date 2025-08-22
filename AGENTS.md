# Agents Guide (Root Entrypoint)

Welcome. This repository **is the package** published as `bpsai-pair`. Your job is to improve the
CLI, the template bundle, and the docs — while following the **PairCoder Context Loop**.

## Where to look (in order)
1. `context/` — Maintainers' Context Loop lives here. Start with `context/development.md`.
2. `README.md` — Package installation & CLI usage.
3. `tools/cli/` — Python package source (CLI + ops + utils) and template bundle under
   `tools/cli/bpsai_pair/data/cookiecutter-paircoder/`.

## Do **not** modify
- Anything under `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` unless the change is explicitly
  a template improvement. Never copy this repo's local state into the template.
- Built artifacts: `tools/cli/dist/`, `tools/cli/build/`, `*.egg-info/`.

## Context Loop (always update)
Keep these fields current in `context/development.md`:
- **Overall goal is:** one sentence mission
- **Last action was:** what just completed
- **Next action will be:** the next atomic step
- **Blockers:** decisions/issues

## Typical flows
```bash
# Create/align a feature branch (for package work)
# (No shell scripts required; CLI uses Python ops)
bpsai-pair feature ops-json \
  --type refactor \
  --primary "Extend pack --json to include sizes" \
  --phase "Phase 2: Portability & CI"

# Create/upload a minimal context pack
autopack='agent_pack.tgz'
bpsai-pair pack --out "$autopack"

# Update the loop
bpsai-pair context-sync --last "Added ops.json details" --next "Wire CLI flag" --blockers ""
```

## Large trees & exclusions
Heavy or irrelevant trees must be excluded via `.agentpackignore` (root).
Agents should assume excluded assets exist; avoid suggestions that remove or rename them.
