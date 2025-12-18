# Current State

> Last updated: 2025-12-17

## Active Plan

**Plan:** `plan-2025-12-sprint-16-real-subagents`
**Status:** in_progress
**Current Sprint:** sprint-16 (Real Sub-agents)

**Previous:** `plan-2025-12-sprint-15-security-sandboxing` (complete)

## Current Focus

Sprint 16: Real Sub-agents - making `bpsai-pair orchestrate task` route to appropriate agents.

**Key Objectives:**
- Agent invocation framework (base class for invoking sub-agents)
- Planner agent implementation
- Reviewer agent implementation
- Security agent implementation
- Agent handoff protocol
- Agent selection logic

## Task Status

### Sprint 1-12: Archived

See `.paircoder/history/sprints-1-12-archive.md` for historical details.

### Sprint 13: Full Autonomy - COMPLETE

All tasks completed. See Sprint 13 section in archive.

### Sprint 14: Trello Deep Integration - COMPLETE

All 8 tasks completed:
- TASK-081: Sync Trello custom fields ✓
- TASK-082: Sync Trello labels with exact BPS colors ✓
- TASK-083: Card description templates (BPS format) ✓
- TASK-084: Effort → Trello Effort field mapping ✓
- TASK-085: Two-way sync (Trello → local) ✓
- TASK-086: Support checklists in cards ✓
- TASK-087: Due date sync ✓
- TASK-088: Activity log comments ✓

### Sprint 15: Security & Sandboxing - COMPLETE ✅

All 7 tasks completed (250/250 points).

### Sprint 16: Real Sub-agents - IN PROGRESS

| Task | Title | Status | Priority | Complexity |
|------|-------|--------|----------|------------|
| TASK-096 | Agent invocation framework | **done** | P0 | 45 |
| TASK-097 | Planner agent implementation | **done** | P1 | 35 |
| TASK-098 | Reviewer agent implementation | pending | P1 | 35 |
| TASK-099 | Security agent implementation | pending | P0 | 40 |
| TASK-100 | Agent handoff protocol | pending | P1 | 40 |
| TASK-101 | Agent selection logic | pending | P0 | 30 |

**Progress:** 2/6 tasks complete (80/225 points)

### Backlog (Deprioritized)

Tasks in `.paircoder/tasks/backlog/`:
- TASK-063: VS Code extension
- TASK-064: Status bar widget
- TASK-065: Auto-context on save
- TASK-074: Dashboard UI
- TASK-075: Slack notifications
- TASK-076: Multi-project support

## What Was Just Done

### Session: 2025-12-17 - TASK-097: Planner Agent Implementation

**TASK-097: Planner Agent Implementation** - DONE

Created the PlannerAgent for design and planning tasks:

**New file:** `tools/cli/bpsai_pair/orchestration/planner.py`
- `PlanPhase` dataclass - represents a phase in the implementation plan
- `PlanOutput` dataclass - structured plan with summary, phases, files, complexity, risks
- `PlanOutput.from_raw_text()` - parses markdown output into structured data
- `PlannerAgent` class - invokes planner via AgentInvoker framework
- `should_trigger_planner()` - trigger conditions for routing
- `invoke_planner()` - convenience function for one-shot planning

**Features:**
- Loads `.claude/agents/planner.md` via AgentInvoker
- Always operates in read-only `plan` permission mode
- Builds context from task description + project context + relevant files
- Returns structured `PlanOutput` with phases, files, complexity
- Parses markdown output into structured plan data

**Updated files:**
- `orchestration/__init__.py` - exports planner classes
- `orchestration/orchestrator.py` - added `_execute_with_planner()` method
- `mcp/tools/orchestration.py` - added `paircoder_orchestrate_plan` MCP tool

**Tests:** 23 tests in `test_planner_agent.py`

---

### Session: 2025-12-17 - TASK-096: Agent Invocation Framework

**TASK-096: Agent Invocation Framework** - DONE

Created the agent invocation framework for Sprint 16:

