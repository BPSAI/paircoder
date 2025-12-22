---
id: T-TOKEN-BUDGET
title: Token-Aware Context Budget Management
plan: sprint-23
priority: 1
complexity: 65
effort: L
status: pending
depends_on: []
trello_card_id: null
---

# Token-Aware Context Budget Management

## Goal

Prevent context compaction by proactively tracking, estimating, and managing token usage throughout a session. Claude should never hit the context limit unexpectedly.

## Background

### The Problem

Claude Code has a ~100K token context limit. When exceeded, compaction occurs:
- Context is summarized/truncated
- Important details are lost
- Claude loses track of what was done
- Work may need to be repeated

### Current State

We have **reactive** tools:
- `compaction check` - Detects AFTER compaction happened
- `compaction recover` - Restores context AFTER the fact
- `session check` - Detects new sessions by TIME, not tokens

We need **proactive** tools:
- Estimate tokens BEFORE starting a task
- Track usage DURING work
- Warn/checkpoint BEFORE hitting limits
- Size tasks to FIT within budget

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TOKEN BUDGET SYSTEM                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   ESTIMATE   │───▶│    TRACK     │───▶│    ALERT     │          │
│  │              │    │              │    │              │          │
│  │ Before task: │    │ During work: │    │ At threshold:│          │
│  │ - File sizes │    │ - Message ct │    │ - 50%: Info  │          │
│  │ - Complexity │    │ - Time proxy │    │ - 75%: Warn  │          │
│  │ - History    │    │ - tiktoken   │    │ - 90%: Block │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────────────────────────────────────────────┐          │
│  │                    ACTIONS                            │          │
│  │                                                       │          │
│  │  • Break large tasks into smaller ones               │          │
│  │  • Force checkpoint before continuing                │          │
│  │  • Auto-save progress to state.md                    │          │
│  │  • Suggest task handoff to new session               │          │
│  └──────────────────────────────────────────────────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation

### 1. Token Estimation Module

**File:** `tools/cli/bpsai_pair/tokens.py`

