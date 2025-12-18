---
id: TASK-093
title: Git checkpoint/rollback
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P0
complexity: 35
status: done
sprint: sprint-15
tags:
- security
- git
- rollback
- checkpoint
---

# Objective

Implement automatic git checkpointing before changes and rollback capability when things break.

# Implementation Plan

1. Create GitCheckpoint class:
   ```python
   class GitCheckpoint:
       def __init__(self, repo_path: Path):
           self.repo = git.Repo(repo_path)
           self.checkpoints: list[str] = []

       def create_checkpoint(self, message: str = None) -> str:
           """Create checkpoint before risky operation."""
           # Stash any uncommitted changes
           stash_ref = self.repo.git.stash("push", "-m", f"checkpoint-{timestamp}")

           # Create lightweight tag for current HEAD
           tag_name = f"paircoder-checkpoint-{timestamp}"
           self.repo.create_tag(tag_name)
           self.checkpoints.append(tag_name)

           return tag_name

       def rollback_to(self, checkpoint: str):
           """Rollback to checkpoint, discarding all changes."""
           self.repo.git.reset("--hard", checkpoint)
           # Pop stash if exists
           self.repo.git.stash("pop")
   ```

2. Create automatic checkpoint triggers:
   - Before any file modification
   - Before running tests (in case they modify state)
   - Before git operations (commit, merge, rebase)

3. Implement rollback CLI:
   ```bash
   bpsai-pair rollback              # List checkpoints
   bpsai-pair rollback --last       # Rollback to last checkpoint
   bpsai-pair rollback --to <tag>   # Rollback to specific checkpoint
   bpsai-pair rollback --preview    # Show what would be reverted
   ```

4. Add checkpoint retention policy:
   - Keep last N checkpoints
   - Auto-cleanup old checkpoints
   - Never delete checkpoints with uncommitted work

# Acceptance Criteria

- [ ] Checkpoints created automatically before changes
- [ ] Rollback restores exact previous state
- [ ] Uncommitted changes preserved in stash
- [ ] CLI shows available checkpoints
- [ ] Preview mode shows what would be reverted
- [ ] Old checkpoints cleaned up automatically
- [ ] Works with both clean and dirty working directory

# Files to Create/Modify

- `tools/cli/bpsai_pair/security/checkpoint.py` (new)
- `tools/cli/bpsai_pair/security/cli_commands.py` (new)
- `tests/test_security_checkpoint.py` (new)