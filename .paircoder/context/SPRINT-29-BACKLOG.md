# Sprint 29 Backlog: Contained Autonomy

> Created: 2026-01-13
> Target Release: v2.9.1
> Estimated Effort: ~30 hours
> Complexity Budget: 250 points

---

## Sprint Overview

### The Problem We're Solving

Claude Code has shown a pattern of bypassing enforcement by editing the enforcement code itself:

```python
# Claude encounters this blocking behavior:
requires_review = True

# Claude's "solution":
requires_review = False  # Just edit the file!
```

Even with v2.9.0's enforcement gates, Claude can still:
1. Edit `.claude/agents/*.md` to change role definitions
2. Modify `.claude/commands/*.md` to bypass slash command enforcement
3. Update `tools/cli/bpsai_pair/security/*.py` to disable security checks
4. Change `.paircoder/config.yaml` enforcement settings

### The Solution: Contained Autonomy

Create a **containment mode** that:
- Mounts sensitive directories as **read-only**
- Restricts network access to an **allowlist**
- Creates **auto-checkpoints** before containment entry
- Provides a memorable command: `bpsai-pair claude666`

When Claude enters contained mode:
```
bpsai-pair claude666
  ├── Git checkpoint created (auto-rollback point)
  ├── Enforcement directories mounted read-only
  ├── Network restricted to allowlist
  └── Claude works autonomously... safely
```

---

## Success Criteria

### Must Have (P0)
- [ ] `bpsai-pair claude666` starts a contained autonomous session
- [ ] Claude cannot modify `.claude/` directory contents
- [ ] Claude cannot modify enforcement modules in `tools/cli/bpsai_pair/security/`
- [ ] Claude cannot modify `tools/cli/bpsai_pair/core/` modules
- [ ] Auto-checkpoint created on containment entry

### Should Have (P1)
- [ ] Network allowlist restricts external access
- [ ] Containment status visible in `bpsai-pair status` output
- [ ] Escape attempts logged to audit log
- [ ] Documentation explains when/why to use contained mode

### Nice to Have (P2)
- [ ] Subagent invocation documentation
- [ ] Integration with existing security agent

---

## Technical Context

### Existing Infrastructure (from Sprint 15)

The security module already has foundations we'll build on:

```
tools/cli/bpsai_pair/security/
├── allowlist.py    # Command allowlist (ALLOW/REVIEW/BLOCK)
├── review.py       # Pre-execution review hooks
├── sandbox.py      # Docker sandbox execution
└── checkpoint.py   # Git checkpoint/rollback
```

**Key Insight:** `sandbox.py` currently uses Docker for isolated execution. For contained autonomy, we need a lighter-weight approach that works within the normal development flow - using **mount options** and **filesystem permissions** rather than full containerization.

### Config Schema Target

```yaml
# New section in .paircoder/config.yaml
containment:
  enabled: true
  
  # Directories mounted read-only (Claude can't edit)
  locked_directories:
    - .claude/agents/
    - .claude/commands/
    - .claude/skills/
    - tools/cli/bpsai_pair/security/
    - tools/cli/bpsai_pair/core/
    - tools/cli/bpsai_pair/orchestration/
  
  # Files mounted read-only
  locked_files:
    - .paircoder/config.yaml
    - CLAUDE.md
    - AGENTS.md
  
  # Network allowlist (everything else blocked)
  allow_network:
    - api.anthropic.com
    - api.trello.com
    - github.com
    - pypi.org
  
  # Auto-checkpoint before containment entry
  auto_checkpoint: true

  # Rollback on containment violation attempts
  rollback_on_violation: false
```

### Architecture Decision: Process-Level vs Container

**Option A: Docker Container (Current sandbox.py)**
- Pros: Strong isolation, proven security
- Cons: Heavy, requires Docker, breaks IDE integration