```python
"""Token estimation and tracking for context budget management."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import tiktoken

# Claude uses cl100k_base encoding
ENCODING = tiktoken.get_encoding("cl100k_base")

# Known context limits
CONTEXT_LIMITS = {
    "claude-opus-4-5": 200000,
    "claude-sonnet-4-5": 200000,
    "claude-haiku-4-5": 200000,
    "default": 100000,  # Conservative default
}

# Base context consumption (skills, state, project docs)
BASE_CONTEXT_TOKENS = 15000


@dataclass
class TokenEstimate:
    """Estimated token usage for a task."""
    base_context: int          # Skills, state, project docs
    file_content: int          # Files that will be read/modified
    expected_output: int       # Estimated response tokens
    conversation_buffer: int   # Back-and-forth overhead
    total: int                 # Sum of all
    confidence: str            # "high", "medium", "low"
    breakdown: dict            # Detailed breakdown by component


@dataclass
class TokenBudget:
    """Current token budget status."""
    limit: int                 # Total context limit
    estimated_used: int        # Estimated tokens consumed
    remaining: int             # Tokens remaining
    percentage_used: float     # 0.0 to 1.0
    status: str                # "ok", "warning", "critical", "exceeded"
    recommendation: str        # What to do


def count_tokens(text: str) -> int:
    """Count tokens in a string using tiktoken."""
    return len(ENCODING.encode(text))


def count_file_tokens(file_path: Path) -> int:
    """Count tokens in a file."""
    if not file_path.exists():
        return 0
    try:
        content = file_path.read_text(errors='ignore')
        return count_tokens(content)
    except Exception:
        # Estimate based on file size (rough: 4 chars per token)
        return file_path.stat().st_size // 4


def estimate_task_tokens(
    task_id: str,
    files_to_read: list[Path] = None,
    files_to_modify: list[Path] = None,
    complexity: str = "m",
    task_type: str = "feature",
) -> TokenEstimate:
    """
    Estimate total tokens a task will consume.
    
    Args:
        task_id: Task identifier for loading task details
        files_to_read: Files that will be read for context
        files_to_modify: Files that will be created/modified
        complexity: Task complexity (xs, s, m, l, xl)
        task_type: Type of task (feature, bugfix, refactor, docs)
    
    Returns:
        TokenEstimate with detailed breakdown
    """
    files_to_read = files_to_read or []
    files_to_modify = files_to_modify or []
    
    # Base context (always loaded)
    base_context = BASE_CONTEXT_TOKENS
    
    # File content tokens
    file_content = 0
    file_breakdown = {}
    
    for f in files_to_read + files_to_modify:
        tokens = count_file_tokens(f)
        file_content += tokens
        file_breakdown[str(f)] = tokens
    
    # Expected output multiplier based on task type
    output_multipliers = {
        "feature": 1.5,    # New code generation
        "bugfix": 0.8,     # Focused fixes
        "refactor": 2.0,   # Lots of code rewriting
        "docs": 0.5,       # Less code generation
        "chore": 0.7,      # Moderate output
    }
    output_mult = output_multipliers.get(task_type, 1.0)
    
    # Complexity affects conversation length
    complexity_multipliers = {
        "xs": 1.0,   # Quick task, minimal back-and-forth
        "s": 1.5,    # Some discussion
        "m": 2.5,    # Typical task
        "l": 4.0,    # Extended work
        "xl": 6.0,   # Long session
    }
    complexity_mult = complexity_multipliers.get(complexity.lower(), 2.5)
    
    # Estimated output tokens (responses from Claude)
    expected_output = int(file_content * output_mult)
    
    # Conversation buffer (user prompts, tool calls, etc.)
    conversation_buffer = int((base_context + file_content) * 0.3 * complexity_mult)
    
    # Total
    total = base_context + file_content + expected_output + conversation_buffer
    
    # Confidence based on how much we know
    if files_to_read or files_to_modify:
        confidence = "high" if len(files_to_read) + len(files_to_modify) > 0 else "medium"
    else:
        confidence = "low"
    
    return TokenEstimate(
        base_context=base_context,
        file_content=file_content,
        expected_output=expected_output,
        conversation_buffer=conversation_buffer,
        total=total,
        confidence=confidence,
        breakdown={
            "base_context": base_context,
            "files": file_breakdown,
            "expected_output": expected_output,
            "conversation_buffer": conversation_buffer,
        }
    )


def get_budget_status(
    estimated_used: int,
    model: str = "default",
) -> TokenBudget:
    """
    Get current budget status and recommendation.
    
    Args:
        estimated_used: Estimated tokens consumed so far
        model: Model name for context limit lookup
    
    Returns:
        TokenBudget with status and recommendation
    """
    limit = CONTEXT_LIMITS.get(model, CONTEXT_LIMITS["default"])
    remaining = limit - estimated_used
    percentage = estimated_used / limit
    
    if percentage < 0.5:
        status = "ok"
        recommendation = "Plenty of budget remaining. Continue normally."
    elif percentage < 0.75:
        status = "warning"
        recommendation = "Consider checkpointing progress to state.md soon."
    elif percentage < 0.90:
        status = "critical"
        recommendation = "Checkpoint NOW. Complete current task and start new session."
    else:
        status = "exceeded"
        recommendation = "Context limit reached. Save progress immediately and restart."
    
    return TokenBudget(
        limit=limit,
        estimated_used=estimated_used,
        remaining=remaining,
        percentage_used=percentage,
        status=status,
        recommendation=recommendation,
    )


def should_break_task(estimate: TokenEstimate, model: str = "default") -> tuple[bool, str]:
    """
    Determine if a task should be broken into smaller pieces.
    
    Returns:
        (should_break, reason)
    """
    limit = CONTEXT_LIMITS.get(model, CONTEXT_LIMITS["default"])
    
    # Task shouldn't consume more than 60% of context in one go
    max_task_tokens = int(limit * 0.6)
    
    if estimate.total > max_task_tokens:
        return True, f"Task estimated at {estimate.total:,} tokens exceeds 60% budget ({max_task_tokens:,}). Break into smaller tasks."
    
    if estimate.total > limit * 0.4:
        return False, f"Task is large ({estimate.total:,} tokens). Consider checkpoints during work."
    
    return False, f"Task fits budget ({estimate.total:,} tokens)."
```

