"""
Planning Parsers

Handles parsing of plan files (.plan.yaml) and task files (.task.md).
Task files use YAML frontmatter + Markdown body format.
"""

import re
from pathlib import Path
from typing import Optional, Tuple

import yaml

from .models import Plan, Task, Sprint


# Regex to match YAML frontmatter (content between --- delimiters)
FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?(.*)$",
    re.DOTALL
)


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Parse YAML frontmatter from a document.
    
    Args:
        content: Full file content with optional YAML frontmatter
        
    Returns:
        Tuple of (frontmatter_dict, body_content)
        If no frontmatter, returns ({}, full_content)
    """
    match = FRONTMATTER_PATTERN.match(content)
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2).strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            frontmatter = {}
        return frontmatter, body
    return {}, content


class PlanParser:
    """
    Parser for plan files (.plan.yaml).
    """
    
    def __init__(self, plans_dir: Path):
        """
        Initialize parser with plans directory.
        
        Args:
            plans_dir: Path to .paircoder/plans/
        """
        self.plans_dir = Path(plans_dir)
    
    def list_plans(self) -> list[Path]:
        """List all plan files in the plans directory."""
        if not self.plans_dir.exists():
            return []
        return sorted(self.plans_dir.glob("*.plan.yaml"))
    
    def parse(self, plan_path: Path) -> Optional[Plan]:
        """
        Parse a single plan file.
        
        Args:
            plan_path: Path to the plan file
            
        Returns:
            Plan object or None if parsing fails
        """
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                return None
            return Plan.from_dict(data, source_path=plan_path)
        except (yaml.YAMLError, OSError) as e:
            print(f"Error parsing plan {plan_path}: {e}")
            return None
    
    def parse_all(self) -> list[Plan]:
        """Parse all plans in the directory."""
        plans = []
        for plan_path in self.list_plans():
            plan = self.parse(plan_path)
            if plan:
                plans.append(plan)
        return plans
    
    def get_plan_by_id(self, plan_id: str) -> Optional[Plan]:
        """
        Find and parse a plan by its ID.
        
        Args:
            plan_id: Plan ID (e.g., "plan-2025-01-feature-name")
            
        Returns:
            Plan object or None if not found
        """
        # Try exact filename match first
        exact_path = self.plans_dir / f"{plan_id}.plan.yaml"
        if exact_path.exists():
            return self.parse(exact_path)
        
        # Search all plans for matching ID
        for plan in self.parse_all():
            if plan.id == plan_id:
                return plan
        
        # Try partial match (slug)
        for plan_path in self.list_plans():
            if plan_id in plan_path.stem:
                return self.parse(plan_path)
        
        return None
    
    def save(self, plan: Plan, filename: Optional[str] = None) -> Path:
        """
        Save a plan to a YAML file.
        
        Args:
            plan: Plan object to save
            filename: Optional filename (defaults to plan.id)
            
        Returns:
            Path to saved file
        """
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"{plan.id}.plan.yaml"
        
        plan_path = self.plans_dir / filename
        
        with open(plan_path, "w", encoding="utf-8") as f:
            yaml.dump(
                plan.to_dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        
        plan.source_path = plan_path
        return plan_path


class TaskParser:
    """
    Parser for task files (.task.md).
    
    Task files use YAML frontmatter + Markdown body format:
    
    ```
    ---
    id: TASK-001
    plan: plan-2025-01-feature
    title: Implement feature X
    status: pending
    ---
    
    # Objective
    
    Description of what this task accomplishes...
    
    # Implementation Plan
    
    - Step 1
    - Step 2
    ```
    """
    
    def __init__(self, tasks_dir: Path):
        """
        Initialize parser with tasks directory.
        
        Args:
            tasks_dir: Path to .paircoder/tasks/
        """
        self.tasks_dir = Path(tasks_dir)
    
    def list_tasks(self, plan_slug: Optional[str] = None) -> list[Path]:
        """
        List all task files, optionally filtered by plan.
        
        Args:
            plan_slug: If provided, only list tasks for this plan
            
        Returns:
            List of task file paths
        """
        if not self.tasks_dir.exists():
            return []
        
        if plan_slug:
            plan_dir = self.tasks_dir / plan_slug
            if plan_dir.exists():
                return sorted(plan_dir.glob("*.task.md"))
            # Also check for plan ID format
            for subdir in self.tasks_dir.iterdir():
                if subdir.is_dir() and plan_slug in subdir.name:
                    return sorted(subdir.glob("*.task.md"))
            return []
        
        # All tasks across all plans
        return sorted(self.tasks_dir.glob("**/*.task.md"))
    
    def parse(self, task_path: Path) -> Optional[Task]:
        """
        Parse a single task file.
        
        Args:
            task_path: Path to the task file
            
        Returns:
            Task object or None if parsing fails
        """
        try:
            with open(task_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            frontmatter, body = parse_frontmatter(content)
            if not frontmatter:
                return None
            
            return Task.from_dict(frontmatter, body=body, source_path=task_path)
        except OSError as e:
            print(f"Error parsing task {task_path}: {e}")
            return None
    
    def parse_all(self, plan_slug: Optional[str] = None) -> list[Task]:
        """
        Parse all tasks, optionally filtered by plan.
        
        Args:
            plan_slug: If provided, only parse tasks for this plan
            
        Returns:
            List of Task objects
        """
        tasks = []
        for task_path in self.list_tasks(plan_slug):
            task = self.parse(task_path)
            if task:
                tasks.append(task)
        return tasks
    
    def get_task_by_id(self, task_id: str, plan_slug: Optional[str] = None) -> Optional[Task]:
        """
        Find and parse a task by its ID.
        
        Args:
            task_id: Task ID (e.g., "TASK-001")
            plan_slug: Optional plan slug to narrow search
            
        Returns:
            Task object or None if not found
        """
        for task in self.parse_all(plan_slug):
            if task.id == task_id:
                return task
        return None
    
    def save(self, task: Task, plan_slug: Optional[str] = None) -> Path:
        """
        Save a task to a Markdown file with YAML frontmatter.
        
        Args:
            task: Task object to save
            plan_slug: Plan slug for directory (defaults to task.plan_id slug)
            
        Returns:
            Path to saved file
        """
        if plan_slug is None:
            # Extract slug from plan ID
            parts = task.plan_id.split("-")
            if len(parts) > 3:
                plan_slug = "-".join(parts[3:])
            else:
                plan_slug = task.plan_id
        
        task_dir = self.tasks_dir / plan_slug
        task_dir.mkdir(parents=True, exist_ok=True)
        
        task_path = task_dir / f"{task.id}.task.md"
        
        # Build frontmatter
        frontmatter = task.to_dict()
        
        # Build content
        content = "---\n"
        content += yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        content += "---\n\n"
        content += task.body if task.body else self._generate_default_body(task)
        
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        task.source_path = task_path
        return task_path
    
    def _generate_default_body(self, task: Task) -> str:
        """Generate default Markdown body for a new task."""
        body = f"# Objective\n\n{task.description or task.title}\n\n"
        body += "# Implementation Plan\n\n- TODO: Add implementation steps\n\n"
        body += "# Acceptance Criteria\n\n- [ ] TODO: Add acceptance criteria\n\n"
        body += "# Verification\n\n- TODO: Add verification steps\n"
        return body
    
    def update_status(self, task_id: str, status: str, plan_slug: Optional[str] = None) -> bool:
        """
        Update a task's status.
        
        Args:
            task_id: Task ID to update
            status: New status value
            plan_slug: Optional plan slug
            
        Returns:
            True if updated successfully
        """
        task = self.get_task_by_id(task_id, plan_slug)
        if not task or not task.source_path:
            return False
        
        # Read current content
        with open(task.source_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        frontmatter["status"] = status
        
        # Rewrite file
        new_content = "---\n"
        new_content += yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        new_content += "---\n\n"
        new_content += body
        
        with open(task.source_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        return True


# Convenience functions

def parse_plan(plan_path: Path) -> Optional[Plan]:
    """Parse a single plan file."""
    parser = PlanParser(plan_path.parent)
    return parser.parse(plan_path)


def parse_task(task_path: Path) -> Optional[Task]:
    """Parse a single task file."""
    parser = TaskParser(task_path.parent.parent)  # tasks_dir is parent of plan_slug dir
    return parser.parse(task_path)
