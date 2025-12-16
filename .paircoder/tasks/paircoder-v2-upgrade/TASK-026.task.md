# TASK-026: Agent Handoff Protocol

## Metadata
- **ID**: TASK-026
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-6
- **Priority**: P1
- **Complexity**: 50
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: orchestration, handoff, multi-agent, pack

## Description

Implement the agent handoff protocol that packages context for transfer between different AI coding agents (Claude Code, Codex CLI, Cursor, etc.). This enables seamless task delegation across agent boundaries.

## Objectives

1. Define handoff package format (context bundle)
2. Implement `bpsai-pair pack` command for creating handoffs
3. Implement `bpsai-pair unpack` command for receiving handoffs
4. Support agent-specific formatting (Claude, Codex, generic)
5. Include relevant context without overwhelming token limits

## Technical Requirements

### Handoff Package Structure

```
handoff-TASK-XXX-{agent}.tgz
├── HANDOFF.md           # Instructions for receiving agent
├── context/
│   ├── task.md          # Current task details
│   ├── state.md         # Project state snapshot
│   └── relevant/        # Only files relevant to task
│       ├── file1.py
│       └── file2.py
├── history/
│   └── conversation.md  # Summary of work done so far
└── metadata.json        # Machine-readable metadata
```

### HANDOFF.md Template

```markdown
# Agent Handoff: {TASK-ID}

## Task
{task description}

## Current State
{what's been done, what's remaining}

## Key Files
{list of files included and why}

## Instructions
{specific instructions for this agent}

## Constraints
- Token budget: {estimate}
- Time budget: {if applicable}
- Scope: {what NOT to do}
```

### CLI Commands

```bash
# Pack context for specific agent
bpsai-pair pack --task TASK-025 --for-agent codex --out handoff.tgz

# Pack with custom context
bpsai-pair pack --task TASK-025 --include src/auth/ --exclude tests/

# Unpack received handoff
bpsai-pair unpack handoff.tgz --into .paircoder/incoming/

# List pending handoffs
bpsai-pair handoffs list
```

### Agent-Specific Formatting

| Agent | Format | Notes |
|-------|--------|-------|
| claude | Include CLAUDE.md pointer | Reference skills |
| codex | AGENTS.md compatible | Keep under 32KB |
| cursor | .cursorrules format | Include rules file |
| generic | Plain markdown | Maximum compatibility |

### Metadata Schema

```json
{
  "version": "1.0",
  "task_id": "TASK-025",
  "source_agent": "claude-code",
  "target_agent": "codex",
  "created_at": "2025-01-16T10:00:00Z",
  "token_estimate": 5000,
  "files_included": ["src/auth.py", "tests/test_auth.py"],
  "conversation_summary": "Implemented basic auth, needs OAuth integration"
}
```

## Acceptance Criteria

- [ ] `pack` command creates valid .tgz with correct structure
- [ ] `unpack` command extracts and validates handoff
- [ ] HANDOFF.md generated with task-specific instructions
- [ ] Agent-specific formatting applied correctly
- [ ] Relevant files auto-detected from task context
- [ ] Token estimate included in metadata
- [ ] Conversation history summarized (not raw dump)
- [ ] Unit tests for pack/unpack
- [ ] Integration test: Claude → Codex handoff

## Dependencies

- TASK-025 (headless mode for conversation capture)
- Existing task management system
- File detection via git diff or task references

## Files to Create/Modify

- `tools/cli/src/paircoder/orchestration/handoff.py`
- `tools/cli/src/paircoder/commands/pack.py`
- `tools/cli/src/paircoder/commands/unpack.py`
- `tools/cli/src/paircoder/templates/HANDOFF.md.j2`
- `tools/cli/tests/test_handoff.py`

## Notes

- Keep handoffs small - receiving agent has limited context
- Summarize conversations, don't include raw transcripts
- Consider security: no credentials in handoffs
- Auto-detect relevant files from git status + task references

## Example Usage

```bash
# After working on auth feature with Claude
bpsai-pair pack --task TASK-025 --for-agent codex

# Output: handoff-TASK-025-codex.tgz (4.2KB, ~3000 tokens)

# Codex receives and unpacks
bpsai-pair unpack handoff-TASK-025-codex.tgz
codex "Continue work on TASK-025 per the handoff instructions"
```
