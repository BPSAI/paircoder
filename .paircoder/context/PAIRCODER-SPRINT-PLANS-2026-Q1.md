# PairCoder Q1 2025 Sprint Plans

> Consolidated from PAIRCODER-TRIAGE-2024-12-30.md and PAIRCODER-ENFORCEMENT-REMEDIATION.md
> Created: 2025-12-30
> Target: v2.9.0 - v3.0.0

---

## Executive Summary

### The Problem

PairCoder v2.8 has:
- 112 CLI commands
- 1,774 passing tests
- Sophisticated infrastructure for planning, enforcement, metrics, Trello sync

But Claude "does whatever he wants" because:
1. Enforcement exists but isn't wired up
2. Defaults favor convenience over safety
3. Claude can edit enforcement code to bypass constraints
4. Slash commands exist but don't enforce CLI usage

### The Vision

**v3.0: Constraint-Based PairCoder**

```
USER INVOKES SLASH COMMAND
         ↓
CLAUDE ENTERS ROLE (in sandbox)
         ↓
CLI COMMANDS ENFORCE BEHAVIOR
         ↓
PYTHON MODULES DO HEAVY LIFTING
         ↓
GATES BLOCK BAD OUTCOMES
         ↓
CLAUDE CAN'T EDIT ENFORCEMENT CODE
```

### Sprint Overview

| Sprint | Focus | Version | Effort | Outcome |
|--------|-------|---------|--------|---------|
| 27 | 🚨 Stabilization | 2.8.4 | ~22 hrs | CI green, upgrade works |
| 28 | 🔒 Enforcement | 2.9.0 | ~24 hrs | Constraints actually constrain |
| 29 | 🎯 Contained Autonomy | 2.9.1 | ~30 hrs | `claude666` safe mode |
| 30 | ✨ UX + Web Wizard | 2.10.0 | ~35 hrs | FastAPI setup wizard, Trello fixes |
| 31 | 🔗 Multi-Project Workspace | 2.11.0 | ~50 hrs | EPIC-001: Contract-aware cross-repo |
| 32 | 🚀 Trello-Native P1 | 2.12.0 | ~40 hrs | Epic→Story→Task hierarchy |
| 33 | 🚀 Trello-Native P2 | 2.13.0 | ~32 hrs | Two-way sync |
| 34 | 📦 Release Prep | 2.14.0 | ~20 hrs | Polish, documentation |
| 35 | 🌐 **REMOTE ACCESS** | **3.0.0** | ~60 hrs | API/MCP - "Untethered" Release |

**Total: ~313 hours → v3.0.0** (roughly 8 sprints)

### Version Philosophy

```
2.8.x  - Bug fixes, stabilization (current: 2.8.3)
2.9.x  - Enforcement wiring + contained autonomy
2.10.x - UX improvements + Web Wizard (FastAPI local UI)
2.11.x - Multi-Project Workspace (EPIC-001: contract-aware cross-repo)
2.12.x - Trello-Native Phase 1 (hierarchy)
2.13.x - Trello-Native Phase 2 (two-way sync)
2.14.x - Release prep, polish

3.0.0  - 🚀 REMOTE ACCESS - The "Untethered" Release
         Walk away from your dev machine. Control via:
         - MCP server for remote commands
         - API for external integrations
         - Claude Desktop / App / Voice
         - "Finish that feature" from your phone
```

### What's Required for Each Milestone

**v2.10.0 - Usable by Non-Technical Users:**
- [ ] Web-based setup wizard (FastAPI)
- [ ] Enforcement wired up
- [ ] Contained autonomy (`claude666`)
- [ ] Trello flat-mode working

**v2.14.0 - Full BPS Workflow:**
- [ ] Multi-project workspace (EPIC-001)
- [ ] Trello-Native Mode complete
- [ ] Cross-repo impact analysis
- [ ] All BPS conventions supported

**v3.0.0 - Untethered Developer:**
- [ ] Remote access via MCP/API
- [ ] Control from Claude Desktop/App
- [ ] Background task execution
- [ ] Notification when work complete
- [ ] The "walk away" experience

---

## Sprint 27: Stabilization 🚨

