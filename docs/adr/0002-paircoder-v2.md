# ADR 0002 — Paircoder v2 Architecture

**Status:** Accepted
**Date:** 2025-12-12
**Authors:** BPS AI Software Team

---

## Context

Paircoder v1 established a disciplined workflow for AI pair programming: context loops, agent packs, feature branching, and validation tooling. As AI capabilities advance, users need:

1. **Native workflow orchestration** — Human-readable "flows" that agents can execute step-by-step
2. **Multi-provider support** — Freedom to use OpenAI, Anthropic, Google, or other providers
3. **Smart routing** — Automatic model selection based on task complexity and cost constraints
4. **Efficiency controls** — Token budgets, prompt caching, and cost awareness

This ADR locks the design constraints and compatibility rules for v2.

---

## Decision

### What Stays Stable (v1 Compatibility)

The following **MUST NOT** change behavior or break existing workflows:

| Component | Location | Guarantee |
|-----------|----------|-----------|
| CLI commands | `bpsai-pair init/feature/pack/context-sync/status/validate/ci` | Same flags, same output semantics |
| Context Loop | `context/development.md` with Overall/Last/Next/Blockers fields | Format unchanged |
| Agent Pack | `.tgz` respecting `.agentpackignore`, includes `context/`, `prompts/`, directory notes | Same archive structure |
| Template layout | `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` | Existing files preserved |
| Cross-platform | Pure Python, no bash-only dependencies | Windows/macOS/Linux parity |
| Configuration | `paircoder.yaml` or `pyproject.toml` sections | Backward-compatible schema |

**Migration policy:** No dedicated migration command. v2 features are opt-in additions; v1 repos continue working unchanged.

### What's New (v2 Additions)

#### 1. Flows System

A declarative workflow engine for multi-step agent tasks.

```yaml
# flows/code-review.yaml
name: code-review
description: Review PR for correctness, style, and security
steps:
  - id: gather
    action: read-files
    inputs: { patterns: ["src/**/*.py", "tests/**/*.py"] }
  - id: analyze
    action: llm-call
    model: auto  # Router decides
    prompt: prompts/review.md
    context: { files: "{{ steps.gather.output }}" }
  - id: report
    action: write-file
    path: reviews/{{ pr_id }}.md
```

- **Location:** `flows/` directory (new)
- **Format:** YAML with Jinja2 templating
- **Execution:** `bpsai-pair flow run <name>` (new command)

#### 2. Orchestration Layer

A provider-agnostic runtime that routes requests to the best model.

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Task Classifier                        │
│  (complexity: trivial/moderate/complex/research)        │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Model Router                          │
│  - User-defined provider priority                        │
│  - Cost/capability matrix per model                      │
│  - Token budget enforcement                              │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌──────────┬──────────────┬──────────────┬───────────────┐
│ OpenAI   │  Anthropic   │   Google     │   (future)    │
│ gpt-4o   │  claude-4    │   gemini-2   │               │
│ o1       │  claude-3.5  │   gemini-1.5 │               │
└──────────┴──────────────┴──────────────┴───────────────┘
```

- **Location:** `tools/cli/bpsai_pair/orchestrator/` (new module)
- **Config:** `paircoder.yaml` → `orchestrator:` section
- **API keys:** Environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`)

#### 3. Provider Extensibility

Initial providers (v2.0):
- **OpenAI:** GPT-4o, GPT-4-turbo, o1-preview, o1-mini
- **Anthropic:** Claude 4 Opus, Claude 4 Sonnet, Claude 3.5 Sonnet
- **Google:** Gemini 2.0, Gemini 1.5 Pro

Extension mechanism:
```python
# bpsai_pair/providers/base.py
class Provider(ABC):
    @abstractmethod
    def complete(self, messages, **kwargs) -> Response: ...
    @abstractmethod
    def capabilities(self) -> ProviderCaps: ...
```

#### 4. Efficiency Features

| Feature | Description | Config |
|---------|-------------|--------|
| Token budgeting | Per-flow and per-session limits | `orchestrator.budget.max_tokens` |
| Prompt caching | Hash-based cache for repeated prompts | `orchestrator.cache.enabled` |
| Cost tracking | Log estimated costs per request | `orchestrator.cost.log_path` |
| Model routing | Complexity → model mapping rules | `orchestrator.routing.rules` |

