---
id: TASK-096
title: Agent invocation framework
status: done
priority: P0
complexity: 45
plan: plan-2025-12-sprint-16-real-subagents
sprint: sprint-16
tags:
- CLI
- orchestration
- agents
created: 2025-12-17
---

# TASK-096: Agent invocation framework

## Description

Create base `AgentInvoker` class that loads agent definitions from `.claude/agents/*.md` and invokes them via `HeadlessSession`.

## Acceptance Criteria

- [ ] `AgentDefinition` dataclass parses YAML frontmatter from agent files
- [ ] `AgentInvoker.load_agent(name)` loads agent definition
- [ ] `AgentInvoker.invoke(agent, context)` invokes via HeadlessSession
- [ ] Permission mode from agent definition is respected
- [ ] Model selection from agent definition is respected
- [ ] Structured `InvocationResult` returned with output, cost, tokens
- [ ] Unit tests for loading and invocation

## Implementation Details

### Files to create/modify

- `tools/cli/bpsai_pair/orchestration/invoker.py` (new)
- `tools/cli/bpsai_pair/orchestration/__init__.py` (export)

### Key classes

```python
@dataclass
class AgentDefinition:
    name: str
    description: str
    model: str  # sonnet, opus, haiku
    permission_mode: str  # plan, auto
    tools: list[str]
    system_prompt: str  # Body of agent .md file

@dataclass
class InvocationResult:
    success: bool
    output: str
    cost_usd: float
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    error: Optional[str]

class AgentInvoker:
    def __init__(self, agents_dir: Path)
    def load_agent(self, name: str) -> AgentDefinition
    def invoke(self, agent: AgentDefinition, context: str) -> InvocationResult
```

### Existing infrastructure to use

- `HeadlessSession` from `orchestration/headless.py`
- Agent files in `.claude/agents/*.md`

## Notes

This is the foundation task - other agent implementations depend on this.