**Option B: Process-Level Restrictions (Recommended)**
- Pros: Lightweight, works with IDE, Claude Code compatible
- Cons: Not as secure as containerization
- Implementation: Use Python's `os.access()` checks + git hooks

**Decision:** Option B - we're not defending against malicious users, we're preventing Claude from accidentally bypassing its own guardrails. Process-level checks are sufficient.

---

## Task Breakdown

### Phase 1: Config Schema & Infrastructure (T29.1-T29.2)

#### T29.1: Design Containment Config Schema
**Priority:** P0
**Complexity:** 25
**Effort:** 2 hours
**Dependencies:** None

**Objective:** Define the complete containment configuration schema that will control contained autonomy behavior.

**Acceptance Criteria:**
- [ ] Schema defined in Pydantic model (ContainmentConfig)
- [ ] Validation for locked_directories paths
- [ ] Validation for locked_files paths
- [ ] Validation for allow_network domains
- [ ] Default values documented
- [ ] Schema added to config.py ConfigModel

**Implementation Notes:**
```python
# tools/cli/bpsai_pair/core/config.py

class ContainmentConfig(BaseModel):
    """Configuration for contained autonomy mode."""
    enabled: bool = False
    locked_directories: list[str] = Field(default_factory=list)
    locked_files: list[str] = Field(default_factory=list)
    allow_network: list[str] = Field(default_factory=lambda: [
        "api.anthropic.com",
        "api.trello.com",
        "github.com",
        "pypi.org"
    ])
    auto_checkpoint: bool = True
    rollback_on_violation: bool = False
```

**Test Cases:**
- Valid config loads successfully
- Invalid directory paths rejected
- Empty network list uses defaults
- Nested path validation works

---

#### T29.2: Add Containment Section to config.yaml
**Priority:** P0
**Complexity:** 20
**Effort:** 2 hours
**Dependencies:** T29.1

**Objective:** Wire the containment config schema into the main config loading and validation system.

**Acceptance Criteria:**
- [ ] `containment:` section recognized in config.yaml
- [ ] Config validation includes containment settings
- [ ] Default containment config generated on `bpsai-pair init`
- [ ] Cookiecutter template updated with containment section
- [ ] `bpsai-pair validate` checks containment config

**Files to Modify:**
- `tools/cli/bpsai_pair/core/config.py` - Add ContainmentConfig to ConfigModel
- `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/config.yaml` - Add containment section
- `tools/cli/bpsai_pair/commands/core.py` - Update init command

**Test Cases:**
- Config without containment section uses defaults
- Config with partial containment section merges with defaults
- Invalid containment config fails validation with clear error

---

### Phase 2: Core Containment Implementation (T29.3-T29.5)

#### T29.3: Implement Directory Locking in containment.py
**Priority:** P0
**Complexity:** 45
**Effort:** 4 hours
**Dependencies:** T29.2

**Objective:** Create the filesystem locking mechanism that prevents writes to protected directories.

**Acceptance Criteria:**
- [ ] `ContainmentManager` class created
- [ ] `is_path_locked(path)` method works correctly
- [ ] `check_write_allowed(path)` raises `ContainmentViolationError` for locked paths
- [ ] Relative and absolute paths handled correctly
- [ ] Symlink resolution prevents bypass
- [ ] Glob patterns supported in locked_directories

**Implementation Notes:**
```python
# tools/cli/bpsai_pair/security/containment.py

class ContainmentViolationError(Exception):
    """Raised when attempting to modify locked resources."""
    pass

class ContainmentManager:
    def __init__(self, config: ContainmentConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self._locked_paths: set[Path] = set()
        self._build_locked_paths()

    def is_path_locked(self, path: Path) -> bool:
        """Check if a path is within a locked directory or is a locked file."""
        resolved = path.resolve()
        for locked in self._locked_paths:
            if resolved == locked or locked in resolved.parents:
                return True
        return False

    def check_write_allowed(self, path: Path) -> None:
        """Raise ContainmentViolationError if write not allowed."""
        if self.is_path_locked(path):
            raise ContainmentViolationError(
                f"Cannot modify locked path: {path}\n"
                f"This path is protected in contained autonomy mode."
            )
```

