# Contained Autonomy Mode

> Safely run Claude Code with autonomous capabilities while protecting critical infrastructure

---

## Overview

### What is Contained Autonomy?

Contained Autonomy Mode is a safety feature that lets you run Claude Code autonomously while preventing it from modifying its own enforcement infrastructure. This solves a fundamental challenge in AI agent development: **how do you let an agent work autonomously without risking it modifying the rules that govern its behavior?**

### The Problem It Solves

When running Claude Code in autonomous mode, there's an inherent risk that the AI might:
- Modify skill definitions to bypass workflow requirements
- Edit CLAUDE.md to remove constraints
- Change security enforcement code
- Access credentials or secrets

Contained Autonomy addresses this by implementing **three-tier filesystem access control**:

| Tier | Access | Purpose | Examples |
|------|--------|---------|----------|
| **Blocked** | No read, no write | Secrets and credentials | `.env`, `credentials.json` |
| **Read-only** | Can read, cannot write | Enforcement infrastructure | `CLAUDE.md`, `.claude/skills/` |
| **Read-write** | Full access | Working area | `src/`, `tests/`, etc. |

### How It Works

1. **Git checkpoint created** - Automatic rollback point before entering containment
2. **Filesystem access enforced** - Three-tier protection based on configuration
3. **Network restricted** - Only allowed domains can be accessed
4. **Claude works autonomously** - Full capability within the allowed scope
5. **Safe exit** - Can rollback if anything goes wrong

---

## Quick Start

### Enter Containment Mode

```bash
# Start Claude Code in contained autonomy mode
bpsai-pair contained-auto
```

This command:
- Creates a git checkpoint (for rollback)
- Activates containment enforcement
- Launches Claude Code with `--dangerously-skip-permissions`

### Check Containment Status

```bash
# View current containment status
bpsai-pair containment status
```

### Exit and Rollback

```bash
# Rollback to last checkpoint (undo all changes)
bpsai-pair containment rollback

# Manual rollback via git
git reset --hard containment-YYYYMMDD-HHMMSS
```

---

## Configuration

### Default Configuration

Containment is configured in `.paircoder/config.yaml`:

```yaml
containment:
  enabled: true
  mode: strict                    # strict | permissive
  auto_checkpoint: true           # Create checkpoint on entry
  rollback_on_violation: false    # Auto-rollback on violation attempt

  # Tier 1: Blocked (no read, no write) - secrets and credentials
  blocked_directories: []
  blocked_files:
    - .env
    - .env.local
    - .env.production
    - credentials.json
    - secrets.yaml
    - .npmrc
    - .pypirc

  # Tier 2: Read-only (can read, cannot write) - enforcement code
  readonly_directories:
    - .claude/agents
    - .claude/commands
    - .claude/skills
    - tools/cli/bpsai_pair/security
    - tools/cli/bpsai_pair/core
    - tools/cli/bpsai_pair/orchestration
  readonly_files:
    - .paircoder/config.yaml
    - CLAUDE.md
    - AGENTS.md

  # Network domains allowed in containment mode
  allow_network:
    - api.anthropic.com
    - api.trello.com
    - github.com
    - pypi.org
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable containment feature |
| `mode` | string | `strict` | `strict` = fail on violation, `permissive` = warn only |
| `auto_checkpoint` | bool | `true` | Create git checkpoint on containment entry |
| `rollback_on_violation` | bool | `false` | Automatically rollback on violation attempt |
| `blocked_directories` | list | `[]` | Directories with no read/write access |
| `blocked_files` | list | See above | Files with no read/write access |
| `readonly_directories` | list | See above | Directories with read-only access |
| `readonly_files` | list | See above | Files with read-only access |
| `allow_network` | list | See above | Domains allowed for network access |

### Modes

**Strict Mode** (default):
- Raises `ContainmentViolationError` on protected path access
- Blocks the operation entirely
- Recommended for production use

**Permissive Mode**:
- Logs warning but allows operation
- Useful for testing and debugging
- Not recommended for autonomous operation

---

## Protected Paths

### Tier 1: Blocked Paths

Blocked paths cannot be read OR written. These typically contain secrets and credentials that Claude should never access:

| Path Pattern | Why Blocked |
|--------------|-------------|
| `.env*` | Environment variables with secrets |
| `credentials.json` | Service account credentials |
| `secrets.yaml` | Application secrets |
| `.npmrc` | NPM auth tokens |
| `.pypirc` | PyPI credentials |

**Note**: Blocked paths are configured as files by default. You can add directories to `blocked_directories` if needed.

### Tier 2: Read-only Paths

Read-only paths can be read but not written. Claude can see these files to understand project context but cannot modify them:

| Path | Why Read-only |
|------|---------------|
| `.claude/agents/` | Role definitions that govern Claude's behavior |
| `.claude/commands/` | Slash command implementations |
| `.claude/skills/` | Skill definitions and workflows |
| `tools/cli/bpsai_pair/security/` | Security enforcement code |
| `tools/cli/bpsai_pair/core/` | Core CLI infrastructure |
| `.paircoder/config.yaml` | Project configuration |
| `CLAUDE.md` | Claude-specific instructions |
| `AGENTS.md` | Universal AI agent entry point |

### Tier 3: Read-write Paths

Everything not in Tier 1 or 2 has full read-write access. This is the "working area" where Claude can:
- Write and modify source code
- Create and update tests
- Modify documentation (except protected files)
- Update state.md and task files

---

## Network Restrictions

In containment mode, network access is restricted to an allowlist. This prevents data exfiltration and limits interaction to known, trusted services.

### Default Allowed Domains

| Domain | Purpose |
|--------|---------|
| `api.anthropic.com` | Claude API calls |
| `api.trello.com` | Trello integration |
| `github.com` | Git operations |
| `pypi.org` | Python package information |

### Adding Domains

To allow additional domains, add them to `allow_network` in config:

```yaml
containment:
  allow_network:
    - api.anthropic.com
    - api.trello.com
    - github.com
    - pypi.org
    - api.your-service.com    # Add custom domain