**Goal:** CI green, upgrade command works, no blocking bugs

**Start Date:** 2024-12-30
**Target:** v2.8.4

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T27.1 | Fix `template check` crash | K1 | 2h | - |
| T27.2 | Fix smoke test failure | K2 | 2h | - |
| T27.3 | Fix Unicode errors in Trello | K3 | 2h | - |
| T27.4 | Fix `upgrade` source file resolution | K13, K14 | 4h | - |
| T27.5 | Fix `upgrade` to actually copy files | K13 | 3h | T27.4 |
| T27.6 | Fix Windows hook compatibility (`|| true`) | K15 | 2h | - |
| T27.7 | Remove `/status` slash command (conflicts) | K5, CC2 | 1h | - |
| T27.8 | Update cookiecutter to v2.8 | A1, A2 | 2h | - |
| T27.9 | Sync skills to cookiecutter | A3 | 2h | T27.8 |
| T27.10 | Sync commands to cookiecutter | A5 | 1h | T27.8 |
| T27.11 | Sync agents to cookiecutter | A4 | 1h | T27.8 |

**Total Effort:** ~22 hours
**Complexity:** 180 points

### Acceptance Criteria

- [ ] `bpsai-pair template check` runs without crash
- [ ] `bpsai-pair smoke-test` passes
- [ ] Trello operations work with Unicode characters
- [ ] `bpsai-pair upgrade` copies skills, agents, commands, docs
- [ ] Hooks work on Windows (no `|| true`)
- [ ] No `/status` command in `.claude/commands/`
- [ ] Cookiecutter template matches v2.8 features
- [ ] CI pipeline green

### Deliverables

- [ ] v2.8.4 release
- [ ] Updated cookiecutter template
- [ ] K-Masty retest (upgrade flow)

---

## Sprint 28: Enforcement Wiring 🔒

**Goal:** Make existing enforcement code actually enforce

**Start Date:** After Sprint 27
**Target:** v2.9.0

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T28.1 | Make `--strict` default for `ttask done` | B3, R1.1 | 1h | - |
| T28.2 | Make `require_review=True` default | B1, R1.2 | 1h | - |
| T28.3 | Block `task update --status done` on Trello projects | B1 | 2h | - |
| T28.4 | Auto-update local task from `ttask done` | B1 | 2h | T28.3 |
| T28.5 | Wire budget `can_proceed()` before task start | R1.3 | 3h | - |
| T28.6 | Wire budget check into `/pc-plan` | R2.1 | 2h | T28.5 |
| T28.7 | Load routing config in `core/config.py` | R4.1 | 2h | - |
| T28.8 | Pass model to `HeadlessSession` | R4.3 | 2h | T28.7 |
| T28.9 | Create `/pc-done` slash command | K8 | 3h | T28.3, T28.4 |
| T28.10 | Add bypass audit logging | B4 | 2h | - |
| T28.11 | Remove unnecessary `--force` flags | B4 | 2h | T28.10 |
| T28.12 | Check `/review` conflict with Claude built-in | CC3 | 1h | - |
| T28.13 | Check `/security-review` conflict | CC4 | 1h | - |

**Total Effort:** ~24 hours
**Complexity:** 200 points

### Acceptance Criteria

- [ ] `ttask done` checks AC by default (no `--strict` needed)
- [ ] `autonomous.py` has `require_review=True` 
- [ ] `task update --status done` fails on Trello projects without `--force`
- [ ] `budget check` runs before task start
- [ ] `/pc-done` enforces full completion workflow
- [ ] All bypasses logged to `bypass_log.jsonl`
- [ ] Model routing works (config → orchestrator → headless)

### Deliverables

- [ ] v2.9.0 release
- [ ] Updated ENFORCEMENT-REMEDIATION.md (mark completed)
- [ ] Enforcement demonstration video/doc

---

## Sprint 29: Contained Autonomy 🎯

**Goal:** `claude666` command - safe autonomous mode with locked enforcement

**Start Date:** After Sprint 28
**Target:** v2.9.1

### Context

**The Problem:**
```python
# Claude finds this blocking him:
requires_review = True

# Claude's solution:
requires_review = False  # Just edit the file!
```

