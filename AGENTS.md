# Agents Guide (Root Pointer)

AI agents should start here, then follow the pointers below.

## Where to find instructions

All agent instructions, context, and guidance are maintained in the `/context` directory:

1. **Start with:** `/context/agents.md` - Complete AI pairing playbook
2. **Current state:** `/context/development.md` - Roadmap and Context Loop
3. **Project structure:** `/context/project_tree.md` - Auto-updated file tree
4. **Component docs:** `/context/directory_notes/` - Per-directory guidance

## Quick reminder

This repository serves two purposes:
- **Package development** (`tools/cli/`) - The bpsai-pair CLI tool
- **Living example** - Demonstrating PairCoder best practices

Always check the Context Loop in `/context/development.md` for the latest state:
- Overall goal
- Last action
- Next action
- Blockers

Do NOT modify files under `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` unless explicitly improving the template.