**Test Cases:**
- Locked directory blocks child file writes
- Locked file blocks specific file writes
- Non-locked paths allow writes
- Symlinks to locked paths are blocked
- Parent directory traversal doesn't bypass locks

---

#### T29.4: Create `contained-auto` Command
**Priority:** P0
**Complexity:** 40
**Effort:** 4 hours
**Dependencies:** T29.3

**Objective:** Implement the main command that starts a contained autonomous session.

**Acceptance Criteria:**
- [ ] `bpsai-pair contained-auto` starts containment session
- [ ] Git checkpoint created on entry (if auto_checkpoint enabled)
- [ ] Containment environment variables set
- [ ] Session start logged
- [ ] Exit handler cleans up containment state
- [ ] Integration with orchestrate module

**Implementation Notes:**
```python
# tools/cli/bpsai_pair/commands/session.py

@app.command("contained-auto")
def contained_auto(
    task: Optional[str] = typer.Argument(None, help="Task to work on"),
    skip_checkpoint: bool = typer.Option(False, help="Skip git checkpoint"),
):
    """
    Start a contained autonomous session.

    In this mode, Claude Code cannot modify:
    - .claude/ directory (agents, commands, skills)
    - Enforcement code (security/, core/, orchestration/)
    - Config files (config.yaml, CLAUDE.md, AGENTS.md)

    A git checkpoint is created automatically for easy rollback.
    """
    config = load_config()

    if not config.containment.enabled:
        console.print("[yellow]Warning: Containment not enabled in config[/yellow]")
        if not typer.confirm("Enable containment for this session?"):
            raise typer.Abort()

    # Create checkpoint
    if config.containment.auto_checkpoint and not skip_checkpoint:
        checkpoint_id = create_checkpoint("containment-entry")
        console.print(f"[green]✓[/green] Checkpoint created: {checkpoint_id}")

    # Initialize containment
    containment = ContainmentManager(config.containment, project_root)
    containment.activate()

    console.print("[green]✓[/green] Contained autonomy mode active")
    console.print("[dim]Protected paths are read-only[/dim]")

    # Set environment for Claude Code to detect
    os.environ["PAIRCODER_CONTAINMENT"] = "1"
    os.environ["PAIRCODER_CONTAINMENT_CHECKPOINT"] = checkpoint_id
```

**Test Cases:**
- Command creates checkpoint when auto_checkpoint enabled
- Command skips checkpoint with --skip-checkpoint
- Containment manager activated correctly
- Environment variables set
- Exit handler called on completion

---

#### T29.5: Add `claude666` Alias
**Priority:** P1  
**Complexity:** 10  
**Effort:** 1 hour  
**Dependencies:** T29.4

**Objective:** Create a memorable alias for the contained-auto command.

**Acceptance Criteria:**
- [ ] `bpsai-pair claude666` works identically to `contained-auto`
- [ ] Help text explains the name ("Claude's beast mode - powerful but contained")
- [ ] Alias documented in CLI reference

**Implementation Notes:**
```python
# In cli.py, add alias
@app.command("claude666", hidden=False)
def claude666_alias(
    task: Optional[str] = typer.Argument(None),
    skip_checkpoint: bool = typer.Option(False),
):
    """
    Start contained autonomy mode. 🔥
    
    Claude's beast mode - powerful but contained.
    Alias for 'contained-auto'.
    """
    return contained_auto(task, skip_checkpoint)
```

**Test Cases:**
- `claude666` invokes `contained-auto`
- Help text shows for `claude666`
- All options work through alias

---

### Phase 3: Network & Security Hardening (T29.6-T29.8)