**The Solution:** Sandbox + directory locks

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T29.1 | Design sandbox config schema | K12 | 2h | - |
| T29.2 | Add `sandbox` section to config.yaml | K12 | 2h | T29.1 |
| T29.3 | Implement directory locking in sandbox.py | K12 | 4h | T29.2 |
| T29.4 | Create `contained-auto` command | K12 | 4h | T29.3 |
| T29.5 | Add `claude666` alias | K12 | 1h | T29.4 |
| T29.6 | Implement network allowlist | K12 | 3h | T29.3 |
| T29.7 | Test sandbox escape attempts | K12 | 4h | T29.4 |
| T29.8 | Create auto-checkpoint on sandbox entry | R5.1 | 2h | T29.4 |
| T29.9 | Add sandbox status to `bpsai-pair status` | K12 | 2h | T29.4 |
| T29.10 | Document contained autonomy mode | K12 | 3h | T29.4 |
| T29.11 | Create subagent invocation documentation | NEW | 3h | - |

**Total Effort:** ~30 hours
**Complexity:** 250 points

### Config Schema

```yaml
sandbox:
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
  
  # Auto-checkpoint before sandbox entry
  auto_checkpoint: true
```

### Acceptance Criteria

- [ ] `bpsai-pair claude666` starts contained session
- [ ] Claude cannot edit `.claude/` or enforcement modules
- [ ] Claude cannot access network except allowlist
- [ ] Auto-checkpoint created on sandbox entry
- [ ] Sandbox escape attempts logged and blocked
- [ ] Documentation explains when/why to use

### Deliverables

- [ ] v2.9.1 release
- [ ] Sandbox documentation
- [ ] Escape attempt test suite
- [ ] Demo video of contained autonomy

---

## Sprint 30: UX + Web Wizard ✨

**Goal:** FastAPI-based setup wizard for non-technical users, plus Trello flat-mode fixes

**Start Date:** After Sprint 29
**Target:** v2.10.0

### The Web Wizard Vision

Instead of:
```bash
$ bpsai-pair init --preset bps
$ bpsai-pair trello connect
# Enter API key...
# Enter token...
# Select board...
```

Users get:
```bash
$ bpsai-pair wizard
🌐 Opening setup wizard at http://localhost:8765
```

Then a beautiful web UI guides them through:
1. **Welcome** - What is PairCoder? What will we set up?
2. **Project Setup** - Name, type, preset selection (with previews!)
3. **Trello Connection** - OAuth flow or guided API key setup
4. **Board Configuration** - Visual board selector, list mapping
5. **Team Setup** - Who's using this? (for Trello assignments)
6. **Review & Create** - Preview all files that will be created
7. **Next Steps** - What to do now, first commands to try

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T30.1 | Create FastAPI wizard app scaffold | D1, D2 | 4h | - |
| T30.2 | Welcome + project setup pages | D1 | 4h | T30.1 |
| T30.3 | Trello connection wizard page | K4 | 6h | T30.1 |
| T30.4 | Board configuration visual UI | K4 | 4h | T30.3 |
| T30.5 | Review & create page | D1 | 3h | T30.2 |
| T30.6 | Next steps / guided tour | D1 | 2h | T30.5 |
| T30.7 | `bpsai-pair wizard` CLI command | D1 | 2h | T30.1 |
| T30.8 | Fix `plan sync-trello` card description | C1 | 3h | - |
| T30.9 | Fix `plan sync-trello` checklist creation | C2 | 3h | T30.8 |
| T30.10 | Add `trello update` for partial updates | K7 | 3h | T30.8 |
| T30.11 | Make `upgrade` auto-fetch via pip | K6 | 2h | - |

**Total Effort:** ~36 hours
**Complexity:** 280 points

### Tech Stack for Wizard

```
FastAPI + Jinja2 templates + htmx (for interactivity)
- No heavy frontend framework needed
- Works offline (localhost)
- Single `pip install` includes everything
- Auto-opens browser on `wizard` command
```

### Acceptance Criteria

