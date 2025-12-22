---
id: T19.5.1
title: Add `bpsai-pair upgrade` command for existing v2.x projects
plan: sprint-19.5
priority: 2
complexity: 50
status: pending
depends_on: []
trello_card_id: null
---

# T19.5.1: Upgrade Command for Existing v2.x Projects

## Goal

Add a `bpsai-pair upgrade` command that updates content (skills, agents, docs) in existing v2.x projects without overwriting project-specific configuration.

## Background

The `migrate` command handles structural changes (v1.x → v2.x). But users with existing v2.x projects need a way to:
- Get new/updated skills
- Get new/updated agents
- Update generic docs (CLAUDE.md, capabilities.yaml, workflow.md)
- Add missing config sections
- WITHOUT losing their project-specific content

## Proposed CLI Interface

```bash
# Show what would be updated
bpsai-pair upgrade --dry-run

# Run upgrade
bpsai-pair upgrade

# Upgrade specific components only
bpsai-pair upgrade --skills          # Only update .claude/skills/
bpsai-pair upgrade --agents          # Only update .claude/agents/
bpsai-pair upgrade --docs            # Only update safe doc files
bpsai-pair upgrade --config          # Only add missing config sections

# Force overwrite (dangerous - requires confirmation)
bpsai-pair upgrade --force
```

## File Categories

### Always Update (Safe)
These are generic and can be overwritten:

| File | Source |
|------|--------|
| `CLAUDE.md` | Template |
| `AGENTS.md` | Template |
| `.paircoder/capabilities.yaml` | Template |
| `.paircoder/context/workflow.md` | Template |
| `.claude/skills/*` | Template (all skills) |
| `.claude/agents/*` | Template (all agents) |

### Merge (Add Missing)
Add new sections without overwriting existing values:

| File | Behavior |
|------|----------|
| `.paircoder/config.yaml` | Add missing sections (trello, hooks, estimation) |

### Never Touch
Project-specific files that should never be modified:

| File | Reason |
|------|--------|
| `.paircoder/context/state.md` | Current project state |
| `.paircoder/context/project.md` | Project-specific description |
| `.paircoder/plans/*` | User's plans |
| `.paircoder/tasks/*` | User's tasks |
| `config.yaml` values | board_id, project name, etc. |

## Implementation

### File: `tools/cli/bpsai_pair/commands/upgrade.py` (new)

