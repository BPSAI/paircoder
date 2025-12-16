# Release Ready: bpsai-pair v2.4.0

> Generated: 2025-12-16

## Package Information

| Field | Value |
|-------|-------|
| Version | 2.4.0 |
| Package Name | bpsai-pair |
| Source | tools/cli/dist/bpsai_pair-2.4.0.tar.gz |
| Wheel | tools/cli/dist/bpsai_pair-2.4.0-py3-none-any.whl |

## Files Built

```
dist/
├── bpsai_pair-2.4.0-py3-none-any.whl  (178 KB)
└── bpsai_pair-2.4.0.tar.gz            (162 KB)
```

## Pre-Release Checklist

- [x] Version bumped in pyproject.toml (2.4.0)
- [x] Version bumped in __init__.py (2.4.0)
- [x] Version bumped in config.yaml (2.4)
- [x] CHANGELOG.md updated with v2.4.0 and v2.3.0 sections
- [x] README.md rewritten with all 64 commands
- [x] USER_GUIDE.md rewritten with all 18 sections
- [x] MCP_SETUP.md created
- [x] FEATURE_MATRIX.md created
- [x] TRELLO_TESTING.md created
- [x] All 245 tests pass
- [x] Package builds without errors
- [x] Test install succeeds
- [x] `--version` shows 2.4.0
- [x] MCP tools listed (13 tools)

## Test Install Verification

```bash
# Tested in clean venv:
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install dist/bpsai_pair-2.4.0-py3-none-any.whl

# Results:
bpsai-pair --version
# bpsai-pair version 2.4.0

bpsai-pair mcp tools
# Lists all 13 MCP tools

bpsai-pair --help
# Shows all command groups
```

## Manual Publish Command

When ready to publish to PyPI:

```bash
cd tools/cli
twine upload dist/*
```

Or with test PyPI first:

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ bpsai-pair==2.4.0
```

## Release Notes Summary

### v2.4.0 Highlights

**MCP Server Integration**
- 13 tools for autonomous agent operation
- Claude Desktop support via stdio transport
- `bpsai-pair mcp serve/tools/test` commands

**Auto-Hooks System**
- Automatic actions on task state changes
- Built-in hooks: start_timer, stop_timer, record_metrics, sync_trello, update_state, check_unblocked
- Configurable in config.yaml

**New Commands**
- `plan status` - Progress with task breakdown
- `plan sync-trello` - Create Trello cards from tasks
- `mcp serve` - Start MCP server
- `mcp tools` - List tools
- `mcp test` - Test tools locally

**Documentation**
- Complete README rewrite (64 commands)
- Complete USER_GUIDE rewrite (18 sections)
- MCP_SETUP.md for Claude Desktop
- FEATURE_MATRIX.md for all features

**Tests**
- 29 new MCP tests
- 245 total tests passing

## Dependencies

Core:
- typer>=0.12.3
- rich>=13.5.0
- pyyaml>=6.0.1
- cookiecutter>=2.6.0

Optional:
- mcp>=1.0.0 (for MCP server)

## Known Issues

1. License deprecation warning during build (cosmetic)
2. Trello integration needs manual E2E testing with credentials

## Post-Release Tasks

After publishing:
1. Create GitHub release with tag v2.4.0
2. Update GitHub releases page
3. Announce on relevant channels
4. Monitor for installation issues
