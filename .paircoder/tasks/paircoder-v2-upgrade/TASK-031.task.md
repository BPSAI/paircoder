# TASK-031: Time Tracking Integration

## Metadata
- **ID**: TASK-031
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-7
- **Priority**: P2
- **Complexity**: 35
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: time-tracking, toggl, clockify, integration

## Description

Implement integration with popular time tracking services to automatically log time spent on tasks. This enables accurate project accounting and productivity analysis.

## Objectives

1. Define time tracking provider interface
2. Implement Toggl integration
3. Implement Clockify integration (optional)
4. Auto-start/stop timers on task state changes
5. Manual override commands

## Technical Requirements

### Provider Interface

```python
from abc import ABC, abstractmethod

class TimeTrackingProvider(ABC):
    @abstractmethod
    def start_timer(self, task_id: str, description: str) -> str:
        """Start timer, return timer_id"""
        
    @abstractmethod
    def stop_timer(self, timer_id: str) -> TimerEntry:
        """Stop timer, return entry with duration"""
        
    @abstractmethod
    def get_entries(self, task_id: str) -> List[TimerEntry]:
        """Get all entries for a task"""
        
    @abstractmethod
    def get_total(self, task_id: str) -> timedelta:
        """Get total time for a task"""
```

### Configuration

```yaml
# .paircoder/config.yaml
time_tracking:
  provider: toggl              # toggl, clockify, harvest, none
  auto_start: true             # Start timer when task starts
  auto_stop: true              # Stop timer when task completes
  project_mapping:
    paircoder-v2-upgrade: 12345678  # Provider project ID
  api_key_env: TOGGL_API_KEY   # Environment variable for API key
  workspace_id: 1234567
  task_pattern: "{task_id}: {task_title}"  # Timer description format
```

### Toggl Integration

```python
class TogglProvider(TimeTrackingProvider):
    BASE_URL = "https://api.track.toggl.com/api/v9"
    
    def __init__(self, api_key: str, workspace_id: int):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.session = self._create_session()
        
    def start_timer(self, task_id: str, description: str) -> str:
        response = self.session.post(
            f"{self.BASE_URL}/workspaces/{self.workspace_id}/time_entries",
            json={
                "description": description,
                "start": datetime.utcnow().isoformat() + "Z",
                "workspace_id": self.workspace_id,
                "created_with": "paircoder"
            }
        )
        return response.json()["id"]
        
    def stop_timer(self, timer_id: str) -> TimerEntry:
        response = self.session.patch(
            f"{self.BASE_URL}/workspaces/{self.workspace_id}/time_entries/{timer_id}/stop"
        )
        data = response.json()
        return TimerEntry(
            id=data["id"],
            duration=timedelta(seconds=data["duration"]),
            description=data["description"]
        )
```

### CLI Commands

```bash
# Manual timer control
bpsai-pair timer start TASK-025
bpsai-pair timer stop
bpsai-pair timer status

# View time for task
bpsai-pair timer show TASK-025

# View time for plan/sprint
bpsai-pair timer summary --plan paircoder-v2-upgrade
bpsai-pair timer summary --sprint sprint-7

# Sync local records with provider
bpsai-pair timer sync

# Configure provider
bpsai-pair timer configure --provider toggl
```

### Auto-Timer Triggers

```python
# In task state management
class TaskManager:
    def start_task(self, task_id: str):
        task = self.load_task(task_id)
        task.status = "in-progress"
        self.save_task(task)
        
        if self.config.time_tracking.auto_start:
            timer_id = self.time_tracker.start_timer(
                task_id,
                self.config.time_tracking.task_pattern.format(
                    task_id=task_id,
                    task_title=task.title
                )
            )
            task.active_timer_id = timer_id
            self.save_task(task)
            
    def complete_task(self, task_id: str):
        task = self.load_task(task_id)
        task.status = "completed"
        
        if task.active_timer_id and self.config.time_tracking.auto_stop:
            entry = self.time_tracker.stop_timer(task.active_timer_id)
            task.time_entries.append(entry)
            task.active_timer_id = None
            
        self.save_task(task)
```

### Local Time Cache

```json
// .paircoder/history/time-entries.json
{
  "TASK-025": {
    "entries": [
      {
        "provider_id": "abc123",
        "start": "2025-01-16T10:00:00Z",
        "end": "2025-01-16T11:30:00Z",
        "duration_seconds": 5400
      }
    ],
    "total_seconds": 5400
  }
}
```

## Acceptance Criteria

- [ ] Toggl integration authenticates successfully
- [ ] Timer starts when task status → in-progress
- [ ] Timer stops when task status → completed/blocked
- [ ] Manual start/stop commands work
- [ ] Time entries cached locally for offline
- [ ] Summary reports show task/sprint/plan totals
- [ ] Graceful degradation if provider unavailable
- [ ] Unit tests with mocked API
- [ ] Integration test with real Toggl (optional)

## Dependencies

- `requests` library for API calls
- API key configured in environment
- Optional: Clockify/Harvest API access

## Files to Create/Modify

- `tools/cli/src/paircoder/integrations/__init__.py`
- `tools/cli/src/paircoder/integrations/time_tracking.py`
- `tools/cli/src/paircoder/integrations/toggl.py`
- `tools/cli/src/paircoder/integrations/clockify.py` (optional)
- `tools/cli/src/paircoder/commands/timer.py`
- `tools/cli/tests/test_time_tracking.py`

## Notes

- API key must NEVER be logged or stored in files
- Cache locally for offline resilience
- Consider: What if task spans multiple sessions?
- Consider: Pausing/resuming timers
- Toggl has rate limits - batch operations where possible

## Provider Comparison

| Feature | Toggl | Clockify | Harvest |
|---------|-------|----------|---------|
| Free tier | Yes | Yes | No |
| API | REST | REST | REST |
| Workspace support | Yes | Yes | Yes |
| Tags | Yes | Yes | Yes |
| Project mapping | Yes | Yes | Yes |

## Example Workflow

```bash
# Configure once
export TOGGL_API_KEY=xxxx
bpsai-pair timer configure --provider toggl --workspace 1234567

# Start work (auto-starts timer)
bpsai-pair task start TASK-025
# Timer started: TASK-025: Headless Mode Integration

# ... do work ...

# Complete task (auto-stops timer)
bpsai-pair task complete TASK-025
# Timer stopped: 1h 23m

# Review time
bpsai-pair timer show TASK-025
# TASK-025: Headless Mode Integration
# Total: 1h 23m
# Entries:
#   - Jan 16, 10:00-11:23 (1h 23m)
```