```python
"""Upgrade command for updating existing v2.x projects."""
from pathlib import Path
from dataclasses import dataclass, field
import shutil
import click
import yaml
from importlib import resources

@dataclass
class UpgradePlan:
    """What will be upgraded."""
    skills_to_update: list[str] = field(default_factory=list)
    skills_to_add: list[str] = field(default_factory=list)
    agents_to_update: list[str] = field(default_factory=list)
    agents_to_add: list[str] = field(default_factory=list)
    docs_to_update: list[str] = field(default_factory=list)
    config_sections_to_add: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def get_template_dir() -> Path:
    """Get path to cookiecutter template in installed package."""
    # For installed package
    try:
        with resources.files("bpsai_pair.data") as data_dir:
            template_dir = data_dir / "cookiecutter-paircoder" / "{{cookiecutter.project_slug}}"
            if template_dir.exists():
                return Path(template_dir)
    except Exception:
        pass
    
    # Fallback for development
    cli_dir = Path(__file__).parent.parent
    return cli_dir / "data" / "cookiecutter-paircoder" / "{{cookiecutter.project_slug}}"


def get_bundled_skills() -> dict[str, Path]:
    """Get all skills bundled with the CLI."""
    template = get_template_dir()
    skills_dir = template / ".claude" / "skills"
    skills = {}
    
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skills[skill_dir.name] = skill_file
    
    return skills


def get_bundled_agents() -> dict[str, Path]:
    """Get all agents bundled with the CLI."""
    template = get_template_dir()
    agents_dir = template / ".claude" / "agents"
    agents = {}
    
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.md"):
            agents[agent_file.stem] = agent_file
    
    return agents


def plan_upgrade(project_root: Path) -> UpgradePlan:
    """Create upgrade plan by comparing project to template."""
    plan = UpgradePlan()
    template = get_template_dir()
    
    # Check skills
    bundled_skills = get_bundled_skills()
    project_skills_dir = project_root / ".claude" / "skills"
    
    for skill_name, skill_path in bundled_skills.items():
        project_skill = project_skills_dir / skill_name / "SKILL.md"
        if not project_skill.exists():
            plan.skills_to_add.append(skill_name)
        elif project_skill.read_text() != skill_path.read_text():
            plan.skills_to_update.append(skill_name)
    
    # Check agents
    bundled_agents = get_bundled_agents()
    project_agents_dir = project_root / ".claude" / "agents"
    
    for agent_name, agent_path in bundled_agents.items():
        project_agent = project_agents_dir / f"{agent_name}.md"
        if not project_agent.exists():
            plan.agents_to_add.append(agent_name)
        elif project_agent.read_text() != agent_path.read_text():
            plan.agents_to_update.append(agent_name)
    
    # Check safe docs
    safe_docs = [
        ("CLAUDE.md", "CLAUDE.md"),
        ("AGENTS.md", "AGENTS.md"),
        (".paircoder/capabilities.yaml", ".paircoder/capabilities.yaml"),
        (".paircoder/context/workflow.md", ".paircoder/context/workflow.md"),
    ]
    
    for template_rel, project_rel in safe_docs:
        template_file = template / template_rel
        project_file = project_root / project_rel
        
        if template_file.exists():
            if not project_file.exists():
                plan.docs_to_update.append(project_rel)
            elif project_file.read_text() != template_file.read_text():
                plan.docs_to_update.append(project_rel)
    
    # Check config sections
    config_path = project_root / ".paircoder" / "config.yaml"
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text())
        
        required_sections = ["trello", "hooks", "estimation", "metrics"]
        for section in required_sections:
            if section not in config:
                plan.config_sections_to_add.append(section)
    
    return plan


def execute_upgrade(
    project_root: Path, 
    plan: UpgradePlan,
    skills: bool = True,
    agents: bool = True,
    docs: bool = True,
    config: bool = True,
) -> None:
    """Execute the upgrade plan."""
    template = get_template_dir()
    
    # Update skills
    if skills:
        bundled_skills = get_bundled_skills()
        for skill_name in plan.skills_to_add + plan.skills_to_update:
            src = bundled_skills[skill_name]
            dst_dir = project_root / ".claude" / "skills" / skill_name
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_dir / "SKILL.md")
    
    # Update agents
    if agents:
        bundled_agents = get_bundled_agents()
        for agent_name in plan.agents_to_add + plan.agents_to_update:
            src = bundled_agents[agent_name]
            dst_dir = project_root / ".claude" / "agents"
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_dir / f"{agent_name}.md")
    
    # Update docs
    if docs:
        for doc_rel in plan.docs_to_update:
            src = template / doc_rel
            dst = project_root / doc_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    
    # Add config sections
    if config and plan.config_sections_to_add:
        config_path = project_root / ".paircoder" / "config.yaml"
        config_data = yaml.safe_load(config_path.read_text())
        
        defaults = {
            "trello": {
                "enabled": False,
                "board_id": "",
            },
            "hooks": {
                "enabled": True,
                "on_task_start": ["start_timer", "sync_trello", "update_state"],
                "on_task_complete": ["stop_timer", "record_metrics", "sync_trello", "update_state", "check_unblocked"],
                "on_task_block": ["sync_trello", "update_state"],
            },
            "estimation": {
                "complexity_to_hours": {
                    "xs": {"range": [0, 15], "hours": [0.5, 1.0, 2.0]},
                    "s": {"range": [16, 30], "hours": [1.0, 2.0, 4.0]},
                    "m": {"range": [31, 50], "hours": [2.0, 4.0, 8.0]},
                    "l": {"range": [51, 75], "hours": [4.0, 8.0, 16.0]},
                    "xl": {"range": [76, 100], "hours": [8.0, 16.0, 32.0]},
                }
            },
            "metrics": {
                "enabled": True,
                "store_path": ".paircoder/history/metrics.jsonl",
            },
        }
        
        for section in plan.config_sections_to_add:
            if section in defaults:
                config_data[section] = defaults[section]
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)


@click.command("upgrade")
@click.option("--dry-run", is_flag=True, help="Show what would change without making changes")
@click.option("--skills", "only_skills", is_flag=True, help="Only update skills")
@click.option("--agents", "only_agents", is_flag=True, help="Only update agents")
@click.option("--docs", "only_docs", is_flag=True, help="Only update safe doc files")
@click.option("--config", "only_config", is_flag=True, help="Only add missing config sections")
@click.pass_context
def upgrade_cmd(ctx, dry_run: bool, only_skills: bool, only_agents: bool, only_docs: bool, only_config: bool):
    """Upgrade existing v2.x project with latest skills, agents, and docs."""
    project_root = Path.cwd()
    
    # Check this is a v2.x project
    paircoder_dir = project_root / ".paircoder"
    if not paircoder_dir.exists():
        click.echo("❌ No .paircoder/ directory found. Run 'bpsai-pair init' first.")
        ctx.exit(1)
    
    config_path = paircoder_dir / "config.yaml"
    if not config_path.exists():
        click.echo("❌ No config.yaml found. Run 'bpsai-pair init' first.")
        ctx.exit(1)
    
    # Plan upgrade
    plan = plan_upgrade(project_root)
    
    # Check if anything needs updating
    has_updates = any([
        plan.skills_to_add,
        plan.skills_to_update,
        plan.agents_to_add,
        plan.agents_to_update,
        plan.docs_to_update,
        plan.config_sections_to_add,
    ])
    
    if not has_updates:
        click.echo("✅ Project is up to date. Nothing to upgrade.")
        return
    
    # Show plan
    click.echo("\n📋 Upgrade Plan:\n")
    
    if plan.skills_to_add:
        click.echo("  Skills to add:")
        for s in plan.skills_to_add:
            click.echo(f"    ➕ {s}")
    
    if plan.skills_to_update:
        click.echo("  Skills to update:")
        for s in plan.skills_to_update:
            click.echo(f"    🔄 {s}")
    
    if plan.agents_to_add:
        click.echo("  Agents to add:")
        for a in plan.agents_to_add:
            click.echo(f"    ➕ {a}")
    
    if plan.agents_to_update:
        click.echo("  Agents to update:")
        for a in plan.agents_to_update:
            click.echo(f"    🔄 {a}")
    
    if plan.docs_to_update:
        click.echo("  Docs to update:")
        for d in plan.docs_to_update:
            click.echo(f"    📄 {d}")
    
    if plan.config_sections_to_add:
        click.echo("  Config sections to add:")
        for c in plan.config_sections_to_add:
            click.echo(f"    ⚙️  {c}")
    
    if dry_run:
        click.echo("\n--dry-run specified. No changes made.")
        return
    
    # Determine what to upgrade
    # If no specific flags, upgrade everything
    upgrade_all = not any([only_skills, only_agents, only_docs, only_config])
    
    do_skills = upgrade_all or only_skills
    do_agents = upgrade_all or only_agents
    do_docs = upgrade_all or only_docs
    do_config = upgrade_all or only_config
    
    # Confirm
    if not click.confirm("\nProceed with upgrade?"):
        click.echo("Aborted.")
        return
    
    # Execute
    click.echo("\n🔄 Upgrading...")
    execute_upgrade(
        project_root, 
        plan,
        skills=do_skills,
        agents=do_agents,
        docs=do_docs,
        config=do_config,
    )
    
    click.echo("\n✅ Upgrade complete!")
    
    # Summary
    summary = []
    if do_skills and (plan.skills_to_add or plan.skills_to_update):
        summary.append(f"{len(plan.skills_to_add)} skills added, {len(plan.skills_to_update)} updated")
    if do_agents and (plan.agents_to_add or plan.agents_to_update):
        summary.append(f"{len(plan.agents_to_add)} agents added, {len(plan.agents_to_update)} updated")
    if do_docs and plan.docs_to_update:
        summary.append(f"{len(plan.docs_to_update)} docs updated")
    if do_config and plan.config_sections_to_add:
        summary.append(f"{len(plan.config_sections_to_add)} config sections added")
    
    if summary:
        click.echo(f"  {', '.join(summary)}")
```

