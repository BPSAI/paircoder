# TASK-025: Headless Mode Integration for Orchestration

## Metadata
- **ID**: TASK-025
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-6
- **Priority**: P0
- **Complexity**: 55
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: orchestration, headless, claude-code, api

## Description

Implement headless mode integration that allows PairCoder to programmatically invoke Claude Code sessions without interactive prompts. This is the foundation for multi-agent orchestration.

## Objectives

1. Create wrapper functions for Claude Code headless invocation
2. Implement session management (create, resume, terminate)
3. Handle JSON input/output parsing
4. Support conversation continuation via session IDs
5. Error handling and retry logic

## Technical Requirements

### Claude Code Headless API

```bash
# Basic headless invocation
claude -p "query" --output-format json --no-input

# With session continuation
claude -p "follow-up" --output-format json --resume <session_id>

# With specific permission mode
claude -p "plan this feature" --permission-mode plan --output-format json
```

### Response Structure

```json
{
  "session_id": "abc123",
  "result": "...",
  "cost_usd": 0.05,
  "tokens": {
    "input": 1500,
    "output": 800
  },
  "is_error": false
}
```

### Implementation Components

1. **HeadlessSession Class**
   ```python
   class HeadlessSession:
       def __init__(self, permission_mode='auto'):
           self.session_id = None
           self.permission_mode = permission_mode
           
       def invoke(self, prompt: str) -> HeadlessResponse:
           """Send prompt, return structured response"""
           
       def resume(self, prompt: str) -> HeadlessResponse:
           """Continue existing session"""
           
       def terminate(self) -> None:
           """Clean up session"""
   ```

2. **Response Parser**
   - Parse JSON output from Claude Code
   - Extract session_id for continuation
   - Capture token usage and cost
   - Handle error responses

3. **CLI Integration**
   ```bash
   bpsai-pair invoke --prompt "..." --mode plan
   bpsai-pair invoke --prompt "..." --session <id>
   ```

## Acceptance Criteria

- [ ] Can invoke Claude Code headlessly with a prompt
- [ ] Can parse JSON response into structured object
- [ ] Can resume sessions using session_id
- [ ] Can specify permission mode (auto, plan, full)
- [ ] Errors are caught and reported cleanly
- [ ] Token/cost data captured for metrics
- [ ] Unit tests for parser and session management
- [ ] Integration test with live Claude Code

## Dependencies

- Claude Code CLI installed and authenticated
- Python 3.10+
- No external dependencies (use subprocess)

## Files to Create/Modify

- `tools/cli/src/paircoder/orchestration/__init__.py`
- `tools/cli/src/paircoder/orchestration/headless.py`
- `tools/cli/src/paircoder/orchestration/session.py`
- `tools/cli/tests/test_headless.py`

## Notes

- This is the foundation for TASK-026, TASK-027, and TASK-028
- Keep it simple - wrapper around CLI, not SDK integration
- Consider timeout handling for long operations
- Log all invocations for debugging

## References

- Claude Code documentation: https://docs.anthropic.com/en/docs/claude-code
- Headless mode: `claude --help` for current flags