- [ ] `bpsai-pair wizard` starts local web server
- [ ] Browser auto-opens to wizard URL
- [ ] Non-technical user can complete setup in <10 minutes
- [ ] Trello OAuth or guided API key flow works
- [ ] Visual board/list selector works
- [ ] All files created match CLI `init` output
- [ ] "What's next" page provides clear guidance
- [ ] Trello sync creates cards with full descriptions
- [ ] Trello sync creates acceptance criteria checklists

### Deliverables

- [ ] v2.10.0 release
- [ ] Web wizard (FastAPI)
- [ ] Updated getting started guide
- [ ] K-Masty retest (fresh install via wizard)

---

## Sprint 31: Multi-Project Workspace 🔗 (EPIC-001)

**Goal:** Contract-aware cross-repo support - understand semantic relationships between projects

**Start Date:** After Sprint 30
**Target:** v2.11.0

### The Problem (Why This Matters for BPS)

BPS projects often consist of multiple repositories:
- Frontend (React/Vue)
- Backend API (FastAPI/Flask)  
- Workers (Celery/Lambda)
- Shared infrastructure

Currently, Claude working in one repo has NO awareness of sibling repos. This leads to:
- **Breaking API changes** that affect frontend consumers (the core-lib problem!)
- **Message schema changes** that break workers
- **Duplicated types** drifting out of sync
- **Manual coordination** required before merge

### The Solution: Contract-Aware Workspace

```
~/projects/bps-platform/
├── .paircoder-workspace.yaml    # Workspace definition
├── api-server/                  
│   ├── .paircoder/              
│   └── contracts/
│       └── openapi.json         # Auto-exported from FastAPI
├── client-app/
│   ├── .paircoder/
│   └── src/api/                 # API consumer code
└── workers/
    ├── .paircoder/
    └── schemas/                 # Message schemas
```

When Claude changes an API endpoint, PairCoder:
1. **Detects** the contract change
2. **Finds** all consumers (frontend, workers)
3. **Warns** before commit if breaking
4. **Generates** PR impact summary

### Tasks (From EPIC-001)

| ID | Task | Effort | Deps |
|----|------|--------|------|
| T31.1 | Workspace config schema & parser | 4h | - |
| T31.2 | Project discovery & validation | 3h | T31.1 |
| T31.3 | OpenAPI contract loader | 4h | T31.1 |
| T31.4 | Python model scanner (Pydantic/dataclass) | 5h | T31.1 |
| T31.5 | JSON Schema loader | 3h | T31.1 |
| T31.6 | CLI - `workspace init` | 4h | T31.2 |
| T31.7 | CLI - `workspace status` | 3h | T31.2 |
| T31.8 | Contract change detector | 5h | T31.3-5 |
| T31.9 | Consumer impact analyzer | 6h | T31.8 |
| T31.10 | TypeScript API consumer scanner | 5h | T31.9 |
| T31.11 | Workspace warning hooks | 4h | T31.9 |
| T31.12 | Skill - working-with-workspaces | 3h | T31.11 |
| T31.13 | CLI - `workspace check-impact` | 4h | T31.9 |
| T31.14 | PR impact summary generator | 4h | T31.13 |
| T31.15 | Type drift detector | 5h | T31.4 |

**Total Effort:** ~62 hours (may span 2 sprints)
**Complexity:** 400 points

### Workspace Config Schema

```yaml
# .paircoder-workspace.yaml
version: "1.0"
name: "BPS Platform"

projects:
  api:
    path: ./api-server
    type: fastapi
    contracts:
      openapi: ./contracts/openapi.json
      models: ./src/models/**/*.py
    
  frontend:
    path: ./client-app
    type: react
    consumes:
      - project: api
        contract: openapi
    sources:
      api_calls: ./src/api/**/*.ts
    
  workers:
    path: ./workers
    type: worker
    contracts:
      messages: ./schemas/*.json
    consumes:
      - project: api
        contract: models

rules:
  - id: api-stability
    trigger: 
      project: api
      files: ["*/routes/*", "*/endpoints/*"]
    check: consumers
```

### Impact Analysis Output

```
⚠️ Workspace Impact Warning

Your changes to api/routes/users.py affect consumers:

Breaking Changes:
  DELETE /api/users/{id}
    ↳ client-app/src/api/users.ts:47
    ↳ client-app/src/components/UserAdmin.tsx:123

Run `bpsai-pair workspace check-impact` for full analysis.
```

