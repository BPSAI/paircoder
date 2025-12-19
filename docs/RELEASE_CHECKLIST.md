# Release Checklist

This checklist should be completed before every PairCoder release.

## Pre-Release Checks

### Version Bumping
- [ ] Bump version in `tools/cli/pyproject.toml`
- [ ] Bump version in `tools/cli/bpsai_pair/__init__.py`
- [ ] Bump version in `.paircoder/config.yaml` (version field)

### Documentation
- [ ] Update CHANGELOG.md with new version section
- [ ] Review and update README.md if needed
- [ ] Review and update docs/USER_GUIDE.md if features changed
- [ ] Update FEATURE_MATRIX.md if features added

### Testing
- [ ] All tests pass: `cd tools/cli && pytest -v`
- [ ] Test build: `cd tools/cli && python -m build`
- [ ] Test install in clean venv: `pip install dist/bpsai_pair-*.whl`
- [ ] Verify `bpsai-pair --version` shows correct version

### Template Sync Check (CRITICAL)

The cookie cutter template files must be synced with the current PairCoder source.

Run this command to verify no drift:
```bash
# Compare key template files against source
diff -u .paircoder/context/state.md tools/cli/bpsai_pair/data/cookiecutter-paircoder/\{\{cookiecutter.project_slug\}\}/.paircoder/context/state.md || echo "state.md template may need update"
```

**Template files to check:**
- [ ] `.paircoder/context/state.md` - matches current format (session tracking, sprint structure)
- [ ] `.paircoder/context/project.md` - includes current directory structure
- [ ] `.paircoder/context/workflow.md` - includes NON-NEGOTIABLE state.md update requirement
- [ ] `.paircoder/capabilities.yaml` - version 2.2+, includes CRITICAL notes
- [ ] `.paircoder/config.yaml` - includes all sections (trello, estimation, hooks, security)
- [ ] `.github/workflows/ci.yml` - proper quoting for conditionals
- [ ] `.github/workflows/project_tree.yml` - outputs to `.paircoder/context/` not `context/`
- [ ] `CODEOWNERS` - includes `.paircoder/` and `.claude/` paths
- [ ] `CLAUDE.md` - current instructions and skill list

### MCP Tools
- [ ] `bpsai-pair mcp tools` lists all expected tools
- [ ] `bpsai-pair mcp test` passes basic validation

## Release Process

1. Create release branch: `git checkout -b release/v<version>`
2. Complete all checklist items above
3. Build final package: `cd tools/cli && python -m build`
4. Create PR to main
5. After merge, tag release: `git tag v<version>`
6. Push tag: `git push origin v<version>`
7. Publish to PyPI: `cd tools/cli && twine upload dist/*`

## Post-Release

- [ ] Create GitHub release from tag
- [ ] Update GitHub releases page with notes
- [ ] Verify PyPI installation works: `pip install bpsai-pair==<version>`
- [ ] Monitor for installation issues

## Template Sync Command (Utility)

To quickly compare all template files with source:

```bash
#!/bin/bash
TEMPLATE_DIR="tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}"

echo "=== Checking template sync status ==="

# Key files to compare (source vs template pattern)
files=(
    ".paircoder/capabilities.yaml"
    ".paircoder/context/state.md"
    ".paircoder/context/workflow.md"
    ".github/workflows/ci.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ] && [ -f "$TEMPLATE_DIR/$file" ]; then
        if ! diff -q "$file" "$TEMPLATE_DIR/$file" > /dev/null 2>&1; then
            echo "⚠️  DIFFERS: $file"
        else
            echo "✓  synced: $file"
        fi
    else
        echo "?  missing: $file"
    fi
done
```