```

---

## Checkpoints and Rollback

Containment mode automatically creates git checkpoints for safe rollback.

### Automatic Checkpoints

When entering containment mode with `bpsai-pair contained-auto`:
1. Current HEAD commit is tagged with `containment-YYYYMMDD-HHMMSS`
2. Any uncommitted changes are stashed
3. Checkpoint tag serves as rollback point

### Listing Checkpoints

```bash
# List all containment checkpoints
bpsai-pair containment checkpoints

# Or via git
git tag -l "containment-*"
```

### Rolling Back

```bash
# Rollback to most recent checkpoint
bpsai-pair containment rollback

# Rollback to specific checkpoint
bpsai-pair containment rollback --checkpoint containment-20260113-140000

# Manual rollback via git
git reset --hard containment-20260113-140000
```

### Rollback Preview

```bash
# Preview what would be reverted
bpsai-pair containment rollback --preview
```

This shows:
- Number of commits to revert
- Files that will be changed

### Disabling Auto-Checkpoint

```yaml
containment:
  auto_checkpoint: false
```

Or skip checkpoint for a single session:
```bash
bpsai-pair contained-auto --skip-checkpoint
```

---

## CLI Commands

### `bpsai-pair contained-auto`

Enter contained autonomy mode with full autonomous capabilities.

```bash
# Basic usage
bpsai-pair contained-auto

# Skip git checkpoint
bpsai-pair contained-auto --skip-checkpoint

# Use permissive mode (warnings only)
bpsai-pair contained-auto --permissive
```

### `bpsai-pair containment status`

Show current containment status and configuration.

```bash
bpsai-pair containment status
```

Output shows:
- Whether containment is active
- Current mode (strict/permissive)
- Protected paths by tier
- Allowed network domains
- Active checkpoint (if any)

### `bpsai-pair containment rollback`

Rollback to a checkpoint.

```bash
# Rollback to most recent
bpsai-pair containment rollback

# Rollback to specific checkpoint
bpsai-pair containment rollback --checkpoint <tag>

# Preview only (don't execute)
bpsai-pair containment rollback --preview
```

### `bpsai-pair containment checkpoints`

List all containment checkpoints.

```bash
bpsai-pair containment checkpoints
```

---

## FAQ

### When should I use contained mode?

**Use contained mode when:**
- Running Claude Code autonomously for extended periods
- Executing implementation tasks without constant supervision
- Working on tasks that don't require modifying enforcement code
- Testing autonomous workflow features

**Don't use contained mode when:**
- You need to modify skills, agents, or commands
- Updating CLAUDE.md or AGENTS.md
- Working on security or core infrastructure
- Debugging containment issues

### Can I add my own protected paths?

Yes! Add them to the appropriate list in `config.yaml`:

```yaml
containment:
  # Add to blocked_files for secrets
  blocked_files:
    - .env
    - my-secret-file.key

  # Add to readonly_directories for enforcement code
  readonly_directories:
    - .claude/skills
    - my-custom-enforcement/
