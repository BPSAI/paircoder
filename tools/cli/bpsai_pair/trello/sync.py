"""
Trello sync module for syncing tasks to Trello cards with custom fields.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
import re

from .client import TrelloService, EffortMapping
from .templates import CardDescriptionTemplate, CardDescriptionData, should_preserve_description

logger = logging.getLogger(__name__)


# BPS Label color mapping
BPS_LABELS = {
    "Frontend": "green",
    "Backend": "blue",
    "Worker/Function": "purple",
    "Deployment": "red",
    "Bug/Issue": "orange",
    "Security/Admin": "yellow",
    "Documentation": "sky",
    "AI/ML": "black",
}

# Keywords to infer stack from task title/tags
STACK_KEYWORDS = {
    "Frontend": ["frontend", "ui", "react", "vue", "angular", "css", "html", "component"],
    "Backend": ["backend", "api", "flask", "fastapi", "django", "server", "endpoint"],
    "Worker/Function": ["worker", "function", "lambda", "celery", "task", "job", "queue"],
    "Deployment": ["deploy", "docker", "k8s", "kubernetes", "ci", "cd", "pipeline"],
    "Bug/Issue": ["bug", "fix", "issue", "error", "crash"],
    "Security/Admin": ["security", "auth", "admin", "permission", "role", "soc2"],
    "Documentation": ["doc", "readme", "guide", "tutorial", "comment"],
    "AI/ML": ["ai", "ml", "model", "llm", "claude", "gpt", "embedding"],
}


@dataclass
class TaskSyncConfig:
    """Configuration for syncing tasks to Trello."""
    # Custom field mappings
    project_field: str = "Project"
    stack_field: str = "Stack"
    status_field: str = "Status"
    effort_field: str = "Effort"
    deployment_tag_field: str = "Deployment Tag"

    # Effort mapping ranges
    effort_mapping: EffortMapping = field(default_factory=EffortMapping)

    # Whether to create missing labels
    create_missing_labels: bool = True

    # Default list for new cards
    default_list: str = "Backlog"

    # Card description template (None uses default BPS template)
    card_template: Optional[str] = None

    # Whether to preserve manually edited card descriptions
    preserve_manual_edits: bool = True

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TaskSyncConfig":
        """Create TaskSyncConfig from a config dictionary.

        Expected config structure (from config.yaml):
        ```yaml
        trello:
          sync:
            custom_fields:
              project: "Project"
              stack: "Stack"
              status: "Status"
              effort: "Effort"
            effort_mapping:
              S: [0, 25]
              M: [26, 50]
              L: [51, 100]
            default_list: "Backlog"
            create_missing_labels: true
            preserve_manual_edits: true
        ```

        Args:
            config: Configuration dictionary (usually from config.yaml's trello.sync section)

        Returns:
            Configured TaskSyncConfig instance
        """
        sync_config = config.get("sync", {})
        custom_fields = sync_config.get("custom_fields", {})

        # Parse effort mapping if provided
        effort_config = sync_config.get("effort_mapping", {})
        if effort_config:
            effort_mapping = EffortMapping(
                small=(effort_config.get("S", [0, 25])[0], effort_config.get("S", [0, 25])[1]),
                medium=(effort_config.get("M", [26, 50])[0], effort_config.get("M", [26, 50])[1]),
                large=(effort_config.get("L", [51, 100])[0], effort_config.get("L", [51, 100])[1]),
            )
        else:
            effort_mapping = EffortMapping()

        return cls(
            project_field=custom_fields.get("project", "Project"),
            stack_field=custom_fields.get("stack", "Stack"),
            status_field=custom_fields.get("status", "Status"),
            effort_field=custom_fields.get("effort", "Effort"),
            deployment_tag_field=custom_fields.get("deployment_tag", "Deployment Tag"),
            effort_mapping=effort_mapping,
            create_missing_labels=sync_config.get("create_missing_labels", True),
            default_list=sync_config.get("default_list", "Backlog"),
            card_template=sync_config.get("card_template"),
            preserve_manual_edits=sync_config.get("preserve_manual_edits", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to config dictionary format.

        Returns:
            Dictionary suitable for saving to config.yaml
        """
        return {
            "sync": {
                "custom_fields": {
                    "project": self.project_field,
                    "stack": self.stack_field,
                    "status": self.status_field,
                    "effort": self.effort_field,
                    "deployment_tag": self.deployment_tag_field,
                },
                "effort_mapping": {
                    "S": list(self.effort_mapping.small),
                    "M": list(self.effort_mapping.medium),
                    "L": list(self.effort_mapping.large),
                },
                "default_list": self.default_list,
                "create_missing_labels": self.create_missing_labels,
                "preserve_manual_edits": self.preserve_manual_edits,
            }
        }


@dataclass
class TaskData:
    """Task data for syncing to Trello."""
    id: str
    title: str
    description: str = ""
    status: str = "pending"
    priority: str = "P1"
    complexity: int = 50
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    plan_title: Optional[str] = None

    @classmethod
    def from_task(cls, task: Any) -> "TaskData":
        """Create TaskData from a Task object."""
        # Extract acceptance criteria from task body if present
        acceptance_criteria = []
        if hasattr(task, 'body') and task.body:
            # Look for checklist items in body
            for line in task.body.split('\n'):
                line = line.strip()
                if line.startswith('- [ ]') or line.startswith('- [x]'):
                    # Remove checkbox prefix
                    item = re.sub(r'^- \[[ x]\]\s*', '', line)
                    acceptance_criteria.append(item)

        return cls(
            id=task.id,
            title=task.title,
            description=getattr(task, 'body', '') or '',
            status=task.status,
            priority=getattr(task, 'priority', 'P1'),
            complexity=getattr(task, 'complexity', 50),
            tags=getattr(task, 'tags', []) or [],
            acceptance_criteria=acceptance_criteria,
            plan_title=getattr(task, 'plan', None),
        )


class TrelloSyncManager:
    """Manages syncing tasks to Trello with custom fields."""

    def __init__(self, service: TrelloService, config: Optional[TaskSyncConfig] = None):
        """Initialize sync manager.

        Args:
            service: Configured TrelloService
            config: Sync configuration (uses defaults if not provided)
        """
        self.service = service
        self.config = config or TaskSyncConfig()

    def infer_stack(self, task: TaskData) -> Optional[str]:
        """Infer stack/label from task title and tags.

        Args:
            task: Task data

        Returns:
            Stack name or None if cannot infer
        """
        # Check tags first
        for tag in task.tags:
            tag_lower = tag.lower()
            for stack, keywords in STACK_KEYWORDS.items():
                if tag_lower in keywords or any(kw in tag_lower for kw in keywords):
                    return stack

        # Check title
        title_lower = task.title.lower()
        for stack, keywords in STACK_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                return stack

        return None

    def build_card_description(self, task: TaskData) -> str:
        """Build BPS-formatted card description.

        Args:
            task: Task data

        Returns:
            Formatted description string
        """
        # Use the CardDescriptionTemplate for proper BPS formatting
        return CardDescriptionTemplate.from_task_data(
            task,
            template=self.config.card_template
        )

    def should_update_description(self, existing_desc: str) -> bool:
        """Check if we should update an existing card description.

        Args:
            existing_desc: Current card description

        Returns:
            True if we should update, False to preserve manual edits
        """
        if not self.config.preserve_manual_edits:
            return True

        return not should_preserve_description(existing_desc)

    def ensure_bps_labels(self) -> Dict[str, bool]:
        """Ensure all BPS labels exist on the board.

        Returns:
            Dict mapping label names to creation success
        """
        results = {}

        if not self.config.create_missing_labels:
            return results

        for label_name, color in BPS_LABELS.items():
            label = self.service.ensure_label_exists(label_name, color)
            results[label_name] = label is not None

        return results

    def sync_task_to_card(
        self,
        task: TaskData,
        list_name: Optional[str] = None,
        update_existing: bool = True
    ) -> Optional[Any]:
        """Sync a task to a Trello card.

        Args:
            task: Task data to sync
            list_name: Target list name (uses config default if not provided)
            update_existing: Whether to update existing cards or skip

        Returns:
            Card object or None if failed
        """
        target_list = list_name or self.config.default_list

        # Check if card already exists
        existing_card, existing_list = self.service.find_card_with_prefix(task.id)

        if existing_card:
            if not update_existing:
                logger.info(f"Card for {task.id} already exists, skipping")
                return existing_card

            # Update existing card
            return self._update_card(existing_card, task)
        else:
            # Create new card
            return self._create_card(task, target_list)

    def _create_card(self, task: TaskData, list_name: str) -> Optional[Any]:
        """Create a new Trello card for a task.

        Args:
            task: Task data
            list_name: Target list name

        Returns:
            Created card or None
        """
        # Build card name with task ID prefix
        card_name = f"[{task.id}] {task.title}"
        description = self.build_card_description(task)

        # Build custom fields
        custom_fields = {}

        # Project field
        if task.plan_title:
            custom_fields[self.config.project_field] = task.plan_title

        # Stack field (inferred)
        stack = self.infer_stack(task)
        if stack:
            custom_fields[self.config.stack_field] = stack

        # Status field
        custom_fields[self.config.status_field] = task.status.replace('_', ' ').title()

        # Create card
        card = self.service.create_card_with_custom_fields(
            list_name=list_name,
            name=card_name,
            desc=description,
            custom_fields=custom_fields
        )

        if not card:
            return None

        # Set effort field (separate because it uses complexity mapping)
        self.service.set_effort_field(card, task.complexity, self.config.effort_field)

        # Add labels
        stack = self.infer_stack(task)
        if stack:
            self.service.add_label_to_card(card, stack)

        # Add labels from tags
        for tag in task.tags:
            tag_title = tag.title()
            if tag_title in BPS_LABELS:
                self.service.add_label_to_card(card, tag_title)

        logger.info(f"Created card for {task.id}: {card_name}")
        return card

    def _update_card(self, card: Any, task: TaskData) -> Any:
        """Update an existing card with task data.

        Args:
            card: Existing Trello card
            task: Task data

        Returns:
            Updated card
        """
        # Check if we should update the description or preserve manual edits
        existing_desc = getattr(card, 'description', '') or ''
        if self.should_update_description(existing_desc):
            description = self.build_card_description(task)
            card.set_description(description)
        else:
            logger.info(f"Preserving manual edits for {task.id}")

        # Update custom fields
        custom_fields = {}

        if task.plan_title:
            custom_fields[self.config.project_field] = task.plan_title

        stack = self.infer_stack(task)
        if stack:
            custom_fields[self.config.stack_field] = stack

        custom_fields[self.config.status_field] = task.status.replace('_', ' ').title()

        self.service.set_card_custom_fields(card, custom_fields)
        self.service.set_effort_field(card, task.complexity, self.config.effort_field)

        # Add labels (stack-based and tag-based)
        if stack:
            self.service.add_label_to_card(card, stack)

        for tag in task.tags:
            tag_title = tag.title()
            if tag_title in BPS_LABELS:
                self.service.add_label_to_card(card, tag_title)

        logger.info(f"Updated card for {task.id}")
        return card

    def sync_tasks(
        self,
        tasks: List[TaskData],
        list_name: Optional[str] = None,
        update_existing: bool = True
    ) -> Dict[str, Optional[Any]]:
        """Sync multiple tasks to Trello cards.

        Args:
            tasks: List of task data
            list_name: Target list name
            update_existing: Whether to update existing cards

        Returns:
            Dict mapping task IDs to cards (or None if failed)
        """
        # Ensure BPS labels exist
        self.ensure_bps_labels()

        results = {}
        for task in tasks:
            card = self.sync_task_to_card(task, list_name, update_existing)
            results[task.id] = card

        return results


def create_sync_manager(
    api_key: str,
    token: str,
    board_id: str,
    config: Optional[TaskSyncConfig] = None
) -> TrelloSyncManager:
    """Create a configured TrelloSyncManager.

    Args:
        api_key: Trello API key
        token: Trello API token
        board_id: Board ID to sync to
        config: Sync configuration

    Returns:
        Configured TrelloSyncManager
    """
    service = TrelloService(api_key, token)
    service.set_board(board_id)

    return TrelloSyncManager(service, config)


# List name to status mapping for reverse sync
LIST_TO_STATUS = {
    "Intake / Backlog": "pending",
    "Backlog": "pending",
    "Planned / Ready": "pending",
    "Ready": "pending",
    "In Progress": "in_progress",
    "Review / Testing": "in_progress",
    "In Review": "in_progress",
    "Deployed / Done": "done",
    "Done": "done",
    "Issues / Tech Debt": "blocked",
    "Blocked": "blocked",
}


@dataclass
class SyncConflict:
    """Represents a sync conflict between Trello and local."""
    task_id: str
    field: str
    local_value: Any
    trello_value: Any
    resolution: str = "trello_wins"  # or "local_wins", "skip"


@dataclass
class SyncResult:
    """Result of a sync operation."""
    task_id: str
    action: str  # "updated", "skipped", "conflict", "error"
    changes: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[SyncConflict] = field(default_factory=list)
    error: Optional[str] = None


class TrelloToLocalSync:
    """Syncs changes from Trello back to local task files."""

    def __init__(self, service: TrelloService, tasks_dir: Path):
        """Initialize the reverse sync manager.

        Args:
            service: TrelloService instance with board set
            tasks_dir: Path to .paircoder/tasks directory
        """
        self.service = service
        self.tasks_dir = tasks_dir
        self._task_parser = None

    @property
    def task_parser(self):
        """Lazy load TaskParser."""
        if self._task_parser is None:
            from ..planning.parser import TaskParser
            self._task_parser = TaskParser(self.tasks_dir)
        return self._task_parser

    def extract_task_id(self, card_name: str) -> Optional[str]:
        """Extract task ID from card name like '[TASK-066] Title'.

        Args:
            card_name: Card name with potential task ID prefix

        Returns:
            Task ID or None if not found
        """
        if card_name.startswith("[") and "]" in card_name:
            return card_name[1:card_name.index("]")]
        return None

    def get_list_status(self, list_name: str) -> Optional[str]:
        """Map Trello list name to task status.

        Args:
            list_name: Trello list name

        Returns:
            Task status string or None if no mapping
        """
        return LIST_TO_STATUS.get(list_name)

    def sync_card_to_task(self, card: Any, detect_conflicts: bool = True) -> SyncResult:
        """Sync a single Trello card back to local task.

        Args:
            card: Trello card object
            detect_conflicts: Whether to detect and report conflicts

        Returns:
            SyncResult with details of the sync operation
        """
        card_name = card.name
        task_id = self.extract_task_id(card_name)

        if not task_id:
            return SyncResult(
                task_id="unknown",
                action="skipped",
                error=f"Could not extract task ID from: {card_name}"
            )

        # Load local task
        task = self.task_parser.get_task_by_id(task_id)
        if not task:
            return SyncResult(
                task_id=task_id,
                action="skipped",
                error=f"Task not found locally: {task_id}"
            )

        changes = {}
        conflicts = []

        # Get card's current list
        list_name = card.get_list().name if hasattr(card, 'get_list') else None
        if list_name:
            new_status = self.get_list_status(list_name)
            if new_status:
                old_status = task.status.value if hasattr(task.status, 'value') else str(task.status)
                if old_status != new_status:
                    if detect_conflicts:
                        conflicts.append(SyncConflict(
                            task_id=task_id,
                            field="status",
                            local_value=old_status,
                            trello_value=new_status,
                            resolution="trello_wins"
                        ))
                    changes["status"] = {"from": old_status, "to": new_status}

                    # Apply the change (Trello wins for status)
                    from ..planning.models import TaskStatus
                    task.status = TaskStatus(new_status)

        # Check due date if present
        if hasattr(card, 'due_date') and card.due_date:
            card_due = card.due_date
            task_due = getattr(task, 'due_date', None)
            if card_due != task_due:
                changes["due_date"] = {"from": task_due, "to": card_due}
                if hasattr(task, 'due_date'):
                    task.due_date = card_due

        # Save task if there were changes
        if changes:
            try:
                self.task_parser.save(task)
                return SyncResult(
                    task_id=task_id,
                    action="updated",
                    changes=changes,
                    conflicts=conflicts
                )
            except Exception as e:
                return SyncResult(
                    task_id=task_id,
                    action="error",
                    error=str(e)
                )

        return SyncResult(
            task_id=task_id,
            action="skipped",
            changes={}
        )

    def sync_all_cards(self, list_filter: Optional[List[str]] = None) -> List[SyncResult]:
        """Sync all cards from Trello board to local tasks.

        Args:
            list_filter: Optional list of list names to sync from

        Returns:
            List of SyncResults for each card processed
        """
        results = []

        # Get all cards from board
        try:
            cards = self.service.board.get_cards()
        except Exception as e:
            logger.error(f"Failed to get cards from board: {e}")
            return [SyncResult(task_id="board", action="error", error=str(e))]

        for card in cards:
            # Filter by list if specified
            if list_filter:
                try:
                    card_list = card.get_list()
                    if card_list.name not in list_filter:
                        continue
                except Exception:
                    continue

            # Skip cards without task IDs
            task_id = self.extract_task_id(card.name)
            if not task_id:
                continue

            result = self.sync_card_to_task(card)
            results.append(result)

        return results

    def get_sync_preview(self) -> List[Dict[str, Any]]:
        """Preview what would be synced without making changes.

        Returns:
            List of dicts describing potential changes
        """
        preview = []

        try:
            cards = self.service.board.get_cards()
        except Exception as e:
            logger.error(f"Failed to get cards: {e}")
            return []

        for card in cards:
            task_id = self.extract_task_id(card.name)
            if not task_id:
                continue

            task = self.task_parser.get_task_by_id(task_id)
            if not task:
                preview.append({
                    "task_id": task_id,
                    "card_name": card.name,
                    "action": "skip",
                    "reason": "Task not found locally"
                })
                continue

            # Check for status difference
            try:
                list_name = card.get_list().name
                trello_status = self.get_list_status(list_name)
                local_status = task.status.value if hasattr(task.status, 'value') else str(task.status)

                if trello_status and trello_status != local_status:
                    preview.append({
                        "task_id": task_id,
                        "card_name": card.name,
                        "action": "update",
                        "field": "status",
                        "from": local_status,
                        "to": trello_status
                    })
                else:
                    preview.append({
                        "task_id": task_id,
                        "card_name": card.name,
                        "action": "skip",
                        "reason": "No changes"
                    })
            except Exception as e:
                preview.append({
                    "task_id": task_id,
                    "card_name": card.name,
                    "action": "error",
                    "reason": str(e)
                })

        return preview


def create_reverse_sync(
    api_key: str,
    token: str,
    board_id: str,
    tasks_dir: Path
) -> TrelloToLocalSync:
    """Create a TrelloToLocalSync instance.

    Args:
        api_key: Trello API key
        token: Trello API token
        board_id: Board ID to sync from
        tasks_dir: Path to .paircoder/tasks directory

    Returns:
        Configured TrelloToLocalSync instance
    """
    service = TrelloService(api_key, token)
    service.set_board(board_id)
    return TrelloToLocalSync(service, tasks_dir)
