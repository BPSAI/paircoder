# TASK-027: Codex CLI Adapter

## Metadata
- **ID**: TASK-027
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-6
- **Priority**: P1
- **Complexity**: 45
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: codex, adapter, flows, cross-agent

## Description

Create an adapter that enables Codex CLI to execute PairCoder flows. This parses `.flow.md` files and translates them into Codex-compatible prompts, enabling cross-agent workflow consistency.

## Objectives

1. Parse `.flow.md` files into structured workflow objects
2. Translate workflow steps into Codex prompts
3. Execute workflows via Codex CLI (full-auto mode)
4. Capture and report execution results
5. Handle Codex-specific constraints (token limits, approval modes)

## Technical Requirements

### Flow File Structure (Reference)

```markdown
# Flow: design-plan-implement

## Description
Turn feature requests into validated designs and implementation plans.

## Triggers
- User describes a feature to build
- Words: design, plan, approach, feature

## Steps

### 1. Clarify Requirements
- Ask clarifying questions
- Confirm understanding
- Output: requirements.md

### 2. Design Solution
- Analyze existing code
- Propose architecture
- Output: design.md

### 3. Create Plan
- Break into tasks
- Estimate complexity
- Output: plan.md
```

### Flow Parser

```python
class Flow:
    name: str
    description: str
    triggers: List[str]
    steps: List[FlowStep]

class FlowStep:
    name: str
    instructions: List[str]
    outputs: List[str]

def parse_flow(path: Path) -> Flow:
    """Parse .flow.md into structured Flow object"""
```

### Codex Adapter

```python
class CodexAdapter:
    def __init__(self, approval_mode='suggest'):
        self.approval_mode = approval_mode  # suggest, auto-edit, full-auto
        
    def execute_flow(self, flow: Flow, context: dict) -> FlowResult:
        """Execute flow via Codex CLI"""
        
    def translate_step(self, step: FlowStep) -> str:
        """Convert step to Codex prompt"""
```

### Codex CLI Invocation

```bash
# Interactive mode (default)
codex "Execute step 1: Clarify Requirements"

# Auto-edit mode (applies changes, asks approval)
codex --approval-mode auto-edit "Execute step 2"

# Full-auto mode (no approval needed)
codex --approval-mode full-auto "Execute step 3"

# With context file
codex --context-file handoff.md "Continue from handoff"
```

### CLI Integration

```bash
# Execute flow with Codex
bpsai-pair flow design-plan-implement --agent codex --mode full-auto

# List available flows for agent
bpsai-pair flow list --agent codex

# Validate flow compatibility
bpsai-pair flow validate design-plan-implement --agent codex
```

## Acceptance Criteria

- [ ] Parse all standard .flow.md files without error
- [ ] Translate flow steps to effective Codex prompts
- [ ] Execute single-step flows via Codex CLI
- [ ] Execute multi-step flows with step tracking
- [ ] Capture Codex output and exit codes
- [ ] Handle Codex token/context limits gracefully
- [ ] Support all approval modes (suggest, auto-edit, full-auto)
- [ ] Unit tests for flow parser
- [ ] Integration test with real Codex CLI

## Dependencies

- Codex CLI installed (`npm install -g @openai/codex`)
- Existing flow files in `.paircoder/flows/`
- TASK-025 (pattern for CLI wrapper)

## Files to Create/Modify

- `tools/cli/src/paircoder/flows/parser.py`
- `tools/cli/src/paircoder/adapters/__init__.py`
- `tools/cli/src/paircoder/adapters/codex.py`
- `tools/cli/src/paircoder/commands/flow.py` (modify)
- `tools/cli/tests/test_flow_parser.py`
- `tools/cli/tests/test_codex_adapter.py`

## Notes

- Codex has different context limits than Claude - be mindful
- full-auto mode is powerful but risky - use judiciously
- Consider dry-run mode for testing without execution
- Log all Codex invocations for debugging
- Codex uses AGENTS.md for context - leverage this

## Codex-Specific Considerations

| Feature | Codex Behavior | Adaptation Needed |
|---------|----------------|-------------------|
| Context | Reads AGENTS.md | Ensure flows referenced |
| Approval | 3 modes | Map to flow risk level |
| Output | Markdown + code | Parse structured output |
| Limits | 32KB context | Chunk large flows |

## Example

```python
# Parse and execute flow
flow = parse_flow('.paircoder/flows/tdd-implement.flow.md')
adapter = CodexAdapter(approval_mode='auto-edit')
result = adapter.execute_flow(flow, context={
    'task': 'TASK-025',
    'focus': 'Add retry logic to headless.py'
})

print(result.success)  # True
print(result.files_modified)  # ['src/headless.py', 'tests/test_headless.py']
```