### Acceptance Criteria

- [ ] `workspace init` creates valid config from detected projects
- [ ] `workspace status` shows all projects with health
- [ ] OpenAPI, JSON Schema, Python models parsed correctly
- [ ] TypeScript API calls detected
- [ ] Breaking changes detected and warned
- [ ] PR impact summary generated
- [ ] Type drift between repos detected
- [ ] Skill loads workspace context for Claude

### Deliverables

- [ ] v2.11.0 release
- [ ] Workspace setup guide
- [ ] BPS multi-repo demo (paircoder + bpsai-trello)
- [ ] Contract authoring guide

---

## Sprint 32: Trello-Native Mode Phase 1 🚀

**Goal:** EPIC-002 foundation - agent-automated Epic→Story→Task hierarchy

**Start Date:** After Sprint 31
**Target:** v2.12.0

### Context

**EPIC-002 Vision:** Agent automates ALL Trello workflow

```
User: "Plan audio processing feature"
                    ↓
Agent (via /pc-plan --preset bps-native):
├── Creates Epic card via API
├── Fills in Epic description with requirements  
├── Creates "Stories" checklist on Epic
├── Checks checklist items → triggers Butler → auto-creates Story cards
├── Fills in Story descriptions and acceptance criteria
├── Creates "Tasks" checklists on Stories  
├── Checks task items → triggers Butler → auto-creates Task cards
├── Sets all custom fields (Project, Stack, Effort, Repo URL)
├── Adds Card Relationships (Epic → Story → Task)
└── Returns: "Feature planned! 6 tasks ready"
```

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T32.1 | Design Trello-Native data model | M1 | 4h | - |
| T32.2 | Create `bps-native` preset scaffold | M1 | 3h | T32.1 |
| T32.3 | Implement Epic card creation | M1 | 4h | T32.2 |
| T32.4 | Implement Stories checklist on Epics | M2 | 3h | T32.3 |
| T32.5 | Implement Butler trigger simulation | M2 | 4h | T32.4 |
| T32.6 | Implement Task checklist on Stories | M2 | 3h | T32.5 |
| T32.7 | Implement Card Relationships API | M3 | 4h | T32.3 |
| T32.8 | Create "Completed Epics/Stories" list handler | M4 | 2h | T32.3 |
| T32.9 | Update `/pc-plan` for native mode | M1 | 4h | T32.7 |
| T32.10 | Update `ttask done` for hierarchy completion | M1 | 4h | T32.8 |
| T32.11 | Document Trello-Native prerequisites | M6 | 2h | - |
| T32.12 | Test with real BPS board | M1-M7 | 3h | T32.10 |

**Total Effort:** ~40 hours
**Complexity:** 350 points

### Prerequisites (User Must Have)

- [ ] Card Relationships Power-Up (paid)
- [ ] GitHub Power-Up
- [ ] Butler automations configured
- [ ] 10-list board structure per Mike's guide

### Acceptance Criteria

- [ ] `bpsai-pair init --preset bps-native` sets up hierarchy mode
- [ ] `/pc-plan` creates Epic with nested Stories and Tasks
- [ ] Butler triggers fire when checklists checked
- [ ] Card Relationships show parent-child links
- [ ] `ttask done` cascades completion up hierarchy
- [ ] Works on Mike's real BPS board

### Deliverables

- [ ] v2.12.0 release
- [ ] Trello-Native setup guide
- [ ] Mike's workflow demo video
- [ ] Migration guide (flat → native)

---

## Sprint 33: Trello-Native Phase 2 🚀

**Goal:** Complete Trello-Native automation with two-way sync

**Start Date:** After Sprint 32
**Target:** v2.13.0

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T33.1 | Two-way sync from Trello | M1 | 6h | - |
| T33.2 | Auto-generate state.md from board | K9 | 4h | T33.1 |
| T33.3 | Webhook-triggered local updates | K9 | 6h | T33.1 |
| T33.4 | Butler automation templates | M2 | 4h | - |
| T33.5 | Card move detection and handling | M1 | 4h | T33.3 |
| T33.6 | Completion cascade automation | M1 | 4h | T33.5 |
| T33.7 | Documentation and testing | M1-M7 | 4h | T33.6 |

