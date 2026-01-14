# PairCoder Q1 2026 Sprint Plans

> **Living Document** - Updated as sprints progress
> Last Updated: 2026-01-14
> Target: v2.9.0 → v3.0.0

---

## Executive Summary

### Vision

**v3.0: Constraint-Based AI Pair Programming**

PairCoder enforces structured workflows through deterministic Python gates rather than relying on AI instruction-following. The core philosophy: **"Claude codes, Python enforces."**

```
USER INVOKES SLASH COMMAND
         ↓
CLAUDE ENTERS ROLE (in container)
         ↓
CLI COMMANDS ENFORCE BEHAVIOR
         ↓
PYTHON MODULES DO HEAVY LIFTING
         ↓
GATES BLOCK BAD OUTCOMES
         ↓
CLAUDE CAN'T EDIT ENFORCEMENT CODE
```

### Current Status

| Metric | Value |
|--------|-------|
| CLI Commands | 127+ |
| Passing Tests | 2,149+ |
| Current Version | v2.9.1 |
| Active Sprint | 29.1 (Hotfixes) |

### Sprint Overview

| Sprint | Focus | Version | Status | Outcome |
|--------|-------|---------|--------|---------|
| 27 | Stabilization | 2.8.4   | ✅ Complete | CI green, upgrade works |
| 28 | Enforcement Wiring | 2.9.0   | ✅ Complete | Gates block bypass attempts |
| 29.0 | Contained Autonomy | 2.9.1   | ✅ Complete | Docker-based containment |
| 29.1 | Hotfixes | 2.9.2   | ✅ Complete | Bug fixes, PR review items |
| 29.2 | Comprehensive Audit | 2.9.2   | 📋 Planned | Know what works |
| 29.3 | EPIC-005 Refactor | 2.9.3   | 🔧 Planned | Clean architecture |
| 29.4 | Remediation | 2.9.4   | 🩹 Planned | Fix audit findings |
| 30 | UX Wizard | 2.10.0  | ✨ Planned | FastAPI setup wizard |
| 30.5 | Feedback Loop | 2.10.1  | 📊 Planned | Token estimation calibration |
| 31 | Multi-Project Workspace | 2.11.0  | 🔗 Planned | EPIC-001: Cross-repo |
| 32 | Trello-Native P1 | 2.12.0  | 🚀 Planned | Epic→Story→Task hierarchy |
| 33 | Trello-Native P2 | 2.13.0  | 🚀 Planned | Two-way sync |
| 34 | Release Prep | 2.14.0  | 📦 Planned | Polish, documentation |
| 35 | Remote Access | 3.0.0   | 🌐 Planned | "Untethered" Release |

### Version Philosophy

```
2.8.x  - Stabilization (complete)
2.9.x  - Enforcement + Containment + Code Quality
  2.9.0 - Enforcement Wiring ✅
  2.9.1 - Contained Autonomy ✅
  2.9.2 - Hotfixes & Comprehensive Audit ✅
  2.9.3 - EPIC-005 Refactor  
  2.9.4 - Audit Remediation

--- FEATURE FREEZE: Clean codebase achieved ---

2.10.x - UX Improvements
  2.10.0 - Web Wizard
  2.10.1 - Feedback Loop (token calibration)
2.11.x - Multi-Project Workspace (EPIC-001)
2.12.x - Trello-Native Phase 1 (hierarchy)
2.13.x - Trello-Native Phase 2 (two-way sync)
2.14.x - Release prep, polish

3.0.0  - 🚀 REMOTE ACCESS - The "Untethered" Release
         Control PairCoder from anywhere:
         - MCP server for remote commands
         - API for external integrations
         - Claude Desktop / App / Voice
```

### Milestone Requirements

**v2.10.0 - Usable by Non-Technical Users:**
- [x] Enforcement gates functional
- [x] Contained autonomy mode
- [ ] Web-based setup wizard
- [ ] Trello flat-mode stable

**v2.14.0 - Full BPS Workflow:**
- [ ] Multi-project workspace (EPIC-001)
- [ ] Trello-Native Mode complete
- [ ] Cross-repo impact analysis
- [ ] All BPS conventions supported