**New file:** `tools/cli/bpsai_pair/orchestration/invoker.py`
- `AgentDefinition` dataclass - parses YAML frontmatter from .claude/agents/*.md
- `InvocationResult` dataclass - structured result with output, tokens, cost
- `AgentInvoker` class - loads agent definitions and invokes via HeadlessSession
- `invoke_agent()` convenience function for one-shot invocations

**Features:**
- Loads agent definitions from `.claude/agents/{name}.md`
- Parses YAML frontmatter (name, description, model, permissionMode, tools)
- Extracts system prompt from markdown body
- Invokes agents via `HeadlessSession` with correct permission mode
- Caches loaded agents for performance
- Supports handoff context between agents

**Updated:** `tools/cli/bpsai_pair/orchestration/__init__.py`
- Exports `AgentDefinition`, `AgentInvoker`, `InvocationResult`, `invoke_agent`

**Tests:** 24 tests in `test_invoker.py`

---

### Session: 2025-12-17 - Sprint 16 Plan Creation

Created Sprint 16: Real Sub-agents plan and synced to Trello:
- Created plan file: `sprint-16-real-subagents.plan.yaml`
- Created task files: TASK-096 to TASK-101
- Created sprint-16 list on Trello board
- Synced 6 cards to Trello

---

### Session: 2025-12-17 - TASK-095: Dependency Vulnerability Scan

**TASK-095: Dependency Vulnerability Scan** - DONE

Implemented dependency vulnerability scanning:

**New file:** `tools/cli/bpsai_pair/security/dependencies.py`
- `DependencyScanner` class for scanning Python and npm dependencies
- `Vulnerability` dataclass for detected CVEs
- `ScanReport` dataclass with severity analysis
- `Severity` enum with comparison operators

**Features:**
- Python scanning via pip-audit (requirements.txt, pyproject.toml)
- npm scanning via npm audit (package.json)
- Result caching for performance (configurable TTL)
- Severity filtering (--fail-on option)
- Verbose and JSON output formats

**CLI commands:**
- `bpsai-pair scan-deps [path]` - Scan dependencies
- `bpsai-pair scan-deps --fail-on high` - Fail on high+ severity
- `bpsai-pair scan-deps --verbose` - Show detailed CVE info
- `bpsai-pair scan-deps --json` - JSON output for CI

**Tests:** 37 tests in `test_security_dependencies.py`

**Sprint 15 Complete!** All 7 security tasks done (250/250 points).

---

### Session: 2025-12-17 - TASK-094: Secret Detection

**TASK-094: Secret Detection** - DONE

Implemented pre-commit secret scanning:

**New file:** `tools/cli/bpsai_pair/security/secrets.py`
- `SecretScanner` class with comprehensive pattern matching
- `SecretMatch` dataclass for detected secrets with redaction
- `SecretType` enum for categorizing secrets
- `AllowlistConfig` for false positive suppression

**Secret patterns supported:**
- AWS credentials (access keys, secret keys)
- GitHub tokens (PAT, OAuth, fine-grained)
- Slack tokens and webhooks
- Private keys (RSA, SSH, EC, DSA, PGP)
- JWT tokens
- Database connection strings
- Stripe keys (live and test)
- SendGrid keys
- Google API keys
- Generic patterns (api_key, password, secret, token)

**Scanning modes:**
- `scan_file()` - Scan individual files
- `scan_diff()` - Scan git diff output
- `scan_staged()` - Scan staged git changes
- `scan_commit_range()` - Scan commits since reference
- `scan_directory()` - Recursive directory scanning

**CLI commands:**
- `bpsai-pair scan-secrets [path]` - Scan files/directories
- `bpsai-pair scan-secrets --staged` - Scan staged changes
- `bpsai-pair scan-secrets --diff HEAD~1` - Scan since commit
- `bpsai-pair security pre-commit` - Pre-commit hook mode
- `bpsai-pair security install-hook` - Install git hook

**Configuration:**
- `.paircoder/security/secret-allowlist.yaml` - Allowlist config
- Supports pattern-based allowlisting
- File path exclusions
- Ignore patterns for false positives

**Tests:** 52 tests in `test_security_secrets.py`

---

### Session: 2025-12-17 - Documentation Audit & Changelog Update

**Documentation Audit Complete:**
- Audited README.md, CONTRIBUTING.md, USER_GUIDE.md, FEATURE_MATRIX.md, docs/SECURITY.md
- Fixed outdated reference to `scripts/ci_local.sh` → `bpsai-pair ci` in CONTRIBUTING.md
- Updated test counts from 412 to 541+ across all documentation
- Added Sprint 14 and Sprint 15 features to FEATURE_MATRIX.md
- Updated docs/SECURITY.md to mark completed Sprint 15 tasks
- Updated ROADMAP-SPRINTS-14-20.md with current status

**CHANGELOG.md Updated:**
- v2.5.1: Sprint 14 (Trello Deep Integration) - 8 tasks
- v2.5.2: Sprint 15 (Security & Sandboxing) - 5 tasks done
- v2.5.3: Unreleased (remaining Sprint 15 tasks)

---

### Session: 2025-12-17 - Sprint 15 Progress (5 tasks complete)

**TASK-093: Git Checkpoint/Rollback** - DONE

Implemented automatic git checkpointing and rollback:

**New file:** `tools/cli/bpsai_pair/security/checkpoint.py`
- `GitCheckpoint` class with full checkpoint management
- `create_checkpoint(message)` - Creates tagged checkpoint at HEAD
- `rollback_to(checkpoint)` - Rolls back with optional stash
- `rollback_to_last()` - Rolls back to most recent checkpoint
- `list_checkpoints()` - Lists all checkpoints with metadata
- `preview_rollback()` - Shows what would be reverted
- `cleanup_old_checkpoints()` - Retention policy enforcement
- `is_dirty()` - Check for uncommitted changes

**Error handling:**
- `CheckpointError`, `NotAGitRepoError`, `CheckpointNotFoundError`, `NoCheckpointsError`

**CLI formatting:**
- `format_checkpoint_list()` - For `bpsai-pair rollback` display
- `format_rollback_preview()` - For `--preview` mode

**Tests:** 20 tests in `test_security_checkpoint.py`

---

**TASK-092: Docker Sandbox Runner** - DONE

Execute commands in isolated Docker containers:

**New file:** `tools/cli/bpsai_pair/security/sandbox.py`
- `SandboxConfig` - Configuration (image, memory, CPU, network)
- `SandboxRunner` - Execute commands in containers
- `SandboxResult` - Results with file change tracking
- `FileChange` - Track created/modified/deleted files
- `MountConfig` - Volume mount configuration

**Features:**
- Network isolation (default: none)
- Resource limits (memory, CPU)
- Environment variable passthrough
- Automatic container cleanup
- File change detection via `container.diff()`

**New file:** `tools/cli/bpsai_pair/security/Dockerfile`
- Python 3.12-slim base with dev tools
- Non-root `sandbox` user for security

**New file:** `.paircoder/security/sandbox.yaml`
- Configuration template with all options

**Tests:** 35 tests in `test_security_sandbox.py`

---

**TASK-091: Pre-execution Security Review** - DONE

Security review before command execution:

**New file:** `tools/cli/bpsai_pair/security/review.py`
- `ReviewResult` - Result dataclass with allow/block/warn
- `SecurityReviewHook` - Pre-execution command review
- `CodeChangeReviewer` - Scan code for vulnerabilities

**Secret detection patterns:**
- API keys, passwords, AWS credentials
- Private keys, GitHub/Slack tokens, JWTs
- Database connection strings

**Injection vulnerability patterns:**
- SQL injection (f-strings in queries)
- Command injection (os.system, subprocess shell=True)
- Path traversal

**New file:** `.claude/hooks/security-review.md`
- Documentation for hook integration

**Tests:** 35 tests in `test_security_review.py`

---

**TASK-090: Command Allowlist System** - DONE

Safe vs unsafe command classification:

**New file:** `tools/cli/bpsai_pair/security/allowlist.py`
- `AllowlistManager` - Command classification
- `CommandDecision` - ALLOW, REVIEW, BLOCK
- `CheckResult` - Full result with reason and matched rule

**Default classifications:**
- Always allowed: git status, pytest, ls, cat, bpsai-pair
- Require review: git push, pip install, docker
- Always blocked: rm -rf /, curl | bash, sudo rm

**Pattern matching:**
- Regex patterns for complex commands
- Wildcard support in allowlist
- Configurable via `.paircoder/security/allowlist.yaml`

**Tests:** 39 tests in `test_security_allowlist.py`

---

**TASK-089: Security Agent Definition** - DONE

Created `.claude/agents/security.md`:
- Pre-execution security gatekeeper role
- Block vs warn conditions defined
- Security checklist for code/commands/git
- SOC2 control references (CC6.1, CC6.6, CC7.1, etc.)
- Output formats for BLOCKED/WARNING/ALLOWED

Also created:
- `.claude/hooks/security-review.md` - Hook integration docs
- `docs/SECURITY.md` - Security features documentation

## What's Next

**Sprint 16 in progress!**

Next tasks (in order):
1. TASK-101: Agent selection logic - Route tasks to appropriate agent
2. TASK-097: Planner agent implementation - Wire planner for design tasks
3. TASK-098: Reviewer agent implementation - Wire reviewer for code review
4. TASK-099: Security agent implementation - Wire security as gatekeeper
5. TASK-100: Agent handoff protocol - Context passing between agents

## Sprint 15 Success Criteria

- [x] Security agent reviews commands before execution
- [x] Dangerous commands blocked with explanation
- [x] Docker sandbox provides isolated execution
- [x] Git checkpoints enable rollback
- [ ] Can run autonomous session without `--dangerously-skip-permissions`
- [x] No secrets in any commits (secret scanning implemented)
- [x] Dependencies scanned for vulnerabilities

## Test Coverage

- **Total tests**: 218 security tests + existing tests
- **Security module tests**:
  - test_security_allowlist.py: 39 tests
  - test_security_review.py: 35 tests
  - test_security_sandbox.py: 35 tests
  - test_security_checkpoint.py: 20 tests
  - test_security_secrets.py: 52 tests
  - test_security_dependencies.py: 37 tests
- **Test command**: `pytest -v`

## Blockers

None currently.
