# Claude Guide (Root Pointer)

Claude, please follow these instructions to work effectively in this repository.

## Getting started

1. Read `/context/agents.md` for complete pairing instructions
2. Check `/context/development.md` for current project state and goals
3. Review `/context/project_tree.md` for current file structure

## Repository context

This is the PairCoder development repository. It has two roles:
- Developing the `bpsai-pair` package (in `tools/cli/`)
- Serving as a reference implementation of PairCoder methodology

## Key principle

Always update the Context Loop after meaningful changes:
```bash
bpsai-pair context-sync --last "What you just did" --next "Next step" --blockers "Any issues"
```

See `/context/` for all detailed instructions.