```

### What if Claude needs to modify a protected file?

You have three options:

1. **Exit containment mode** - Run normal `claude` command instead of `contained-auto`
2. **Temporarily adjust config** - Remove the path from protection
3. **Manual edit** - Make the change yourself, then return to containment

### How do I disable containment entirely?

```yaml
containment:
  enabled: false
```

### Does strict containment require Docker?

**Yes.** Strict containment mode requires Docker to enforce filesystem protections:

- **Strict mode** (requires Docker) = OS-level read-only mounts that Claude cannot bypass
- **Advisory mode** (no Docker) = Python-level warnings only, no actual enforcement

Without Docker installed, containment falls back to advisory mode which **logs warnings but cannot prevent writes**. For real security, Docker must be available.

**Note:** The Docker sandbox (command isolation) and containment (filesystem protection) both use Docker but serve different purposes. Containment mounts paths as read-only; the command sandbox isolates untrusted command execution.

### What happens on a violation in strict mode?

1. The operation is blocked immediately
2. `ContainmentViolationError` is raised
3. Error message indicates what path was blocked
4. The checkpoint remains available for rollback

### Are glob patterns supported?

Yes, for directories. You can use glob patterns like:

```yaml
containment:
  readonly_directories:
    - .claude/**/          # All subdirectories under .claude
    - protected/**/config/ # All config dirs under protected
```

---

## Troubleshooting

### "Cannot modify locked path" Error

**Symptom**: Claude reports it cannot write to a file.

**Cause**: The path is in `blocked_files`, `blocked_directories`, `readonly_files`, or `readonly_directories`.

**Solution**:
1. Check if the file should be protected:
   ```bash
   bpsai-pair containment status
   ```
2. If protection is intentional, exit containment mode to make the change
3. If protection is unintended, update `config.yaml` to remove the path

### "Cannot read blocked path" Error

**Symptom**: Claude reports it cannot read a file.

**Cause**: The path is in `blocked_files` or `blocked_directories` (Tier 1).

**Solution**: Blocked paths cannot be read in containment mode. Either:
- Exit containment mode
- Remove the path from blocked lists if it shouldn't be blocked

### Network Restriction Errors

**Symptom**: Network requests fail or timeout.

**Cause**: The domain isn't in `allow_network`.

**Solution**: Add the domain to allowed list:
```yaml
containment:
  allow_network:
    - api.anthropic.com
    - your-domain.com
```

### Checkpoint Rollback Issues

**Symptom**: `bpsai-pair containment rollback` fails.

**Possible causes**:
1. No checkpoint exists - was `--skip-checkpoint` used?
2. Git repository is in detached HEAD state
3. Checkpoint tag was manually deleted

**Solutions**:
```bash
# List available checkpoints
git tag -l "containment-*"

# If tag exists, manual rollback
git reset --hard containment-YYYYMMDD-HHMMSS

# If no checkpoint, check git reflog
git reflog
```

### Stashed Changes Not Restored

**Symptom**: Uncommitted changes are missing after rollback.

**Cause**: Auto-stash was performed but not popped.

**Solution**:
```bash
# List stashes
git stash list

# Pop the containment stash
git stash pop
```

### Permissive Mode Warnings Being Ignored

**Symptom**: Violations are logged but not acted upon.

**Cause**: You're in permissive mode which only warns.

**Solution**: Switch to strict mode for enforcement:
```yaml
containment:
  mode: strict
```

---

## Security Considerations

### What Containment Does NOT Protect Against

- **Malicious code execution**: Claude can still run arbitrary commands
- **External network access**: Only domain filtering, not content inspection
- **Memory/process isolation**: Use Docker sandbox for that
- **Git history manipulation**: Checkpoint tags can be deleted

### Defense in Depth

For maximum security, combine:
1. **Containment** - Filesystem access control
2. **Docker sandbox** - Process isolation
3. **Budget limits** - Token/cost constraints
4. **Audit logging** - Track all operations

### Audit Trail

Containment violations are logged to `.paircoder/history/containment_log.jsonl`:

```json
{
  "timestamp": "2026-01-13T14:00:00",
  "action": "write_blocked",
  "path": ".claude/skills/my-skill/SKILL.md",
  "tier": "readonly",
  "checkpoint": "containment-20260113-140000"
}
```

---

## Related Documentation

- [User Guide](../.paircoder/docs/USER_GUIDE.md) - Full PairCoder documentation
- [Security Guide](../.paircoder/docs/SECURITY.md) - Security features overview
- [Claude Code Integration](CLAUDE_CODE_INTEGRATION.md) - How PairCoder works with Claude Code

---

*PairCoder v2.9.1 - MIT License*
