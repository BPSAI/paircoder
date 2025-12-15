# PairCoder Project Context

## What Is This Project?

PairCoder is a CLI tool and framework for AI-augmented pair programming. It provides:

1. **Context Management** — Structured project memory that persists across sessions
2. **Planning System** — Goals decomposed into tasks organized into sprints
3. **Flows** — Reusable workflows that guide AI agents through complex tasks
4. **Agent Packs** — Portable context bundles for handoff between sessions/tools
5. **Multi-Provider Support** — Works with Claude, GPT, Gemini, and others

## Repository Structure

```
paircoder/
├── .paircoder/              # v2 system files (YOU ARE HERE)
│   ├── config.yaml          # Project configuration
│   ├── capabilities.yaml    # LLM capability manifest
│   ├── context/             # Project memory
│   ├── flows/               # Workflow definitions
│   ├── plans/               # Active plans
│   └── tasks/               # Task files by plan
├── tools/cli/               # The CLI package
│   ├── bpsai_pair/          # Python package source
│   └── pyproject.toml       # Package metadata
├── docs/                    # Documentation
│   └── adr/                 # Architecture Decision Records
├── context/                 # DEPRECATED: v1 context (migrating)
└── [governance files]       # LICENSE, CONTRIBUTING, etc.
```

## Key Constraints

| Constraint | Requirement |
|------------|-------------|
| **Python Version** | 3.9+ (cross-platform compatibility) |
| **Dependencies** | Minimal; pure Python where possible |
| **Platform** | Windows, macOS, Linux parity |
| **CLI Stability** | v1 commands must continue working |
| **File Format** | YAML for config/plans, Markdown for docs/flows |

## Current State (v2 Upgrade)

We are upgrading from v1 to v2. Key changes:

- **Consolidation**: All system files move under `.paircoder/`
- **Planning**: New Goals → Tasks → Sprints system
- **Flows**: Enhanced with YAML frontmatter + Markdown body
- **LLM Integration**: `capabilities.yaml` tells LLMs what they can do

See `.paircoder/context/state.md` for current progress.

## Architecture Principles

1. **File-Based State** — No databases; everything is human-readable files
2. **Opt-In Complexity** — Simple projects need only `config.yaml`
3. **LLM-First Design** — Structure files so AI agents can understand them
4. **Composable Flows** — Small flows that chain together
5. **Provider Agnostic** — Don't lock users into one AI provider

## How to Work Here

1. Read `.paircoder/context/state.md` for current plan/task status
2. Check `.paircoder/capabilities.yaml` to understand available actions
3. Follow the active flow for structured work
4. Update `state.md` after completing significant work

## Important Files

| File | Purpose |
|------|---------|
| `.paircoder/config.yaml` | Project configuration |
| `.paircoder/capabilities.yaml` | What LLMs can do here |
| `.paircoder/context/state.md` | Current status and active work |
| `docs/adr/0002-paircoder-v2.md` | v2 architecture decisions |
| `tools/cli/bpsai_pair/cli.py` | CLI entry point |
| `tools/cli/bpsai_pair/ops.py` | Core operations |

## Testing

```bash
cd tools/cli
pip install -e ".[dev]"
pytest
```

## Building

```bash
cd tools/cli
pip install build
python -m build
```
