"""
Tests for the Planning Module

Run with: pytest test_planning.py -v
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from bpsai_pair.planning.models import (
    Plan, Task, Sprint,
    PlanStatus, PlanType, TaskStatus
)
from bpsai_pair.planning.parser import (
    PlanParser, TaskParser, parse_frontmatter
)
from bpsai_pair.planning.state import StateManager, ProjectState


class TestModels:
    """Test data models."""
    
    def test_task_from_dict(self):
        """Test creating Task from dictionary."""
        data = {
            "id": "TASK-001",
            "plan": "plan-2025-01-test",
            "title": "Test Task",
            "type": "feature",
            "priority": "P0",
            "complexity": 50,
            "status": "pending",
            "tags": ["test", "example"],
        }
        
        task = Task.from_dict(data)
        
        assert task.id == "TASK-001"
        assert task.plan_id == "plan-2025-01-test"
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.complexity == 50
        assert "test" in task.tags
    
    def test_task_status_emoji(self):
        """Test status emoji property."""
        task = Task(id="T1", title="Test", plan_id="p1", status=TaskStatus.DONE)
        assert task.status_emoji == "✅"
        
        task.status = TaskStatus.IN_PROGRESS
        assert task.status_emoji == "🔄"
    
    def test_plan_from_dict(self):
        """Test creating Plan from dictionary."""
        data = {
            "id": "plan-2025-01-feature",
            "title": "Feature Plan",
            "type": "feature",
            "status": "in_progress",
            "goals": ["Goal 1", "Goal 2"],
            "sprints": [
                {"id": "sprint-1", "title": "Sprint 1", "tasks": ["TASK-001"]},
            ],
            "tasks": [
                {"id": "TASK-001", "title": "Task 1", "priority": "P0"},
            ],
        }
        
        plan = Plan.from_dict(data)
        
        assert plan.id == "plan-2025-01-feature"
        assert plan.type == PlanType.FEATURE
        assert plan.status == PlanStatus.IN_PROGRESS
        assert len(plan.goals) == 2
        assert len(plan.sprints) == 1
        assert plan.sprints[0].id == "sprint-1"
    
    def test_plan_slug(self):
        """Test plan slug extraction."""
        plan = Plan(id="plan-2025-01-my-feature", title="Test")
        assert plan.slug == "my-feature"


class TestParsers:
    """Test file parsers."""
    
    def test_parse_frontmatter(self):
        """Test YAML frontmatter parsing."""
        content = """---
id: TASK-001
title: Test Task
status: pending
---

# Objective

This is the task body.
"""
        frontmatter, body = parse_frontmatter(content)
        
        assert frontmatter["id"] == "TASK-001"
        assert frontmatter["title"] == "Test Task"
        assert "# Objective" in body
        assert "This is the task body." in body
    
    def test_parse_frontmatter_no_frontmatter(self):
        """Test parsing content without frontmatter."""
        content = "# Just Markdown\n\nNo frontmatter here."
        
        frontmatter, body = parse_frontmatter(content)
        
        assert frontmatter == {}
        assert body == content
    
    def test_plan_parser(self):
        """Test PlanParser with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / "plans"
            plans_dir.mkdir()
            
            # Create a plan file
            plan_content = """
id: plan-2025-01-test
title: Test Plan
type: feature
status: planned
goals:
  - Test goal
tasks:
  - id: TASK-001
    title: First Task
"""
            plan_file = plans_dir / "plan-2025-01-test.plan.yaml"
            plan_file.write_text(plan_content)
            
            # Parse
            parser = PlanParser(plans_dir)
            plans = parser.parse_all()
            
            assert len(plans) == 1
            assert plans[0].id == "plan-2025-01-test"
            assert plans[0].title == "Test Plan"
    
    def test_task_parser(self):
        """Test TaskParser with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_dir = Path(tmpdir) / "tasks" / "test-plan"
            tasks_dir.mkdir(parents=True)
            
            # Create a task file
            task_content = """---
id: TASK-001
plan: plan-2025-01-test-plan
title: Test Task
type: feature
priority: P0
complexity: 50
status: pending
---

# Objective

Do the thing.

# Acceptance Criteria

- [ ] Thing is done
"""
            task_file = tasks_dir / "TASK-001.task.md"
            task_file.write_text(task_content)
            
            # Parse
            parser = TaskParser(Path(tmpdir) / "tasks")
            tasks = parser.parse_all("test-plan")
            
            assert len(tasks) == 1
            assert tasks[0].id == "TASK-001"
            assert tasks[0].title == "Test Task"
            assert "Do the thing." in tasks[0].body


class TestState:
    """Test state management."""
    
    def test_project_state_from_md(self):
        """Test parsing state from state.md content."""
        content = """# Current State

> Last updated: 2025-01-15

## Active Plan

**Plan:** `plan-2025-01-upgrade`
**Status:** in_progress
**Current Sprint:** sprint-1

## What Was Just Done

- ✅ Completed task 1
- ✅ Completed task 2

## What's Next

1. Do task 3
2. Do task 4

## Blockers

- Waiting on dependency
"""
        state = ProjectState.from_state_md(content)
        
        assert state.active_plan_id == "plan-2025-01-upgrade"
        assert len(state.what_was_done) == 2
        assert len(state.whats_next) == 2
        assert len(state.blockers) == 1
    
    def test_project_state_no_blockers(self):
        """Test parsing state with no blockers."""
        content = """# Current State

## Active Plan

**Plan:** `plan-test`

## Blockers

None.
"""
        state = ProjectState.from_state_md(content)
        
        assert state.active_plan_id == "plan-test"
        assert state.blockers == []


class TestFlowParserV2:
    """Test updated flow parser."""
    
    def test_parse_flow_md(self):
        """Test parsing .flow.md format."""
        from bpsai_pair.flows.parser_v2 import FlowParser, parse_frontmatter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            flows_dir = Path(tmpdir) / "flows"
            flows_dir.mkdir()
            
            # Create a .flow.md file
            flow_content = """---
name: test-flow
version: 1
description: A test flow
when_to_use:
  - testing
roles:
  navigator:
    primary: true
  driver:
    primary: true
triggers:
  - test_trigger
tags:
  - test
---

# Test Flow

## Phase 1

Do the first thing.

## Phase 2

Do the second thing.
"""
            flow_file = flows_dir / "test-flow.flow.md"
            flow_file.write_text(flow_content)
            
            # Parse
            parser = FlowParser(flows_dir)
            flows = parser.parse_all()
            
            assert len(flows) == 1
            assert flows[0].name == "test-flow"
            assert flows[0].format == "md"
            assert len(flows[0].roles) == 2
            assert "# Test Flow" in flows[0].body
    
    def test_list_flows_deduplicates(self):
        """Test that .flow.md takes precedence over .flow.yml."""
        from bpsai_pair.flows.parser_v2 import FlowParser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            flows_dir = Path(tmpdir) / "flows"
            flows_dir.mkdir()
            
            # Create both formats for same flow
            yml_content = "name: duplicate\nversion: 1\n"
            md_content = "---\nname: duplicate\nversion: 2\n---\n# Body"
            
            (flows_dir / "duplicate.flow.yml").write_text(yml_content)
            (flows_dir / "duplicate.flow.md").write_text(md_content)
            
            # Parse
            parser = FlowParser(flows_dir)
            flow_paths = parser.list_flows()
            
            # Should only have one (the .md version)
            assert len(flow_paths) == 1
            assert flow_paths[0].suffix == ".md"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