**v3.0.0 - Untethered Developer:**
- [ ] Remote access via MCP/API
- [ ] Control from Claude Desktop/App
- [ ] Background task execution
- [ ] Notification on completion/blocker

---

## Completed Sprints

### Sprint 27: Stabilization ✅

**Version:** 2.8.4
**Status:** Complete

- CI pipeline stable
- Upgrade command functional
- Cookiecutter template synced

### Sprint 28: Enforcement Wiring ✅

**Version:** 2.9.0
**Status:** Complete

Key deliverables:
- `ttask done` requires acceptance criteria verification
- `task update` blocked for Trello-linked tasks
- Budget check on task start
- Bypass audit logging to `bypass_log.jsonl`
- State machine commands (`state show/list/history/reset/advance`)

### Sprint 29.0: Contained Autonomy ✅

**Version:** 2.9.1
**Status:** Complete

Key deliverables:
- Docker-based containment with three-tier access control
- `bpsai-pair contained-auto` command
- Network allowlist via iptables
- Git checkpoint on container entry
- Auto-pull from Docker Hub (`bpsai/paircoder-containment`)
- Comprehensive documentation

---

## Current Sprint

### Sprint 29.1: Hotfixes ✅ 

**Version:** 2.9.2 (patch)
**Status:** In Progress

Addressing items from PR review and testing:

| ID      | Task                                      | Status | Notes                                |
|---------|-------------------------------------------|--------|--------------------------------------|
| T29.1.1 | Fix exec exit code with network allowlist | ✅ | Return exec code, not container code |
| T29.1.2 | Fix stash pop using specific ref          | ✅ | Pop correct stash entry              |
| T29.1.3 | Mount ~/.claude/ for credentials          | ✅ | Persist auth in container            |
| T29.1.4 | Simplify containment Dockerfile           | ✅ | Reduce vulnerabilities               |
| T29.1.5 | Patch UTF encoding issues project wide    | ✅ | Enable seamless multi-os operations  |

---

## Planned Sprints

### Sprint 29.2: Comprehensive Audit 📋

**Goal:** Systematic audit of all functionality before building new features

**Target:** v2.9.2 (Audit Only)
**Effort:** ~24-32 hours

#### Scope

| Area | Questions to Answer |
|------|---------------------|
| CLI Commands | Do all 127+ commands work? |
| Modules | Which are stale or unused? |
| Config Fields | What's documented vs. actually used? |
| Enforcement | Are gates actually blocking? |
| First-Run | What breaks on fresh install? |
| Documentation | Does FEATURE_MATRIX match reality? |
| MCP Server | Is it current with CLI? |
| Test Coverage | What's not tested? |

#### Deliverables

- [ ] Audit report with findings
- [ ] Dead code inventory
- [ ] Prioritized fix list
- [ ] Documentation gap analysis
- [ ] Wizard requirements (which config fields matter)

---

### Sprint 29.3: EPIC-005 CLI Module Decomposition 🔧

**Goal:** Extract monolithic command files into focused, maintainable modules

**Target:** v2.9.3 (Post Audit Findings)
**Effort:** ~26 hours

#### The Problem

Two command files exceed maintainable size:
- `planning/commands.py` - 2,119 lines
- `trello/task_commands.py` - 965 lines

#### Target Structure

```
bpsai_pair/
├── enforcement/                # Centralized enforcement
│   ├── gates.py               # can_complete(), check_bypass_allowed()
│   ├── config.py              # Load enforcement.* settings
│   └── audit.py               # Bypass logging
├── commands/
│   ├── plan.py                # plan new/list/show/tasks/estimate
│   ├── task.py                # task list/show/update/next/archive
│   ├── intent.py              # intent detect/should-plan
│   └── standup.py             # standup generate/post
└── trello/
    ├── commands.py            # trello connect/boards/lists
    └── task_commands.py       # ttask list/show/start/done
```

#### Tasks

| Phase | Focus | Effort |
|-------|-------|--------|
| 1 | Extract enforcement module | ~8h |
| 2 | Split planning/commands.py | ~12h |
| 3 | Cleanup and testing | ~6h |

#### Success Criteria

- [ ] No command file exceeds 500 lines
- [ ] All enforcement logic centralized
- [ ] IDE warnings reduced by 50%+
- [ ] All existing tests pass
- [ ] Zero CLI interface changes

