# TASK-038: Codex Optimization Pass

## Metadata
- **ID**: TASK-038
- **Plan**: paircoder-v2.2-features
- **Sprint**: sprint-9
- **Priority**: P2
- **Complexity**: 35
- **Status**: done
- **Created**: 2025-12-15
- **Tags**: enhancement, codex, optimization
- **changelog_entry**: Optimized AGENTS.md and context for Codex CLI efficiency

## Description

User noted that Codex "wasted energy" during validation runs. This task optimizes the context and instructions for Codex CLI's 32KB context limit and behavioral patterns.

**Note:** This is lower priority (P2). Defer if Sprint 9 is time-constrained. Core functionality works without this optimization.

## Objectives

1. Review AGENTS.md for Codex-specific guidance
2. Ensure context packs fit within 32KB limit
3. Add Codex-specific instructions to reduce unnecessary exploration
4. Document best practices for Codex usage

## Analysis: Codex vs Claude Code

| Aspect | Claude Code | Codex CLI |
|--------|-------------|-----------|
| Context limit | 200K tokens | 32K tokens |
| Approval modes | plan, auto, full | suggest, auto-edit, full-auto |
| Strengths | Complex reasoning, architecture | Rapid iteration, file ops |
| Weaknesses | Can be verbose | Limited context, exploration |
| Best for | Design, review | Refactoring, bulk edits |

## Optimization Areas

### 1. Context Size Reduction

The default context pack may exceed 32KB. Create a "lite" pack option:

```bash
# Full context (for Claude)
bpsai-pair pack --out full-context.tgz

# Lite context (for Codex)
bpsai-pair pack --lite --out codex-context.tgz
```

**Lite pack includes:**
- state.md (essential - what's current)
- Relevant task file only (not all tasks)
- Abbreviated project.md (key constraints only)
- NO flows (Codex doesn't use them same way)

**Lite pack excludes:**
- capabilities.yaml (Claude-specific)
- workflow.md (too verbose for 32K)
- Full project tree

### 2. AGENTS.md Codex Section

Add Codex-specific section to AGENTS.md:

```markdown
## Codex CLI Notes

When working with Codex CLI:

1. **Be direct** - Codex works best with clear, specific instructions
2. **One task at a time** - Don't give multi-step plans
3. **File-focused** - Tell it exactly which files to modify
4. **Avoid exploration** - Don't ask "what should we do?" - tell it what to do
5. **Use full-auto sparingly** - Prefer auto-edit for more control

### Codex-Optimized Task Format

Instead of:
> "Design and implement a caching system for context files"

Use:
> "In tools/cli/bpsai_pair/context/cache.py, create a ContextCache class with get(), set(), and invalidate() methods. Use sha256 for cache keys and JSON for the index file."

### Context Limit

Codex has 32KB context limit. If you hit limits:
1. Use `bpsai-pair pack --lite` for minimal context
2. Focus on specific files, not whole project
3. Reference docs by path instead of including them
```

### 3. Capabilities.yaml Codex Profile

Update capabilities.yaml with Codex constraints:

```yaml
agents:
  codex-cli:
    context_limit: 32000
    strengths:
      - rapid-iteration
      - file-operations
      - refactoring
      - bulk-edits
    weaknesses:
      - complex-reasoning
      - architecture-decisions
      - multi-step-planning
    cost_per_1k: 0.01
    best_for:
      - "Simple bug fixes"
      - "Mechanical refactoring"
      - "File renames/moves"
      - "Adding tests for existing code"
    avoid_for:
      - "Architectural decisions"
      - "Complex feature design"
      - "Security-sensitive code"
```

### 4. Orchestrator Routing Optimization

Update orchestrator to better route to Codex:

```python
# In orchestrator.py

def should_use_codex(task: TaskCharacteristics) -> bool:
    """Determine if Codex is appropriate for this task."""
    
    # Good for Codex
    if task.task_type == TaskType.REFACTOR:
        return True
    if task.complexity <= TaskComplexity.SIMPLE:
        return True
    if task.requires_iteration and not task.requires_reasoning:
        return True
    
    # Bad for Codex
    if task.task_type in [TaskType.DESIGN, TaskType.REVIEW]:
        return False
    if task.requires_reasoning:
        return False
    if task.estimated_context_size > 30000:  # Near 32K limit
        return False
    
    return False
```

### 5. Handoff Pack Size Check

Add size check to handoff creation:

```python
# In handoff.py

def create_handoff(self, task_id: str, target_agent: str) -> HandoffPackage:
    package = self._build_package(task_id)
    
    if target_agent == "codex-cli":
        size = self._estimate_size(package)
        if size > 30000:  # Leave buffer for prompt
            logger.warning(f"Handoff package ({size} tokens) may exceed Codex limit")
            package = self._create_lite_package(task_id)
    
    return package
```

## Implementation Steps

### Phase 1: Documentation Updates

1. Update AGENTS.md with Codex section
2. Update capabilities.yaml with Codex profile
3. Add Codex best practices to USER_GUIDE.md

### Phase 2: CLI Enhancements

1. Add `--lite` flag to pack command
2. Add size estimation to pack output
3. Warn if pack exceeds 32KB

### Phase 3: Orchestrator Updates

1. Add context size to task characteristics
2. Update routing to consider Codex limits
3. Add size check to handoff creation

## Acceptance Criteria

- [ ] AGENTS.md has Codex-specific guidance section
- [ ] capabilities.yaml has Codex agent profile
- [ ] `bpsai-pair pack --lite` produces <32KB output
- [ ] Pack command shows size estimate
- [ ] Warning when pack exceeds Codex limit
- [ ] Orchestrator considers context size in routing
- [ ] USER_GUIDE.md has Codex best practices

## Dependencies

- TASK-028 (Orchestrator) - completed
- TASK-026 (Handoff) - completed

## Files to Modify

**Documentation:**
- `AGENTS.md` (add Codex section)
- `.paircoder/capabilities.yaml` (add Codex profile)
- `USER_GUIDE.md` (add Codex best practices)

**Code:**
- `tools/cli/bpsai_pair/ops.py` (add --lite pack option)
- `tools/cli/bpsai_pair/orchestration/orchestrator.py` (size-aware routing)
- `tools/cli/bpsai_pair/orchestration/handoff.py` (size check)
- `tools/cli/bpsai_pair/cli.py` (add --lite flag)

## Notes

- This is P2 priority - core functionality works without it
- Focus on documentation first, code changes second
- Real-world Codex testing would be valuable but not required
- Consider deferring code changes to future sprint if time-constrained
