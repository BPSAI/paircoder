# TASK-029: Task Lifecycle Management

## Metadata
- **ID**: TASK-029
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-7
- **Priority**: P1
- **Complexity**: 40
- **Status**: pending
- **Created**: 2025-01-16
- **Tags**: tasks, lifecycle, archive, retention, cleanup

## Description

Implement task lifecycle management to prevent task file bloat. This includes automatic archival of completed tasks, retention policies, and cleanup utilities.

## Objectives

1. Define task lifecycle states
2. Implement automatic archival after PR merge
3. Create retention policies (configurable)
4. Build cleanup utilities for manual management
5. Support task restoration from archive

## Technical Requirements

### Task Lifecycle States

```
pending → in-progress → review → completed → archived
                ↓
              blocked
                ↓
            cancelled → archived
```

### Archive Structure

```
.paircoder/
├── tasks/
│   └── {plan-slug}/
│       ├── TASK-025.task.md      # Active
│       └── TASK-026.task.md      # Active
└── history/
    └── archived-tasks/
        └── {plan-slug}/
            ├── TASK-001.task.md.gz   # Compressed
            ├── TASK-002.task.md.gz
            └── manifest.json         # Archive index
```

### Archive Manifest

```json
{
  "plan": "paircoder-v2-upgrade",
  "archived_at": "2025-01-16T10:00:00Z",
  "tasks": [
    {
      "id": "TASK-001",
      "title": "Create v2 structure",
      "status": "completed",
      "completed_at": "2025-01-10T15:00:00Z",
      "archived_at": "2025-01-16T10:00:00Z",
      "pr": "#42"
    }
  ]
}
```

### Retention Policy Configuration

```yaml
# .paircoder/config.yaml
task_lifecycle:
  auto_archive:
    enabled: true
    trigger: pr_merge          # or: status_completed, manual
    delay_days: 7              # Keep completed tasks visible for 7 days
  retention:
    completed: 90d             # Keep archived completed for 90 days
    cancelled: 30d             # Keep archived cancelled for 30 days
  compression: gzip            # gzip, none
```

### CLI Commands

```bash
# Archive completed tasks manually
bpsai-pair task archive --completed

# Archive specific task
bpsai-pair task archive TASK-025

# List archived tasks
bpsai-pair task list --archived

# Restore task from archive
bpsai-pair task restore TASK-025

# Cleanup old archives per retention policy
bpsai-pair task cleanup --dry-run
bpsai-pair task cleanup --confirm

# Show task lifecycle status
bpsai-pair task lifecycle TASK-025
```

### Archival Logic

```python
class TaskArchiver:
    def __init__(self, config: TaskLifecycleConfig):
        self.config = config
        
    def should_archive(self, task: Task) -> bool:
        """Check if task meets archive criteria"""
        if task.status not in ['completed', 'cancelled']:
            return False
        if self.config.trigger == 'pr_merge':
            return task.pr_merged
        if self.config.trigger == 'status_completed':
            age = datetime.now() - task.completed_at
            return age.days >= self.config.delay_days
        return False
        
    def archive(self, task: Task) -> Path:
        """Move task to archive, compress, update manifest"""
        
    def restore(self, task_id: str) -> Task:
        """Restore task from archive to active"""
        
    def cleanup(self, dry_run: bool = True) -> List[str]:
        """Remove tasks past retention period"""
```

### Hook Integration

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "bash",
        "pattern": "gh pr merge",
        "command": "bpsai-pair task archive --trigger pr-merge"
      }
    ]
  }
}
```

## Acceptance Criteria

- [ ] Tasks can be manually archived
- [ ] Archived tasks are compressed (.gz)
- [ ] Archive manifest tracks all archived tasks
- [ ] Retention policy enforced by cleanup command
- [ ] Archived tasks can be restored
- [ ] `--dry-run` shows what would be archived/cleaned
- [ ] Hook triggers archive on PR merge (if configured)
- [ ] Unit tests for archival logic
- [ ] Integration test for full lifecycle

## Dependencies

- Existing task management system
- gzip compression (stdlib)
- Optional: GitHub CLI for PR detection

## Files to Create/Modify

- `tools/cli/src/paircoder/tasks/lifecycle.py`
- `tools/cli/src/paircoder/tasks/archiver.py`
- `tools/cli/src/paircoder/commands/task.py` (add subcommands)
- `tools/cli/tests/test_lifecycle.py`
- `.paircoder/config.yaml` (add lifecycle section)

## Notes

- Keep archive format simple - just gzipped markdown
- Manifest enables quick listing without decompressing
- Consider: What happens to metrics when task archived?
- Restoration should be rare - warn user about state conflicts

## Example Workflow

```bash
# Work on task
bpsai-pair task start TASK-025
# ... do work ...
bpsai-pair task complete TASK-025

# After PR merged (7 days later, per config)
bpsai-pair task archive --completed
# → Archived TASK-025 to history/archived-tasks/

# Need to reference old task?
bpsai-pair task list --archived --plan paircoder-v2-upgrade
bpsai-pair task show TASK-025 --archived

# Monthly cleanup
bpsai-pair task cleanup --confirm
# → Removed 12 tasks past retention period
```