---

### Sprint 29.4: Triage & Remediation 🩹

**Goal:** Fix issues identified in audit, apply refactor learnings

**Target:** v2.9.4 (Post Audit Findings)
**Effort:** TBD (depends on audit findings)

#### Scope

- Fix broken/stale commands identified in 29.2
- Remove confirmed dead code
- Update stale modules (MCP, upgrade, etc.)
- Ensure enforcement gates function correctly
- Sync documentation with reality
- First-run experience fixes

#### Deliverables

- [ ] All audit findings addressed or documented as known issues
- [ ] FEATURE_MATRIX.md accurate
- [ ] MCP server current with CLI
- [ ] Clean first-run experience

---

### Sprint 30: UX + Web Wizard ✨

**Goal:** FastAPI-based setup wizard for accessible onboarding

**Target:** v2.10.0
**Effort:** ~36 hours

#### The Vision

```bash
$ bpsai-pair wizard
🌐 Opening setup wizard at http://localhost:8765
```

A web UI guides users through:
1. **Welcome** - What is PairCoder?
2. **Project Setup** - Name, preset selection with previews
3. **Integrations** - Trello, GitHub (skippable)
4. **Security** - Containment mode, network allowlist
5. **Review & Create** - Preview generated files
6. **Next Steps** - First commands to try

#### Key Features

- **Re-runnable** - Update existing config, not just create
- **Conditional flows** - Skip sections not needed
- **Preview before write** - See YAML before committing
- **Validation** - Check existing config for issues

#### Tech Stack

```
FastAPI + Jinja2 + htmx
- No heavy frontend framework
- Works offline (localhost)
- Single pip install
- Auto-opens browser
```

#### Acceptance Criteria

- [ ] `bpsai-pair wizard` starts local server
- [ ] Non-technical user completes setup in <10 minutes
- [ ] Trello connection optional and skippable
- [ ] All config fields accessible
- [ ] Re-run mode for updates

---

### Sprint 30.5: Feedback Loop 📊

**Goal:** Close the estimation feedback loop using Claude Code session data

**Target:** v2.10.1
**Effort:** ~14 hours

#### Context

Claude Code stores session data in `~/.claude/` including token usage per message. By comparing estimates against actuals, PairCoder can auto-calibrate its estimation coefficients.

#### CLI Commands

```bash
# Import sessions
bpsai-pair session import --all
bpsai-pair session import --since 7d

# View accuracy
bpsai-pair budget accuracy
bpsai-pair budget accuracy --sprint 28

# Calibrate
bpsai-pair budget calibrate --apply
```

#### Acceptance Criteria

- [ ] Sessions imported from ~/.claude/
- [ ] Auto-linked to tasks via history.jsonl patterns
- [ ] Accuracy report shows estimated vs actual
- [ ] Calibration updates config.yaml coefficients

---

### Sprint 31: Multi-Project Workspace 🔗 (EPIC-001)

**Goal:** Contract-aware cross-repo support

**Target:** v2.11.0
**Effort:** ~62 hours

#### The Problem

Multi-repo projects suffer from:
- Breaking API changes affecting consumers
- Message schema changes breaking workers
- Duplicated types drifting out of sync
- Manual coordination required before merge

#### The Solution

```yaml
# .paircoder-workspace.yaml
projects:
  api:
    path: ./api-server
    contracts:
      openapi: ./contracts/openapi.json
  frontend:
    path: ./client-app
    consumes:
      - project: api
        contract: openapi
```

When Claude changes an API endpoint:
1. Detects the contract change
2. Finds all consumers
3. Warns before commit if breaking
4. Generates PR impact summary

---

### Sprint 32-33: Trello-Native Mode 🚀 (EPIC-002)

**Goal:** Full Trello automation with Epic→Story→Task hierarchy

**Target:** v2.12.0 - v2.13.0

#### Phase 1 (Sprint 32)
- Epic card creation with nested Stories/Tasks
- Card Relationships API integration
- Butler trigger simulation

#### Phase 2 (Sprint 33)
- Two-way sync from Trello
- Auto-generate state.md from board
- Webhook-triggered local updates

---