### 2. CLI Commands

**File:** `tools/cli/bpsai_pair/commands/budget.py`

```python
"""Token budget CLI commands."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn

try:
    from ..tokens import (
        estimate_task_tokens, get_budget_status, should_break_task,
        count_file_tokens, CONTEXT_LIMITS
    )
    from ..planning import TaskParser
    from ..config import Config
except ImportError:
    from bpsai_pair.tokens import (
        estimate_task_tokens, get_budget_status, should_break_task,
        count_file_tokens, CONTEXT_LIMITS
    )
    from bpsai_pair.planning import TaskParser
    from bpsai_pair.config import Config

console = Console()

budget_app = typer.Typer(
    help="Token budget management",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@budget_app.command("estimate")
def budget_estimate(
    task_id: Optional[str] = typer.Argument(None, help="Task ID to estimate"),
    files: Optional[list[str]] = typer.Option(None, "--file", "-f", help="Files to include"),
    complexity: str = typer.Option("m", "--complexity", "-c", help="Complexity (xs/s/m/l/xl)"),
    task_type: str = typer.Option("feature", "--type", "-t", help="Task type"),
):
    """Estimate token usage for a task or set of files."""
    
    file_paths = [Path(f) for f in (files or [])]
    
    # If task_id provided, load task details
    if task_id:
        try:
            config = Config.load()
            task_parser = TaskParser(Path.cwd() / config.workflow.tasks_dir)
            task = task_parser.get_task(task_id)
            if task:
                complexity = task.complexity or complexity
                task_type = task.type or task_type
                # Could also extract files_touched from task if available
        except Exception:
            pass
    
    estimate = estimate_task_tokens(
        task_id=task_id or "manual",
        files_to_read=file_paths,
        files_to_modify=[],
        complexity=complexity,
        task_type=task_type,
    )
    
    # Display estimate
    console.print(f"\n[bold]Token Estimate[/bold] (confidence: {estimate.confidence})\n")
    
    table = Table(show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Tokens", justify="right")
    
    table.add_row("Base context (skills, state, docs)", f"{estimate.base_context:,}")
    table.add_row("File content", f"{estimate.file_content:,}")
    table.add_row("Expected output", f"{estimate.expected_output:,}")
    table.add_row("Conversation buffer", f"{estimate.conversation_buffer:,}")
    table.add_row("[bold]Total[/bold]", f"[bold]{estimate.total:,}[/bold]")
    
    console.print(table)
    
    # Check if should break
    should_break, reason = should_break_task(estimate)
    
    if should_break:
        console.print(f"\n[red]⚠️  {reason}[/red]")
    else:
        console.print(f"\n[green]✓ {reason}[/green]")
    
    # Show budget bar
    budget = get_budget_status(estimate.total)
    _print_budget_bar(budget)


@budget_app.command("status")
def budget_status(
    model: str = typer.Option("default", "--model", "-m", help="Model for context limit"),
):
    """Show current estimated budget status."""
    
    # Estimate current context by counting loaded files
    paircoder_dir = Path.cwd() / ".paircoder"
    
    estimated_tokens = 0
    
    # Count context files
    context_files = [
        paircoder_dir / "context" / "state.md",
        paircoder_dir / "context" / "project.md",
        paircoder_dir / "context" / "workflow.md",
        paircoder_dir / "capabilities.yaml",
        Path.cwd() / "CLAUDE.md",
    ]
    
    for f in context_files:
        estimated_tokens += count_file_tokens(f)
    
    # Count skills
    skills_dir = Path.cwd() / ".claude" / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.rglob("SKILL.md"):
            estimated_tokens += count_file_tokens(skill_file)
    
    # Add base overhead
    estimated_tokens += 5000  # System prompt, etc.
    
    budget = get_budget_status(estimated_tokens, model)
    
    console.print(f"\n[bold]Token Budget Status[/bold]\n")
    console.print(f"Model: {model}")
    console.print(f"Context limit: {budget.limit:,} tokens")
    console.print(f"Base context: ~{estimated_tokens:,} tokens")
    console.print(f"Available for work: ~{budget.remaining:,} tokens")
    
    _print_budget_bar(budget)
    
    console.print(f"\n[dim]{budget.recommendation}[/dim]")


@budget_app.command("check")
def budget_check(
    task_id: str = typer.Argument(..., help="Task ID to check"),
    block: bool = typer.Option(False, "--block", help="Exit with error if task too large"),
):
    """Check if a task fits in the current budget. Use before starting work."""
    
    # Load task
    config = Config.load()
    task_parser = TaskParser(Path.cwd() / config.workflow.tasks_dir)
    task = task_parser.get_task(task_id)
    
    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)
    
    estimate = estimate_task_tokens(
        task_id=task_id,
        complexity=task.complexity or "m",
        task_type=task.type or "feature",
    )
    
    should_break, reason = should_break_task(estimate)
    
    if should_break:
        console.print(f"[red]⚠️  TASK TOO LARGE[/red]")
        console.print(f"[red]{reason}[/red]")
        console.print("\n[yellow]Suggestions:[/yellow]")
        console.print("  1. Break this task into 2-3 smaller tasks")
        console.print("  2. Create checkpoint tasks between phases")
        console.print("  3. Reduce scope of this task")
        
        if block:
            raise typer.Exit(1)
    else:
        console.print(f"[green]✓ Task fits budget[/green]")
        console.print(f"[dim]{reason}[/dim]")


def _print_budget_bar(budget: TokenBudget):
    """Print a visual budget bar."""
    
    # Color based on status
    colors = {
        "ok": "green",
        "warning": "yellow", 
        "critical": "red",
        "exceeded": "red",
    }
    color = colors.get(budget.status, "white")
    
    # Create bar
    bar_width = 40
    filled = int(bar_width * budget.percentage_used)
    empty = bar_width - filled
    
    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
    
    console.print(f"\n{bar} {budget.percentage_used:.0%}")
    console.print(f"[{color}]{budget.status.upper()}[/{color}]")
```