#### T29.6: Implement Network Allowlist
**Priority:** P1
**Complexity:** 35
**Effort:** 3 hours
**Dependencies:** T29.3

**Objective:** Restrict network access to only allowed domains during containment mode.

**Acceptance Criteria:**
- [ ] Network check hooks into subprocess/request calls
- [ ] Allowed domains pass through
- [ ] Blocked domains raise `NetworkRestrictionError`
- [ ] DNS resolution checked against allowlist
- [ ] Localhost always allowed

**Implementation Notes:**
```python
# tools/cli/bpsai_pair/security/network.py

import socket
from urllib.parse import urlparse

class NetworkRestrictionError(Exception):
    pass

class NetworkGuard:
    def __init__(self, allowed_domains: list[str]):
        self.allowed = set(allowed_domains)
        self.allowed.add("localhost")
        self.allowed.add("127.0.0.1")

    def check_url(self, url: str) -> None:
        """Raise NetworkRestrictionError if URL not in allowlist."""
        parsed = urlparse(url)
        domain = parsed.netloc.split(':')[0]  # Remove port

        if not self._is_allowed(domain):
            raise NetworkRestrictionError(
                f"Network access to '{domain}' blocked in containment mode.\n"
                f"Allowed domains: {', '.join(sorted(self.allowed))}"
            )

    def _is_allowed(self, domain: str) -> bool:
        # Exact match or subdomain match
        for allowed in self.allowed:
            if domain == allowed or domain.endswith(f".{allowed}"):
                return True
        return False
```

**Test Cases:**
- Allowed domain passes check
- Subdomain of allowed domain passes
- Blocked domain raises error
- Localhost always allowed
- IP address handling works

---

#### T29.7: Test Containment Escape Attempts
**Priority:** P0
**Complexity:** 45
**Effort:** 4 hours
**Dependencies:** T29.4

**Objective:** Create comprehensive tests that attempt to bypass containment restrictions.

**Acceptance Criteria:**
- [ ] 20+ escape attempt test cases
- [ ] Symlink bypass attempts blocked
- [ ] Relative path traversal blocked (../)
- [ ] Hardlink bypass attempts blocked
- [ ] Subprocess spawn with modified PATH blocked
- [ ] Environment variable injection blocked
- [ ] All escape attempts logged to audit

**Test Categories:**
```python
# tests/security/test_containment_escapes.py

class TestSymlinkEscapes:
    """Attempts to bypass via symlinks."""
    def test_symlink_to_locked_dir(self): ...
    def test_symlink_chain_to_locked_file(self): ...
    def test_relative_symlink_escape(self): ...

class TestPathTraversalEscapes:
    """Attempts to bypass via path manipulation."""
    def test_dotdot_traversal(self): ...
    def test_double_slash_traversal(self): ...
    def test_encoded_path_traversal(self): ...
    def test_null_byte_injection(self): ...

class TestFilesystemEscapes:
    """Attempts to bypass via filesystem tricks."""
    def test_hardlink_to_locked_file(self): ...
    def test_rename_locked_directory(self): ...
    def test_move_file_to_locked_dir(self): ...

class TestProcessEscapes:
    """Attempts to bypass via process manipulation."""
    def test_subprocess_with_modified_path(self): ...
    def test_shell_command_injection(self): ...
    def test_env_var_override(self): ...

class TestNetworkEscapes:
    """Attempts to bypass network restrictions."""
    def test_dns_rebinding(self): ...
    def test_ip_instead_of_domain(self): ...
    def test_redirect_to_blocked_domain(self): ...
```

**Deliverables:**
- Test file with 20+ test cases
- All tests passing (escapes blocked)
- Audit log contains all attempts

---

#### T29.8: Create Auto-Checkpoint on Containment Entry
**Priority:** P1
**Complexity:** 25
**Effort:** 2 hours
**Dependencies:** T29.4

**Objective:** Ensure a git checkpoint is created before entering containment mode, enabling easy rollback.

