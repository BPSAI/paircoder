# PairCoder Project Context

## What Is This Project?

PairCoder is a CLI tool and framework for AI-augmented pair programming. It provides:

1. **Context Management** — Structured project memory that persists across sessions
2. **Planning System** — Goals decomposed into tasks organized into sprints
3. **Skills** — Reusable workflows that guide AI agents through complex tasks
4. **Agent Packs** — Portable context bundles for handoff between sessions/tools
5. **Multi-Provider Support** — Works with Claude, GPT, Gemini, and others

## Repository Structure

```
paircoder/
├── .paircoder/              # v2 system files (YOU ARE HERE)
│   ├── config.yaml          # Project configuration
│   ├── capabilities.yaml    # LLM capability manifest
│   ├── context/             # Project memory
│   ├── plans/               # Active plans
│   ├── tasks/               # Task files by plan
│   └── docs/                # Internal docs (FEATURE_MATRIX, etc.)
├── .claude/                 # Claude Code integration
│   ├── skills/              # 5 skills for AI agents
│   └── agents/              # Custom subagent definitions
├── tools/cli/               # The CLI package
│   └── bpsai_pair/          # Python package source (see CLI Architecture)
├── docs/                    # Public documentation
│   └── adr/                 # Architecture Decision Records
└── [governance files]       # LICENSE, CONTRIBUTING, etc.
```

## CLI Architecture (tools/cli/bpsai_pair/)

```
bpsai_pair/
├── cli.py                   # Sub-app registration (~200 lines)
├── tokens.py                # Token estimation (tiktoken)
├── session.py               # Session detection
├── core/                    # Shared infrastructure
│   ├── config.py           # Configuration loading
│   ├── hooks.py            # Hook system (11 hooks)
│   ├── ops.py              # Git and file operations
│   ├── presets.py          # Project templates
│   └── utils.py            # Utilities
├── commands/                # General CLI commands (15 modules)
├── planning/                # plan, task, intent, standup
├── trello/                  # Trello integration
└── [other modules]          # github, security, mcp, etc.
```

## Key Constraints

| Constraint | Requirement                                     |
|------------|-------------------------------------------------|
| **Python Version** | 3.9+ (cross-platform compatibility)             |
| **Dependencies** | Minimal; pure Python where possible             |
| **Platform** | Windows, macOS, Linux parity                    |
| **CLI Stability** | v1 commands must continue working               |
| **File Format** | YAML for config/plans, Markdown for docs/skills |

## Current State (v2.8.0)

PairCoder v2.8.0 is the latest release with:

- **112 CLI commands** across 15 command groups
- **1774 tests** with comprehensive coverage
- **11 built-in hooks** for workflow automation
- **Token Budget System** for context management
- **Trello/GitHub integration** for project management

Key v2.8 features:
- **EPIC-003 Complete**: CLI architecture fully refactored
- **Token Estimation**: `budget estimate/status/check` commands
- **Session Management**: `session check/status` with compaction recovery

See `.paircoder/context/state.md` for current sprint progress.

## Architecture Principles

1. **File-Based State** — No databases; everything is human-readable files
2. **Opt-In Complexity** — Simple projects need only `config.yaml`
3. **LLM-First Design** — Structure files so AI agents can understand them
4. **Provider Agnostic** — Don't lock users into one AI provider

## How to Work Here

1. Read `.paircoder/context/state.md` for current plan/task status
2. Check `.paircoder/capabilities.yaml` to understand available actions
3. Follow the active skill for structured work
4. Update `state.md` after completing significant work

## Important Files

| File | Purpose |
|------|---------|
| `.paircoder/config.yaml` | Project configuration |
| `.paircoder/capabilities.yaml` | What LLMs can do here |
| `.paircoder/context/state.md` | Current status and active work |
| `.paircoder/docs/FEATURE_MATRIX.md` | Complete feature inventory |
| `tools/cli/bpsai_pair/cli.py` | CLI sub-app registration |
| `tools/cli/bpsai_pair/core/` | Shared infrastructure (config, hooks, ops) |
| `tools/cli/bpsai_pair/commands/` | CLI command implementations |
| `CHANGELOG.md` | Version history and release notes |

## Testing

```bash
cd tools/cli
pip install -e ".[dev]"
pytest                    # Run all 1774 tests
pytest -x                 # Stop on first failure
pytest -k "test_budget"   # Run specific tests
```

## Building

```bash
cd tools/cli
pip install build
python -m build
```
