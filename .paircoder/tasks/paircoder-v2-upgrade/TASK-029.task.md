# TASK-029: Task Lifecycle Management

## Metadata
- **ID**: TASK-029
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-7
- **Priority**: P1
- **Complexity**: 45
- **Status**: done
- **Created**: 2025-01-16
- **Updated**: 2025-01-16
- **Tags**: tasks, lifecycle, archive, retention, cleanup, changelog

## Description

Implement task lifecycle management to prevent task file bloat. This includes automatic archival of completed tasks, retention policies, cleanup utilities, and changelog generation.

## Objectives

1. Define task lifecycle states
2. Implement automatic archival after PR merge
3. Create retention policies (configurable)
4. Build cleanup utilities for manual management
5. Support task restoration from archive
6. **Generate changelog entries from archived tasks**

## Initial Validation Test Case

**Upon implementation, immediately validate by archiving Sprint 1-6 tasks:**

- Archive TASK-001 through TASK-028 (completed tasks)
- Verify archive structure and manifest
- Verify changelog is updated with Sprint 1-6 accomplishments
- Keep TASK-029 through TASK-032 active (Sprint 7)
- Document `paircoder-v2-upgrade` plan as transitioning to completion
- Next plan will be `paircoder-v2.2-features`

This provides real-world validation with actual project history.

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
│       ├── TASK-029.task.md      # Active
│       └── TASK-030.task.md      # Active
├── history/
│   └── archived-tasks/
│       └── {plan-slug}/
│           ├── manifest.json         # Archive index
│           ├── TASK-001.task.md.gz   # Compressed
│           └── TASK-002.task.md.gz
└── CHANGELOG.md                      # Updated on archive
```

### Archive Manifest

```json
{
  "plan": "paircoder-v2-upgrade",
  "archived_at": "2025-01-16T10:00:00Z",
  "tasks": [
    {
      "id": "TASK-001",
      "title": "Create v2 directory structure",
      "sprint": "sprint-1",
      "status": "completed",
      "completed_at": "2025-01-10T15:00:00Z",
      "archived_at": "2025-01-16T10:00:00Z",
      "pr": "#42",
      "changelog_entry": "Established v2 project structure with .paircoder/ directory"
    }
  ],
  "changelog_generated": true
}
```

### Changelog Integration

```markdown
# Changelog

All notable changes to this project are documented in this file.

## [v2.1.0] - 2025-01-16

### Added
- Multi-agent orchestration with headless mode (TASK-025)
- Agent handoff protocol for cross-agent workflows (TASK-026)
- Codex CLI adapter with flow parsing (TASK-027)
- Orchestrator service for intelligent agent routing (TASK-028)

### Changed
- Migrated to dual-layer architecture (AGENTS.md + .claude/) (TASK-020, TASK-021)
- Converted flows to Claude Code skills (TASK-022)

### Infrastructure
- Custom subagents for planning and review (TASK-023)
- Auto context-sync hooks (TASK-024)

## [v2.0.0] - 2025-01-10

### Added
- Initial v2 directory structure (TASK-001)
- Planning module implementation (TASK-002)
- Flow parser and integration (TASK-003)
...
```

### Changelog Generator

```python
class ChangelogGenerator:
    CATEGORIES = {
        'feature': 'Added',
        'enhancement': 'Changed', 
        'fix': 'Fixed',
        'infrastructure': 'Infrastructure',
        'docs': 'Documentation',
        'deprecation': 'Deprecated',
        'removal': 'Removed',
        'security': 'Security'
    }
    
    def __init__(self, changelog_path: Path):
        self.changelog_path = changelog_path
        
    def generate_entry(self, tasks: List[ArchivedTask], version: str) -> str:
        """Generate changelog section from archived tasks"""
        categorized = self._categorize_tasks(tasks)
        return self._format_section(version, categorized)
        
    def _categorize_tasks(self, tasks: List[ArchivedTask]) -> dict:
        """Group tasks by changelog category based on tags"""
        categories = defaultdict(list)
        for task in tasks:
            category = self._determine_category(task)
            entry = task.changelog_entry or task.title
            categories[category].append(f"- {entry} ({task.id})")
        return categories
        
    def _determine_category(self, task: ArchivedTask) -> str:
        """Determine changelog category from task tags"""
        tag_mapping = {
            'feature': 'Added',
            'enhancement': 'Changed',
            'bugfix': 'Fixed',
            'fix': 'Fixed',
            'infrastructure': 'Infrastructure',
            'docs': 'Documentation'
        }
        for tag in task.tags:
            if tag in tag_mapping:
                return tag_mapping[tag]
        return 'Changed'  # Default
        
    def update_changelog(self, tasks: List[ArchivedTask], version: str) -> None:
        """Prepend new version section to changelog"""
        new_section = self.generate_entry(tasks, version)
        existing = self.changelog_path.read_text() if self.changelog_path.exists() else ""
        
        # Insert after header
        if existing.startswith("# Changelog"):
            header_end = existing.find("\n\n") + 2
            updated = existing[:header_end] + new_section + "\n" + existing[header_end:]
        else:
            updated = "# Changelog\n\n" + new_section + "\n" + existing
            
        self.changelog_path.write_text(updated)
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
  changelog:
    enabled: true
    path: CHANGELOG.md
    auto_version: true         # Auto-increment version on archive
    version_pattern: "v{major}.{minor}.{patch}"
```

### CLI Commands

```bash
# Archive completed tasks manually
bpsai-pair task archive --completed

# Archive specific task
bpsai-pair task archive TASK-025