### What's Explicitly NOT Included

These features are **out of scope** for v2 to avoid bloat:

| Exclusion | Rationale |
|-----------|-----------|
| Planning OS / task hierarchy | Adds complexity without clear value; use external tools |
| Project memory graphs | Speculative; context loop is sufficient |
| Auto-commit or git automation | Too opinionated; users control git |
| GUI or web interface | Out of scope for CLI tool |
| Migration command | v1 → v2 is additive; no migration needed |
| Plugin marketplace | Premature; start with built-in providers |
| Persistent agent state | Flows are stateless; state lives in files |

---

## Architecture Constraints

### Module Structure (v2)

```
tools/cli/bpsai_pair/
├── cli.py                 # Existing CLI (stable)
├── ops.py                 # Existing operations (stable)
├── config.py              # Extended for v2 config
├── orchestrator/          # NEW: routing + runtime
│   ├── __init__.py
│   ├── router.py          # Model selection logic
│   ├── classifier.py      # Task complexity detection
│   └── budget.py          # Token/cost tracking
├── providers/             # NEW: provider adapters
│   ├── __init__.py
│   ├── base.py            # Abstract provider
│   ├── openai.py
│   ├── anthropic.py
│   └── google.py
└── flows/                 # NEW: flow engine
    ├── __init__.py
    ├── parser.py          # YAML flow parsing
    ├── executor.py        # Step execution
    └── actions.py         # Built-in actions
```

### New CLI Commands (v2)

```bash
# Flow execution
bpsai-pair flow list                    # List available flows
bpsai-pair flow run <name> [--var k=v]  # Execute a flow
bpsai-pair flow validate <name>         # Validate flow syntax

# Orchestration
bpsai-pair provider list                # Show configured providers
bpsai-pair provider test [name]         # Test provider connectivity
bpsai-pair budget status                # Show token/cost usage
```

### Configuration Schema (v2 additions)

```yaml
# paircoder.yaml
version: 2

# v1 sections remain unchanged
context:
  dir: context

# v2 additions
orchestrator:
  default_provider: anthropic
  providers:
    anthropic:
      models: [claude-sonnet-4-5-20250929, claude-3-5-sonnet-20241022]
      priority: 1
    openai:
      models: [gpt-4o, gpt-4-turbo]
      priority: 2
    google:
      models: [gemini-2.0-flash]
      priority: 3
  routing:
    trivial: openai/gpt-4o-mini
    moderate: anthropic/claude-3-5-sonnet-20241022
    complex: anthropic/claude-sonnet-4-5-20250929
    research: anthropic/claude-sonnet-4-5-20250929
  budget:
    max_tokens_per_session: 100000
    warn_at_percent: 80
  cache:
    enabled: true
    ttl_hours: 24

flows:
  dir: flows
  variables:
    default_reviewer: "team"
```

---

## Consequences

### Positive

1. **Backward compatible** — Existing v1 users unaffected
2. **Progressive adoption** — Teams enable v2 features as needed
3. **Provider freedom** — No vendor lock-in
4. **Cost control** — Budgets prevent runaway spending
5. **Reproducible workflows** — Flows are version-controlled YAML

### Negative

1. **Increased surface area** — More code to maintain
2. **API key management** — Users must secure credentials
3. **Testing complexity** — Must mock multiple providers

### Mitigations

- Comprehensive test suite with provider mocks
- Clear documentation for credential management
- Feature flags to disable unused v2 components

---

## Implementation Phases

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| 0 | This ADR | Design locked |
| 1 | Provider abstraction | `providers/` module with OpenAI/Anthropic/Google |
| 2 | Orchestrator core | Router + classifier + budget tracking |
| 3 | Flows MVP | Parser + executor + basic actions |
| 4 | CLI integration | New commands wired up |
| 5 | Documentation | User guide + examples |

---

## References

- ADR 0001: Context Loop design
- `/context/agents.md`: Development workflow
- `/tools/cli/README.md`: Current CLI documentation
