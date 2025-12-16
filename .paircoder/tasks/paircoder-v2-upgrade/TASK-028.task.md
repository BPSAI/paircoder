# TASK-028: Orchestrator Service

## Metadata
- **ID**: TASK-028
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-6
- **Priority**: P2
- **Complexity**: 60
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: orchestration, multi-agent, routing, automation

## Description

Implement the orchestrator service that intelligently routes tasks to the most appropriate AI coding agent based on task characteristics, agent capabilities, cost, and availability.

## Objectives

1. Define agent capability profiles
2. Implement task-to-agent matching algorithm
3. Create orchestration loop (assign, monitor, handoff)
4. Support multi-agent workflows (Claude → Codex → Claude)
5. Handle failures and fallbacks

## Technical Requirements

### Agent Capability Profiles

```yaml
# .paircoder/capabilities.yaml
agents:
  claude-code:
    strengths:
      - complex-reasoning
      - architecture-design
      - code-review
      - documentation
    weaknesses:
      - rapid-iteration
      - bulk-file-operations
    cost_per_1k_tokens: 0.015
    context_limit: 200000
    availability: local
    
  codex-cli:
    strengths:
      - rapid-iteration
      - file-operations
      - shell-commands
      - refactoring
    weaknesses:
      - complex-reasoning
      - architecture
    cost_per_1k_tokens: 0.01
    context_limit: 32000
    availability: local
    
  cursor:
    strengths:
      - ide-integration
      - interactive-editing
      - ui-development
    weaknesses:
      - headless-operation
      - automation
    cost_per_1k_tokens: 0.012
    context_limit: 100000
    availability: optional
```

### Task Characteristics

```python
class TaskCharacteristics:
    complexity: Literal['low', 'medium', 'high']
    type: Literal['design', 'implement', 'review', 'refactor', 'fix']
    scope: Literal['single-file', 'multi-file', 'cross-module']
    risk: Literal['low', 'medium', 'high']
    estimated_tokens: int
    requires_reasoning: bool
    requires_iteration: bool
```

### Matching Algorithm

```python
def select_agent(task: TaskCharacteristics, 
                 available_agents: List[str],
                 preferences: dict) -> str:
    """
    Score each agent and return best match.
    
    Scoring factors:
    - Strength match (40%)
    - Cost efficiency (20%)
    - Context fit (20%)
    - Availability (10%)
    - User preference (10%)
    """
```

### Orchestrator Loop

```python
class Orchestrator:
    def __init__(self, config_path: Path):
        self.agents = load_capabilities(config_path)
        self.sessions = {}
        
    def assign_task(self, task_id: str) -> Assignment:
        """Analyze task, select agent, create assignment"""
        
    def execute(self, assignment: Assignment) -> Result:
        """Execute task with selected agent"""
        
    def monitor(self, assignment: Assignment) -> Status:
        """Check progress, handle timeouts"""
        
    def handoff(self, assignment: Assignment, target_agent: str) -> Assignment:
        """Transfer task to different agent"""
        
    def run(self, task_ids: List[str]) -> BatchResult:
        """Execute multiple tasks with optimal routing"""
```

### CLI Integration

```bash
# Auto-route task to best agent
bpsai-pair orchestrate --task TASK-025

# Route with constraints
bpsai-pair orchestrate --task TASK-025 --prefer claude --max-cost 0.50

# Batch orchestration
bpsai-pair orchestrate --plan sprint-6 --parallel 2

# Show routing decision without executing
bpsai-pair orchestrate --task TASK-025 --dry-run
```

### Multi-Agent Workflow Example

```yaml
# Complex task flow
workflow:
  - agent: claude-code
    mode: plan
    task: "Design authentication system"
    output: design.md
    
  - agent: codex-cli
    mode: full-auto
    task: "Implement basic auth per design.md"
    output: src/auth/
    
  - agent: claude-code
    mode: plan
    task: "Review implementation against design"
    output: review.md
```

## Acceptance Criteria

- [ ] Capability profiles loaded from config
- [ ] Task characteristics extracted from task files
- [ ] Matching algorithm selects appropriate agent
- [ ] Single-task orchestration works end-to-end
- [ ] Handoff between agents works (Claude → Codex)
- [ ] Dry-run mode shows decisions without executing
- [ ] Failures handled with fallback options
- [ ] Execution logged for debugging
- [ ] Unit tests for matching algorithm
- [ ] Integration test for full orchestration loop

## Dependencies

- TASK-025 (headless mode)
- TASK-026 (handoff protocol)
- TASK-027 (Codex adapter)
- Capability profiles defined

## Files to Create/Modify

- `tools/cli/src/paircoder/orchestration/orchestrator.py`
- `tools/cli/src/paircoder/orchestration/matcher.py`
- `tools/cli/src/paircoder/orchestration/monitor.py`
- `tools/cli/src/paircoder/commands/orchestrate.py`
- `.paircoder/capabilities.yaml` (template)
- `tools/cli/tests/test_orchestrator.py`
- `tools/cli/tests/test_matcher.py`

## Notes

- Start simple: just Claude + Codex routing
- Don't over-engineer the matching algorithm initially
- Prefer deterministic routing over ML-based
- Log decisions for transparency and debugging
- Consider cost tracking integration (TASK-030)

## Routing Decision Tree (v1)

```
Task received
├── Is it design/architecture?
│   └── Yes → Claude (plan mode)
├── Is it code review?
│   └── Yes → Claude (plan mode)
├── Is it bulk refactoring?
│   └── Yes → Codex (full-auto)
├── Is it rapid implementation?
│   └── Yes → Codex (auto-edit)
├── Is it complex implementation?
│   └── Yes → Claude (auto)
└── Default → Claude (auto)
```

## Future Enhancements (Post-Sprint 6)

- Learning from execution results
- Cost optimization mode
- Parallel execution
- Queue management
- External agent plugins