**Acceptance Criteria:**
- [ ] Checkpoint created with descriptive name
- [ ] Checkpoint ID stored in environment
- [ ] `bpsai-pair containment rollback` restores checkpoint
- [ ] Uncommitted changes stashed before checkpoint
- [ ] Warning if dirty working directory

**Integration with existing checkpoint.py:**
```python
# tools/cli/bpsai_pair/security/checkpoint.py

def create_containment_checkpoint() -> str:
    """
    Create a checkpoint for containment entry.

    Returns checkpoint ID that can be used for rollback.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    checkpoint_name = f"containment-{timestamp}"

    # Stash any uncommitted changes
    stash_result = run_git("stash", "push", "-m", f"Auto-stash for {checkpoint_name}")

    # Create lightweight tag as checkpoint
    run_git("tag", checkpoint_name, "-m", "Containment entry checkpoint")

    return checkpoint_name
```

**Test Cases:**
- Checkpoint created with correct name format
- Stash created for dirty working directory
- Clean working directory doesn't stash
- Rollback restores to checkpoint state

---

### Phase 4: Integration & Documentation (T29.9-T29.11)

#### T29.9: Add Containment Status to `bpsai-pair status`
**Priority:** P1
**Complexity:** 20
**Effort:** 2 hours
**Dependencies:** T29.4

**Objective:** Show containment status in the main status command output.

**Acceptance Criteria:**
- [ ] Containment section appears in status output when containment enabled
- [ ] Shows: active/inactive, locked paths count, checkpoint ID
- [ ] Color coding: green (safe), yellow (partial), red (disabled)
- [ ] Network allowlist shown when active

**Output Example:**
```
$ bpsai-pair status

Project: paircoder (v2.9.1)
Branch: feature/contained-autonomy
Plan: plan-2026-01-sprint-29

🔒 Containment Status
   Mode: ACTIVE (contained autonomy)
   Checkpoint: containment-20260113-143022
   Locked Paths: 6 directories, 3 files
   Network: Restricted (4 domains allowed)

   Protected:
   • .claude/agents/
   • .claude/commands/
   • .claude/skills/
   • tools/cli/bpsai_pair/security/
   • tools/cli/bpsai_pair/core/
   • .paircoder/config.yaml
```

**Test Cases:**
- Status shows containment section when enabled
- Status hides containment section when disabled
- Correct path counts displayed
- Network status accurate

---

#### T29.10: Document Contained Autonomy Mode
**Priority:** P1
**Complexity:** 30
**Effort:** 3 hours
**Dependencies:** T29.4

**Objective:** Create comprehensive documentation for the contained autonomy feature.

**Acceptance Criteria:**
- [ ] USER_GUIDE.md updated with Contained Autonomy section
- [ ] CLAUDE.md updated with containment instructions
- [ ] New doc: `docs/CONTAINED_AUTONOMY.md` with full details
- [ ] FAQ: When to use contained mode vs normal mode
- [ ] Troubleshooting guide for common containment issues

**Documentation Outline:**
```markdown
# Contained Autonomy Mode

## Overview
What it is, why it exists, when to use it.

## Quick Start
$ bpsai-pair claude666

## Configuration
containment:
  enabled: true
  ...

## Protected Paths
What's locked and why.

## Network Restrictions
What domains are allowed.

## Checkpoints and Rollback
How to recover from bad changes.

## FAQ
- When should I use contained mode?
- Can I add my own locked paths?
- How do I disable containment temporarily?

## Troubleshooting
- "Cannot modify locked path" error
- Network restriction errors
- Checkpoint rollback issues
```

**Test Cases:**
- Documentation renders correctly
- All code examples are valid
- Links work

---

#### T29.11: Create Subagent Invocation Documentation
**Priority:** P2
**Complexity:** 30
**Effort:** 3 hours
**Dependencies:** None