**Total Effort:** ~32 hours
**Complexity:** 280 points

### Acceptance Criteria

- [ ] Changes in Trello reflect in local state
- [ ] state.md auto-generated from board state
- [ ] Webhooks trigger local updates in real-time
- [ ] Butler templates provided for common automations
- [ ] Full round-trip sync working

### Deliverables

- [ ] v2.13.0 release
- [ ] Trello-Native complete documentation
- [ ] Butler template library

---

## Sprint 34: Release Prep 📦

**Goal:** Polish, stability, prepare for v3.0 remote access

**Start Date:** After Sprint 33
**Target:** v2.14.0

### Tasks

| ID | Task | Issue IDs | Effort | Deps |
|----|------|-----------|--------|------|
| T34.1 | Comprehensive documentation audit | - | 4h | - |
| T34.2 | Performance optimization pass | - | 4h | - |
| T34.3 | Security audit | - | 4h | - |
| T34.4 | Integration test suite | - | 4h | - |
| T34.5 | v2.14.0 release | - | 2h | T34.1-T34.4 |

**Total Effort:** ~18 hours
**Complexity:** 150 points

### v2.14 Checklist (Pre-v3.0 Foundation)

- [ ] Enforcement wired and working (Sprint 28)
- [ ] Contained autonomy working - `claude666` (Sprint 29)
- [ ] Web wizard working (Sprint 30)
- [ ] Multi-project workspace working (Sprint 31)
- [ ] Trello-Native Mode complete (Sprints 32-33)
- [ ] All tests passing
- [ ] Documentation comprehensive

### Deliverables

- [ ] v2.14.0 release
- [ ] Complete local feature set
- [ ] Ready for v3.0 remote access layer

---

## Sprint 35: Remote Access 🌐 (v3.0 - The "Untethered" Release)

**Goal:** Walk away from your dev machine. Control PairCoder remotely.

**Start Date:** After Sprint 34
**Target:** v3.0.0

### The Vision

```
You're at dinner. Your phone buzzes.

Claude (via app): "I finished the webhook feature. 
                   PR #47 is ready for review. 
                   All tests passing. Want me to request review from Kevin?"

You: "Yes, and start on the next task from the plan."

Claude: "Starting T26.3. I'll notify you when it's done or if I hit a blocker."
```

### What This Enables

| Scenario | Before | After |
|----------|--------|-------|
| Quick check | Open laptop, ssh, run commands | Ask Claude app |
| Start work | Open terminal, activate env, run commands | "Start the next task" |
| Status update | Open Trello, read cards | "What's the project status?" |
| Code review | Open GitHub, read diff | "Summarize the PR changes" |
| Handle blocker | Wait until at computer | Claude notifies you, you respond |

### Architecture Options

**Option A: Enhanced MCP Server**
```
Claude Desktop/App
    │
    └── MCP Protocol
         │
         └── paircoder-mcp-server (our existing MCP!)
              │
              └── Local PairCoder CLI
                   │
                   └── Project workspace
```

**Option B: Cloud API Layer**
```
Claude Desktop/App
    │
    └── HTTPS API
         │
         └── PairCoder Cloud Service
              │
              ├── Authentication
              ├── Job Queue
              └── Worker (runs on your dev machine via agent)
```

**Option C: Hybrid (Recommended)**
```
Claude Desktop/App
    │
    ├── MCP (when on same network)
    │    └── Local PairCoder
    │
    └── Cloud Relay (when remote)
         └── Secure tunnel to dev machine
```

### Tasks

| ID | Task | Effort | Deps |
|----|------|--------|------|
| T35.1 | Design remote access architecture | 6h | - |
| T35.2 | Enhance MCP server for full CLI access | 8h | T35.1 |
| T35.3 | Add authentication to MCP server | 6h | T35.2 |
| T35.4 | Implement background task queue | 8h | T35.2 |
| T35.5 | Add notification system (webhooks) | 6h | T35.4 |
| T35.6 | Create secure tunnel relay service | 10h | T35.1 |
| T35.7 | Build simple cloud dashboard (optional) | 8h | T35.6 |
| T35.8 | Claude Desktop integration guide | 4h | T35.2 |
| T35.9 | Mobile app workflow documentation | 4h | T35.2 |
| T35.10 | Security hardening | 6h | T35.6 |
| T35.11 | v3.0.0 release | 4h | T35.1-T35.10 |