### 3. Pre-Task Hook

**Add to `hooks.py`:**

```python
def check_token_budget(task_id: str) -> bool:
    """
    Hook that runs before starting a task.
    Warns or blocks if task may exceed budget.
    
    Returns:
        True if ok to proceed, False to block
    """
    from .tokens import estimate_task_tokens, should_break_task, get_budget_status
    from .planning import TaskParser
    from .config import Config
    
    try:
        config = Config.load()
        task_parser = TaskParser(Path.cwd() / config.workflow.tasks_dir)
        task = task_parser.get_task(task_id)
        
        if not task:
            return True  # Can't estimate, proceed anyway
        
        estimate = estimate_task_tokens(
            task_id=task_id,
            complexity=task.complexity or "m",
            task_type=task.type or "feature",
        )
        
        should_break, reason = should_break_task(estimate)
        
        if should_break:
            console.print(f"\n[red]⚠️  TOKEN BUDGET WARNING[/red]")
            console.print(f"[red]{reason}[/red]")
            console.print("\n[yellow]Consider breaking this task into smaller pieces.[/yellow]")
            console.print("[dim]Use --force to proceed anyway[/dim]\n")
            return False
        
        budget = get_budget_status(estimate.total)
        if budget.status in ["warning", "critical"]:
            console.print(f"\n[yellow]⚠️  {budget.recommendation}[/yellow]\n")
        
        return True
        
    except Exception as e:
        # Don't block on estimation errors
        console.print(f"[dim]Token estimation unavailable: {e}[/dim]")
        return True
```