# Archive sprint (with changelog)
bpsai-pair task archive --sprint sprint-6 --version v2.1.0

# Archive without changelog update
bpsai-pair task archive --completed --no-changelog

# List archived tasks
bpsai-pair task list --archived

# Restore task from archive
bpsai-pair task restore TASK-025

# Cleanup old archives per retention policy
bpsai-pair task cleanup --dry-run
bpsai-pair task cleanup --confirm

# Show task lifecycle status
bpsai-pair task lifecycle TASK-025

# Preview changelog entry
bpsai-pair task changelog-preview --sprint sprint-6
```

### Archival Logic

```python
class TaskArchiver:
    def __init__(self, config: TaskLifecycleConfig, changelog: ChangelogGenerator):
        self.config = config
        self.changelog = changelog
        
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
        
    def archive_batch(self, tasks: List[Task], version: str = None) -> ArchiveResult:
        """Archive multiple tasks with single changelog entry"""
        archived = []
        for task in tasks:
            path = self.archive(task)
            archived.append(task)
            
        if self.config.changelog.enabled and archived:
            self.changelog.update_changelog(archived, version)
            
        return ArchiveResult(archived=archived, changelog_updated=True)
        
    def restore(self, task_id: str) -> Task:
        """Restore task from archive to active"""
        
    def cleanup(self, dry_run: bool = True) -> List[str]:
        """Remove tasks past retention period"""
```

### Plan Transition

When archiving completes a plan:

```python
def complete_plan(plan_slug: str, next_plan: str = None) -> PlanCompletion:
    """Mark plan as complete and optionally create successor"""
    plan = load_plan(plan_slug)
    
    # Verify all tasks archived or cancelled
    active_tasks = get_active_tasks(plan_slug)
    if active_tasks:
        raise PlanNotCompleteError(f"Active tasks remain: {active_tasks}")
    
    plan.status = "completed"
    plan.completed_at = datetime.now()
    plan.successor = next_plan
    save_plan(plan)
    
    if next_plan:
        create_plan(next_plan, predecessor=plan_slug)
        
    return PlanCompletion(plan=plan_slug, successor=next_plan)
```

```bash
# Complete plan and create successor
bpsai-pair plan complete paircoder-v2-upgrade --next paircoder-v2.2-features
```

## Acceptance Criteria

- [ ] Tasks can be manually archived
- [ ] Archived tasks are compressed (.gz)
- [ ] Archive manifest tracks all archived tasks
- [ ] **Changelog updated on archive with categorized entries**
- [ ] **Changelog categories derived from task tags**
- [ ] Retention policy enforced by cleanup command
- [ ] Archived tasks can be restored
- [ ] `--dry-run` shows what would be archived/cleaned
- [ ] Hook triggers archive on PR merge (if configured)
- [ ] **Validate by archiving TASK-001 through TASK-028**
- [ ] **Plan completion workflow creates successor plan**
- [ ] Unit tests for archival logic
- [ ] Unit tests for changelog generation
- [ ] Integration test for full lifecycle

## Dependencies

- Existing task management system
- gzip compression (stdlib)
- Optional: GitHub CLI for PR detection

## Files to Create/Modify

- `tools/cli/src/paircoder/tasks/lifecycle.py`
- `tools/cli/src/paircoder/tasks/archiver.py`
- `tools/cli/src/paircoder/tasks/changelog.py`
- `tools/cli/src/paircoder/commands/task.py` (add subcommands)
- `tools/cli/src/paircoder/commands/plan.py` (add complete command)
- `tools/cli/tests/test_lifecycle.py`
- `tools/cli/tests/test_changelog.py`
- `.paircoder/config.yaml` (add lifecycle section)
- `CHANGELOG.md` (create/update)

## Notes

- Keep archive format simple - just gzipped markdown
- Manifest enables quick listing without decompressing
- Changelog entries should be human-readable, not just task titles
- Consider: Task can have explicit `changelog_entry` field for custom text
- Restoration should be rare - warn user about state conflicts
- Plan naming convention: `project-v{major}.{minor}-{scope}`

## Example Workflow

```bash
# Sprint 7 starts - archive completed sprints
bpsai-pair task archive --sprint sprint-1,sprint-2,sprint-3,sprint-4,sprint-5,sprint-6 --version v2.1.0

# Output:
# Archiving 28 tasks from 6 sprints...
# ✓ TASK-001: Create v2 directory structure
# ✓ TASK-002: Planning module implementation
# ...
# ✓ TASK-028: Orchestrator service
# 
# Updated CHANGELOG.md with v2.1.0 release notes
# Archived to: .paircoder/history/archived-tasks/paircoder-v2-upgrade/

# Complete Sprint 7
bpsai-pair task archive --sprint sprint-7 --version v2.1.1

# Complete plan and start next
bpsai-pair plan complete paircoder-v2-upgrade --next paircoder-v2.2-features

# Output:
# ✓ Plan 'paircoder-v2-upgrade' marked complete
# ✓ Created successor plan 'paircoder-v2.2-features'
# 
# Ready for next phase of development!
```

## Changelog Entry Format

Tasks should include optional `changelog_entry` in metadata for custom changelog text:

```yaml
# In task file metadata
changelog_entry: "Added intelligent agent routing with cost optimization"
```

If not specified, the task title is used. Tags determine category:
- `feature` → Added
- `enhancement` → Changed
- `fix`, `bugfix` → Fixed
- `infrastructure` → Infrastructure
- `docs` → Documentation
- `security` → Security