### Sprint 34: Release Prep 📦

**Goal:** Polish and documentation for v3.0 foundation

**Target:** v2.14.0

- [ ] Documentation comprehensive and accurate
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] All local features stable

---

### Sprint 35: Remote Access 🌐 (v3.0)

**Goal:** Control PairCoder from anywhere

**Target:** v3.0.0

```
You're at dinner. Your phone buzzes.

Claude: "I finished the webhook feature. 
        PR #47 ready for review. All tests passing.
        Want me to request review from Kevin?"

You: "Yes, and start on the next task."

Claude: "Starting T26.3. I'll notify you when done."
```

#### Architecture

```
Claude Desktop/App
    │
    ├── MCP (when on same network)
    │    └── Local PairCoder
    │
    └── Cloud Relay (when remote)
         └── Secure tunnel to dev machine
```

---

## Dependencies Graph

```
Sprint 27 (Stabilization) - v2.8.4 ✅
    │
Sprint 28 (Enforcement) - v2.9.0 ✅
    │
Sprint 29.0 (Contained Autonomy) - v2.9.1 ✅
    │
Sprint 29.1 (Hotfixes) - v2.9.1 🔄
    │
Sprint 29.2 (Audit) - v2.9.2
    │
    └── Findings inform →
                        │
Sprint 29.3 (Refactor) - v2.9.3
    │                   │
    └── Clean code enables →
                            │
Sprint 29.4 (Remediation) - v2.9.4
    │
    └── Stable foundation
                │
    ┌───────────┴───────────┐
    │                       │
Sprint 30               Sprint 30.5
(Wizard)                (Feedback Loop)
v2.10.0                 v2.10.1
    │                       │
    └───────────┬───────────┘
                │
Sprint 31 (Multi-Project) - v2.11.0
    │
Sprint 32 (Trello P1) - v2.12.0
    │
Sprint 33 (Trello P2) - v2.13.0
    │
Sprint 34 (Release Prep) - v2.14.0
    │
Sprint 35 (Remote Access) - v3.0.0 🚀
```

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Audit reveals major issues | HIGH | MEDIUM | Budget time in 29.4 for fixes |
| Refactor breaks functionality | HIGH | LOW | Comprehensive test suite |
| Wizard scope creep | MEDIUM | MEDIUM | MVP first, enhance later |
| MCP protocol changes | MEDIUM | LOW | Abstract behind interface |
| Remote access security | HIGH | MEDIUM | Security audit before v3.0 |

---

## Success Metrics

### Sprint 29.2 Success (Audit)
- [ ] All 127+ commands verified (working/broken/unused)
- [ ] Config field usage documented
- [ ] Dead code identified
- [ ] First-run issues catalogued

### Sprint 29.3 Success (Refactor)
- [ ] No file exceeds 500 lines
- [ ] Enforcement centralized
- [ ] All tests passing
- [ ] Zero interface changes

### Sprint 29.4 Success (Remediation)
- [ ] All critical audit findings fixed
- [ ] Documentation accurate
- [ ] Clean first-run experience
- [ ] MCP server current

### Sprint 30 Success (Wizard)
- [ ] Wizard launches at localhost
- [ ] Setup completes in <10 minutes
- [ ] Re-run mode works
- [ ] All config fields accessible

### Sprint 35 Success (v3.0.0) 🎉
- [ ] MCP server handles all commands
- [ ] Control from Claude Desktop works
- [ ] Background tasks functional
- [ ] Notifications delivered

---

## Resource Requirements

### Human
- Primary Developer: Implementation
- Kevin: Testing, UX feedback
- Mike: Trello-Native validation

### Tools
- Docker: Containment development
- Real Trello board: Integration testing
- Fresh VM: First-run testing

### External Dependencies
- Docker Hub: Image hosting
- Trello API: Card Relationships, Butler
- GitHub API: PR integration

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-12-30 | Claude | Initial sprint plan |
| 2025-01-04 | Claude | Sprint 28 complete, updated structure |
| 2025-01-14 | Claude | Sprint 29.0 complete, added 29.1-29.4 quality sprints |
| 2025-01-14 | Claude | Moved Feedback Loop to 30.5, added Audit/Refactor/Remediation sequence |
