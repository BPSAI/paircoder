# Deprecated Directory

This `context/` directory is deprecated as of PairCoder v2.1.

Context files should now be in `.paircoder/context/`:
- `.paircoder/context/project.md` - Project overview
- `.paircoder/context/workflow.md` - Development workflow
- `.paircoder/context/state.md` - Current state (replaces development.md)

This directory will be removed in a future version.

## Migration

If you have existing files here, move them to `.paircoder/context/`:

```bash
mkdir -p .paircoder/context
mv context/development.md .paircoder/context/state.md
mv context/agents.md AGENTS.md
mv context/project_tree.md .paircoder/context/
```

Then update your workflows to reference the new paths.