### 4. Config Integration

**Add to `config.yaml` schema:**

```yaml
token_budget:
  enabled: true
  model: claude-sonnet-4-5    # For context limit lookup
  warn_threshold: 0.50        # Warn at 50% usage
  critical_threshold: 0.75    # Critical warning at 75%
  block_threshold: 0.90       # Block new tasks at 90%
  max_task_percentage: 0.60   # Max % of budget for single task
  auto_checkpoint: true       # Auto-save progress at thresholds
```

### 5. Session Integration

**Update `session.py` to include token tracking:**

```python
@session_app.command("status")
def session_status():
    """Show current session status including token budget."""
    
    # ... existing session time tracking ...
    
    # Add token budget info
    from ..tokens import get_budget_status, count_file_tokens
    
    # Estimate current usage
    estimated = estimate_current_context()
    budget = get_budget_status(estimated)
    
    console.print(f"\n[bold]Token Budget[/bold]")
    console.print(f"  Estimated used: {budget.estimated_used:,}")
    console.print(f"  Remaining: {budget.remaining:,}")
    console.print(f"  Status: [{status_color(budget.status)}]{budget.status}[/]")
```

## CLI Commands Summary

```bash
# Estimate tokens for a task before starting
bpsai-pair budget estimate T23.1

# Estimate for specific files
bpsai-pair budget estimate --file src/main.py --file src/utils.py -c l

# Check current budget status
bpsai-pair budget status

# Pre-flight check before starting task (use in hooks)
bpsai-pair budget check T23.1 --block

# Session status now includes budget
bpsai-pair session status
```

## Hook Integration

```yaml
# config.yaml
hooks:
  on_task_start:
    - check_token_budget    # NEW: Warn if task too large
    - start_timer
    - sync_trello
    - update_state
```

## Acceptance Criteria

- [ ] `bpsai-pair budget estimate <task>` shows token breakdown
- [ ] `bpsai-pair budget status` shows current context usage
- [ ] `bpsai-pair budget check <task> --block` exits 1 if task too large
- [ ] `check_token_budget` hook runs before task start
- [ ] Warning displayed at 50% context usage
- [ ] Critical warning at 75%
- [ ] Block new tasks at 90%
- [ ] `session status` includes token budget
- [ ] Large tasks (>60% budget) flagged for breakdown
- [ ] tiktoken integration for accurate counting

## Dependencies

- `tiktoken` package (add to requirements.txt)

## Test Cases

```python
def test_count_tokens():
    """Token counting works."""
    from bpsai_pair.tokens import count_tokens
    assert count_tokens("hello world") > 0

def test_estimate_small_task():
    """Small task estimates correctly."""
    estimate = estimate_task_tokens("test", complexity="xs")
    assert estimate.total < 30000

def test_estimate_large_task():
    """Large task flagged for breakdown."""
    estimate = estimate_task_tokens("test", complexity="xl")
    should_break, _ = should_break_task(estimate)
    # XL tasks should usually be broken down

def test_budget_status_ok():
    """Budget ok at low usage."""
    budget = get_budget_status(20000)
    assert budget.status == "ok"

def test_budget_status_warning():
    """Budget warning at 50%+."""
    budget = get_budget_status(55000)
    assert budget.status == "warning"

def test_budget_status_critical():
    """Budget critical at 75%+."""
    budget = get_budget_status(80000)
    assert budget.status == "critical"
```

## Effort Estimate

- Complexity: 65
- Effort: L (6-10 hours)
- Risk: Medium (tiktoken accuracy varies)

## Notes

- tiktoken provides ~95% accurate estimates for Claude
- Real usage varies based on conversation flow
- Estimates are conservative to avoid underestimating
- File content is the most predictable component
- Conversation buffer is hardest to estimate
