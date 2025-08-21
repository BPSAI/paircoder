# PairCoder — AI-Augmented Pair Programming Framework

PairCoder is a structured framework for working with AI coding agents (GPT-5, Claude, Codex) as reliable pair programming partners.  
It provides governance, context persistence, and a CLI+UI pipeline that keeps AI agents grounded in project goals and repo state.

---

## ✨ Key Features

- **Context as Memory**: All important state is persisted in `/context/*.md` files (development roadmap, agent playbook, project tree).
- **Roadmap Driven**: Agents generate a 3-phase roadmap and continuously sync progress in context.
- **Governance Templates**: Contributing, PR, and Security policies are pre-seeded.
- **Pre-Commit Discipline**: Linting, formatting, and secret scanning are enforced.
- **CLI Tools** (`bpsai-pair`):
  - `init` — bootstrap governance, context, and prompts
  - `feature` — create new feature branches with context sync
  - `pack` — bundle context for agent upload
  - `context-sync` — update context sync loop programmatically
- **CI Integration**: GitHub Actions workflows keep context/project_tree updated and run lint/tests.

---

## 📂 Repository Layout

context/ # Development roadmap, agent playbook, project tree
prompts/ # YAML prompt templates for roadmap, deep research, implementation
scripts/ # Shell scripts for feature branching and packaging
tools/cli/ # Typer-based CLI (bpsai-pair)
tools/cookiecutter-paircoder/ # Cookiecutter template for new repos
.github/workflows/ # CI and project_tree sync workflows

yaml
Copy
Edit

---

## 🚀 Getting Started

### Install CLI locally
```bash
cd tools/cli
pip install -e .
Verify CLI works
bash
Copy
Edit
bpsai-pair --help
Bootstrap Repo Context
bash
Copy
Edit
bpsai-pair init tools/cookiecutter-paircoder
Create Feature Branch
bash
Copy
Edit
bpsai-pair feature login-system --primary "Implement login" --phase "Phase 1: Scaffolding"
Sync Context
bash
Copy
Edit
bpsai-pair context-sync --last "Roadmap generated" --nxt "Initialize feature branch"
🧩 Roadmap
Phase 0–2 (Complete):

Governance files, CI workflows, context discipline

CLI + cookiecutter bootstrap

Phase 3 (Upcoming):

Local BYO API key web app

UI to trigger roadmap, feature, and context sync flows

Future:

Vector-based memory integration

Richer agent orchestration

Multi-agent collaboration

🤝 Contributing
See CONTRIBUTING.md.
Follow PR template guidelines and always update context sync loop.

🔒 Security
Please review SECURITY.md for vulnerability disclosure policies.

yaml
Copy
Edit

---

# 2. CLI Testing Plan

Before we move to Phase 3, we should **systematically test the CLI**:

1. **Basic help check**
   ```bash
   python -m tools.cli.bpsai_pair --help
Expected: shows init, feature, pack, context-sync.

Init flow

bash
Copy
Edit
bpsai-pair init tools/cookiecutter-paircoder
Expected: copies governance, prompts, context into repo root. Skips existing files safely.

Feature branch flow

bash
Copy
Edit
bpsai-pair feature demo --primary "Smoke Test" --phase "Phase 1: Init"
Expected: creates feature/demo branch, scaffolds context, commits files.

Pack context

bash
Copy
Edit
bpsai-pair pack context.tar.gz
Expected: tarball with context + prompts is created.

Context sync

bash
Copy
Edit
bpsai-pair context-sync --last "Ran feature command" --nxt "Proceed to Phase 3"
Expected: context/development.md updated with a new Context Sync block.
