# PairCoder Reference Project

This directory is a **living example** of how to use the PairCoder package.
Workflows you can run **from inside this folder**:

```bash
# initialize (bundled template already applied to this repo; keep up to date)
bpsai-pair-init

# create a feature branch with context alignment
bpsai-pair feature example-feature \
  --type refactor \
  --primary "Show end-to-end PairCoder flow" \
  --phase "Phase 1: Scaffolding"

# create/upload context pack to agent session
bpsai-pair pack --out agent_pack.tgz

# update the Context Loop
bpsai-pair context-sync \
  --last "Did X" \
  --next "Do Y" \
  --blockers "None"
```

### Context Loop
Keep `context/development.md` synced on every commit:
- **Overall goal is** / **Last action was** / **Next action will be** / **Blockers**

### Agent Pack Exclusions
`reference/.agentpackignore` excludes heavy/irrelevant artifacts for agents.