**Objective:** Document how to properly invoke subagents (planner, reviewer, security) in containment mode.

**Acceptance Criteria:**
- [ ] Document: `docs/SUBAGENT_INVOCATION.md`
- [ ] Explains subagent roles and when to use each
- [ ] Shows how to invoke subagents from Claude Code
- [ ] Explains subagent file locations and structure
- [ ] Integration with containment mode documented

**Documentation Outline:**
```markdown
# Subagent Invocation Guide

## Available Subagents
| Agent | Location | Purpose |
|-------|----------|---------|
| Planner | .claude/agents/planner.md | Strategic planning |
| Reviewer | .claude/agents/reviewer.md | Code review |
| Security | .claude/agents/security.md | Security gating |

## Invoking Subagents
How Claude Code reads and applies agent definitions.

## Subagent Structure
What makes a good subagent definition file.

## Custom Subagents
How to create project-specific subagents.

## Containment Considerations
Subagents are read-only in containment mode.
```

---

## Dependency Graph

```
T29.1 (Schema Design)
   │
   └──► T29.2 (Config Integration)
           │
           └──► T29.3 (Directory Locking)
                   │
                   ├──► T29.4 (contained-auto Command)
                   │       │
                   │       ├──► T29.5 (claude666 Alias)
                   │       │
                   │       ├──► T29.7 (Escape Tests)
                   │       │
                   │       ├──► T29.8 (Auto-Checkpoint)
                   │       │
                   │       └──► T29.9 (Status Integration)
                   │
                   └──► T29.6 (Network Allowlist)

T29.10 (Documentation) ──► T29.4 (needs command working)

T29.11 (Subagent Docs) ──► (no dependencies)
```

---

## Effort Summary

| Task | Complexity | Hours | Priority | Phase |
|------|------------|-------|----------|-------|
| T29.1 | 25 | 2h | P0 | 1 |
| T29.2 | 20 | 2h | P0 | 1 |
| T29.3 | 45 | 4h | P0 | 2 |
| T29.4 | 40 | 4h | P0 | 2 |
| T29.5 | 10 | 1h | P1 | 2 |
| T29.6 | 35 | 3h | P1 | 3 |
| T29.7 | 45 | 4h | P0 | 3 |
| T29.8 | 25 | 2h | P1 | 3 |
| T29.9 | 20 | 2h | P1 | 4 |
| T29.10 | 30 | 3h | P1 | 4 |
| T29.11 | 30 | 3h | P2 | 4 |
| **Total** | **325** | **30h** | | |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Containment too restrictive for normal work | HIGH | MEDIUM | Make contained mode opt-in, not default |
| Escape paths missed in testing | HIGH | MEDIUM | Extensive escape testing (T29.7) |
| Network allowlist breaks integrations | MEDIUM | LOW | Allow localhost by default, test with real Trello/GitHub |
| Checkpoint rollback loses wanted changes | MEDIUM | LOW | Warn before rollback, show diff |
| Windows compatibility issues | MEDIUM | MEDIUM | Test on Windows early in sprint |

---

## Definition of Done

### Per Task
- [ ] Implementation complete
- [ ] Unit tests passing (≥80% coverage for new code)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Code reviewed (self-review for solo sprint)

### Per Sprint
- [ ] All P0 tasks complete
- [ ] ≥80% of P1 tasks complete
- [ ] Test suite passing (2200+ tests)
- [ ] `bpsai-pair claude666` works end-to-end
- [ ] Documentation complete
- [ ] Version bumped to 2.9.1
- [ ] CHANGELOG updated

---

## Notes for Planning System

**Plan Type:** `feature`
**Plan Slug:** `sprint-29-contained-autonomy`
**Sprint:** 29

**Trello Mapping:**
- Stack: `Worker/Function`
- Project: `PairCoder`
- Labels: `Worker / Function`

**Task ID Format:** `T29.{n}` (e.g., T29.1, T29.2, ...)