### Register in CLI

Add to `cli.py`:
```python
from bpsai_pair.commands.upgrade import upgrade_cmd
app.add_command(upgrade_cmd)
```

## Acceptance Criteria

- [ ] `bpsai-pair upgrade --dry-run` shows what would change
- [ ] `bpsai-pair upgrade` updates all safe files
- [ ] `bpsai-pair upgrade --skills` only updates skills
- [ ] `bpsai-pair upgrade --agents` only updates agents
- [ ] `bpsai-pair upgrade --docs` only updates safe docs
- [ ] `bpsai-pair upgrade --config` only adds missing config sections
- [ ] Project-specific files (state.md, project.md) are NEVER touched
- [ ] Config values (board_id, project name) are NEVER overwritten
- [ ] Missing directories are created automatically
- [ ] Works for both installed package and dev mode

## Test Cases

```python
def test_plan_upgrade_detects_missing_skills(tmp_path):
    """Detect when skills are missing from project."""
    # Setup minimal v2 project without skills
    (tmp_path / ".paircoder").mkdir()
    (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.4'")
    (tmp_path / ".claude").mkdir()
    
    plan = plan_upgrade(tmp_path)
    
    # Should detect all bundled skills as needing to be added
    assert len(plan.skills_to_add) > 0

def test_upgrade_preserves_project_specific_files(tmp_path):
    """Ensure project-specific files are not touched."""
    # Setup project with custom state.md
    (tmp_path / ".paircoder" / "context").mkdir(parents=True)
    custom_state = "# My Custom State\n\nDo not overwrite!"
    (tmp_path / ".paircoder" / "context" / "state.md").write_text(custom_state)
    (tmp_path / ".paircoder" / "config.yaml").write_text("version: '2.4'")
    
    plan = plan_upgrade(tmp_path)
    
    # state.md should never appear in update list
    assert ".paircoder/context/state.md" not in plan.docs_to_update

def test_upgrade_adds_missing_config_sections(tmp_path):
    """Missing config sections are detected."""
    (tmp_path / ".paircoder").mkdir()
    (tmp_path / ".paircoder" / "config.yaml").write_text(
        "version: '2.4'\nproject:\n  name: test"
    )
    
    plan = plan_upgrade(tmp_path)
    
    assert "trello" in plan.config_sections_to_add
    assert "hooks" in plan.config_sections_to_add

def test_upgrade_does_not_overwrite_config_values(tmp_path):
    """Existing config values preserved when adding sections."""
    (tmp_path / ".paircoder").mkdir()
    original_config = """
version: '2.4'
project:
  name: my-project
trello:
  board_id: "abc123"
  enabled: true
"""
    (tmp_path / ".paircoder" / "config.yaml").write_text(original_config)
    
    plan = plan_upgrade(tmp_path)
    execute_upgrade(tmp_path, plan, config=True)
    
    # Verify board_id was preserved
    updated = yaml.safe_load((tmp_path / ".paircoder" / "config.yaml").read_text())
    assert updated["trello"]["board_id"] == "abc123"
```

## Effort Estimate

- Complexity: 50
- Effort: M (4-6 hours)
- Risk: Low (file operations, no external dependencies)

## Notes

- Complements `migrate` (structural) with content updates
- Uses same template source as cookiecutter
- Safe by default - only touches generic files
- Config merge is additive only (never overwrites values)