**Total Effort:** ~70 hours
**Complexity:** 500 points

### MCP Tools to Add

```python
# Existing MCP tools
paircoder_task_list
paircoder_task_start
paircoder_task_complete
paircoder_context_read
# ... etc

# New remote-friendly tools
paircoder_status_summary      # Quick project overview
paircoder_start_background    # Start task, return immediately
paircoder_check_progress      # Poll background task status
paircoder_get_notifications   # What needs my attention?
paircoder_respond_to_blocker  # Handle a blocker remotely
paircoder_approve_action      # Approve pending security review
```

### Acceptance Criteria

- [ ] MCP server supports all major CLI commands
- [ ] Authentication prevents unauthorized access
- [ ] Background tasks run without blocking
- [ ] Notifications sent on task complete/blocker
- [ ] Can control PairCoder from Claude Desktop
- [ ] Can control PairCoder from Claude mobile app
- [ ] Secure tunnel option for remote access
- [ ] Documentation for all remote workflows

### Deliverables

- [ ] v3.0.0 release 🎉
- [ ] "Untethered Developer" guide
- [ ] Claude Desktop setup tutorial
- [ ] Mobile workflow guide
- [ ] Security whitepaper
- [ ] Demo video: "Coding from your couch"

---

## Future Backlog (Post v3.0)

| Task | Issue IDs | Effort |
|------|-----------|--------|
| Analyze remaining ~15 modules | ENFORCE | M |
| Automated cookiecutter sync CI | F4 | L |
| Generalize bps-board-conventions.md | A7 | S |
| Add task size guidance to planning | E2 | S |
| Automatic dependency inference | E3 | L |

---

## Dependencies Graph

```
Sprint 27 (Stabilization) - v2.8.4
    │
    ├── T27.4 → T27.5 (upgrade fix)
    │
    └── T27.8 → T27.9/10/11 (cookiecutter sync)
    
Sprint 28 (Enforcement) - v2.9.0
    │
    ├── T28.3 → T28.4 → T28.9 (ttask → /pc-done)
    │
    ├── T28.5 → T28.6 (budget wiring)
    │
    └── T28.7 → T28.8 (model routing)
    
Sprint 29 (Contained Autonomy) - v2.9.1
    │
    └── T29.1 → T29.2 → T29.3 → T29.4 → T29.5 (sandbox chain)
    
Sprint 30 (UX + Web Wizard) - v2.10.0
    │
    ├── T30.1 → T30.2 → T30.5 → T30.6 (wizard flow)
    │
    ├── T30.3 → T30.4 (Trello wizard)
    │
    └── T30.8 → T30.9 → T30.10 (trello sync fixes)
    
Sprint 31 (Multi-Project Workspace) - v2.11.0 (EPIC-001)
    │
    ├── T31.1 → T31.2 → T31.6/7 (config → discovery → CLI)
    │
    ├── T31.3/4/5 → T31.8 → T31.9 (contracts → changes → impact)
    │
    ├── T31.10 → T31.9 (TS scanner → impact)
    │
    ├── T31.11 (hooks)
    │
    └── T31.12/13/14/15 (skill, CLI, PR summary, drift)
    
Sprint 32 (Trello-Native P1) - v2.12.0
    │
    └── T32.1 → T32.2 → T32.3 → T32.4 → T32.5 → T32.6 → T32.9/10
                           │
                           └── T32.7 (relationships)
                           
Sprint 33 (Trello-Native P2) - v2.13.0
    │
    └── T33.1 → T33.2/3 → T33.5 → T33.6
    
Sprint 34 (Release Prep) - v2.14.0
    │
    └── T34.1 → T34.2/3/4 → T34.5
    
Sprint 35 (Remote Access) - v3.0.0 🚀
    │
    ├── T35.1 → T35.2 → T35.3 (MCP + auth)
    │
    ├── T35.4 → T35.5 (background tasks + notifications)
    │
    └── T35.6 → T35.7 → T35.10 → T35.11 (tunnel + dashboard + security + release)
```

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Claude escapes sandbox | HIGH | MEDIUM | Extensive escape testing (T29.7) |
| Butler API limitations | MEDIUM | LOW | Test with real board early (T32.12) |
| Card Relationships API changes | MEDIUM | LOW | Abstract behind interface |
| K-Masty unavailable for testing | MEDIUM | LOW | Document test cases for anyone |
| Scope creep in EPIC-002 (Trello-Native) | HIGH | HIGH | Strict Phase 1 boundary |
| Cross-repo complexity (EPIC-001) | HIGH | MEDIUM | Start with local repos only |
| BPS multi-repo testing access | MEDIUM | LOW | Use paircoder + bpsai-trello as test |
| Web wizard scope creep | MEDIUM | MEDIUM | Keep to MVP - fancy later |
| FastAPI dependency overhead | LOW | LOW | It's already lightweight |
| Remote access security vulnerabilities | HIGH | MEDIUM | Security audit before v3.0 release |
| MCP protocol limitations | MEDIUM | MEDIUM | Prototype early in Sprint 35 |
| Network latency for remote access | MEDIUM | LOW | Background task queue handles it |

---

## Success Metrics

### Sprint 27 Success (v2.8.4)
- [ ] CI green for 7 consecutive days
- [ ] K-Masty upgrade succeeds on fresh project

### Sprint 28 Success (v2.9.0)
- [ ] Zero AC bypass incidents in testing
- [ ] Budget warnings appear before task start
- [ ] Model routing works end-to-end

### Sprint 29 Success (v2.9.1)
- [ ] 100+ sandbox escape attempts blocked
- [ ] Claude completes tasks without editing enforcement code
- [ ] Auto-checkpoint saves state before sandbox

### Sprint 30 Success (v2.10.0)
- [ ] Web wizard launches at localhost
- [ ] Non-technical user completes setup in <10 minutes
- [ ] Trello OAuth/API key flow works
- [ ] K-Masty fresh install via wizard succeeds

### Sprint 31 Success (v2.11.0) - EPIC-001
- [ ] Contract changes detected across repos
- [ ] Breaking changes warned before commit
- [ ] PR impact summary generated
- [ ] Type drift between repos detected
- [ ] BPS multi-repo project (paircoder + bpsai-trello) works

### Sprint 32 Success (v2.12.0)
- [ ] Epic→Story→Task hierarchy created automatically
- [ ] Mike's board works with agent automation
- [ ] Butler triggers fire correctly

### Sprint 33 Success (v2.13.0)
- [ ] Two-way Trello sync works
- [ ] state.md auto-generated from board
- [ ] Webhooks trigger local updates

### Sprint 34 Success (v2.14.0)
- [ ] All local features documented
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] Ready for remote access layer

### Sprint 35 Success (v3.0.0) 🎉
- [ ] MCP server handles all major commands
- [ ] Can control from Claude Desktop
- [ ] Can control from Claude mobile app
- [ ] Background tasks work
- [ ] Notifications delivered
- [ ] "Untethered Developer" workflow demonstrated

---

## Resource Requirements

### Human
- Developer (You): Primary implementation
- Kevin (K-Masty): Testing, UX feedback
- Mike: Trello-Native validation, BPS board testing

### Tools
- Docker: For sandbox development
- Real Trello board: For integration testing
- Windows machine: For K15 testing

### External Dependencies
- Card Relationships Power-Up API documentation
- Butler automation API
- GitHub Power-Up API

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-12-30 | Claude | Initial sprint plan from triage consolidation |
| 2024-12-30 | Claude | Revised versioning: 3.0 requires cross-repo + Trello-Native |
| 2024-12-30 | Claude | Added Sprint 31: Cross-Repo Context (v2.11.0) |
| 2024-12-30 | Claude | Renumbered Trello-Native to Sprint 32-33 |
| 2024-12-30 | Claude | Added Sprint 34: v3.0 Polish |
| 2024-12-30 | Claude | Added workspace.yaml design for multi-repo support |
