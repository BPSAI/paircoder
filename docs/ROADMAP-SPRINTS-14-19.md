# PairCoder Roadmap: Sprints 14-19

> Created: 2025-12-16
> Updated: 2025-12-16
> Focus: Trello perfection → Security → Real agents → Metrics → Enforcement → Cross-Platform

---

## Sprint Summary

| Sprint | Theme | Tasks | Est. Effort | Priority |
|--------|-------|-------|-------------|----------|
| 14 | Trello Deep Integration | 8 tasks | 3-4 days | **Current** |
| 15 | Security & Sandboxing | 7 tasks | 4-5 days | High |
| 16 | Real Sub-agents | 6 tasks | 3-4 days | Medium |
| 17 | Time & Metrics | 6 tasks | 2-3 days | Medium |
| 18 | Methodology Enforcement | 6 tasks | 2-3 days | Medium |
| 19 | Cross-Platform Skills 🔥 | 7 tasks | 3-4 days | Future |
| Backlog | Remote API (TASK-114) 🔥 | 1 task | 3-4 days | Future |

---

## Sprint 13: Full Autonomy - COMPLETE ✅

**Completed Tasks:**
- TASK-066: Webhook listener for Trello card moves
- TASK-067: Agent assignment on Ready column
- TASK-068: Progress comments from agents
- TASK-069: Auto-PR link when branch pushed
- TASK-070: GitHub PR integration
- TASK-071: PR merge triggers task archive
- TASK-072: Automatic next task assignment
- TASK-073: Daily standup summary generation
- TASK-077: Add preset system (8 presets including BPS)
- TASK-078: Create BPS preset with full Trello guidelines
- TASK-079: Auto-enter planning mode on new feature detection
- TASK-080: Orchestrator sequencing for full autonomy

**Deprioritized to Backlog:**
- TASK-063: VS Code extension
- TASK-064: Status bar widget
- TASK-065: Auto-context on save
- TASK-074: Dashboard UI (BPS has Trello React app)
- TASK-075: Slack notifications
- TASK-076: Multi-project support

**Test Coverage:** 445 tests passing

---

## Sprint 14: Trello Deep Integration - IN PROGRESS

> **Goal:** Cards created by PairCoder look exactly like Mike would create manually.

### Tasks

| ID | Title | Status | Complexity |
|----|-------|--------|------------|
| TASK-081 | Sync Trello custom fields | ✅ done | 35 |
| TASK-082 | Sync Trello labels with exact BPS colors | pending | 25 |
| TASK-083 | Card description templates (BPS format) | pending | 25 |
| TASK-084 | Effort → Trello Effort field mapping | pending | 20 |
| TASK-085 | Two-way sync (Trello → local) | pending | 45 |
| TASK-086 | Support checklists in cards | pending | 30 |
| TASK-087 | Due date sync | pending | 20 |
| TASK-088 | Activity log comments | pending | 25 |

### ⚠️ Integration Gap Identified

The new `TrelloSyncManager` class exists but is **not wired into the actual commands**:
- `trello/sync.py` created with `TrelloSyncManager`, `BPS_LABELS`, `TaskSyncConfig`
- `plan sync-trello` command is NOT using the new sync module
- Labels and custom fields NOT being applied to real cards

**Fix Required:** Update `planning/cli_commands.py` to use `TrelloSyncManager`

### BPS Trello Requirements

**Custom Fields:**
| Field | Example | Maps From |
|-------|---------|-----------|
| Project | Aurora | plan.title |
| Stack | Flask | task.tags or inferred |
| Status | In Progress | task.status |
| Effort | S / M / L | task.complexity |
| Deployment Tag | v1.2.3 | git tag or manual |

**Label Colors:**
| Label | Color | Hex |
|-------|-------|-----|
| Frontend | Green | #61bd4f |
| Backend | Blue | #0079bf |
| Worker/Function | Purple | #c377e0 |
| Deployment | Red | #eb5a46 |
| Bug/Issue | Orange | #ff9f1a |
| Security/Admin | Yellow | #f2d600 |
| Documentation | Sky | #00c2e0 |
| AI/ML | Black | #344563 |

### Success Criteria
- [ ] `plan sync-trello` creates cards with all custom fields populated
- [ ] Labels match exact BPS colors (created on board)
- [ ] Card description follows BPS template
- [ ] Moving card in Trello updates local task status
- [ ] Checklist items created from acceptance criteria
- [ ] Credentials persist across sessions

---

## Sprint 15: Security & Sandboxing

> **Goal:** Safe autonomous execution without `--dangerously-skip-permissions`.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-089 | Security agent definition | Create .claude/agents/security.md with SOC2 focus | 30 |
| TASK-090 | Command allowlist system | Define safe vs unsafe commands | 35 |
| TASK-091 | Pre-execution security review | Security agent reviews commands before running | 45 |
| TASK-092 | Docker sandbox runner | Execute agent work in isolated container | 50 |
| TASK-093 | Git checkpoint/rollback | Auto-checkpoint before changes, rollback on failure | 35 |
| TASK-094 | Secret detection | Scan for leaked credentials before commit | 30 |
| TASK-095 | Dependency vulnerability scan | Check for known CVEs in dependencies | 25 |

### Security Agent Scope

```markdown
# .claude/agents/security.md

## Role
Review all code changes and commands for security issues before execution.

## Checklist
- [ ] No hardcoded credentials
- [ ] No SQL injection vulnerabilities
- [ ] No command injection risks
- [ ] Dependencies are pinned and scanned
- [ ] File permissions are appropriate
- [ ] Network calls use HTTPS
- [ ] Input validation present
- [ ] SOC2 controls addressed

## Blocking Conditions
- BLOCK if credentials detected
- BLOCK if rm -rf without confirmation
- BLOCK if sudo without justification
- WARN if new dependencies added
```

### Command Allowlist Structure

```yaml
# .paircoder/security/allowlist.yaml
commands:
  always_allowed:
    - git status
    - git diff
    - git log
    - pytest
    - bpsai-pair *
    - cat
    - ls
    - grep
    
  require_review:
    - git push
    - git commit
    - pip install
    - npm install
    
  always_blocked:
    - rm -rf /
    - sudo rm
    - curl | bash
    - wget | sh
    
  patterns:
    blocked:
      - "rm -rf [^.]*"  # rm -rf not in current dir
      - "curl.*\\|.*sh"  # piped curl to shell
```

### Success Criteria
- [ ] Can run autonomous session without `--dangerously-skip-permissions`
- [ ] Dangerous commands are blocked with explanation
- [ ] Security agent reviews all PRs before creation
- [ ] Rollback works when things break
- [ ] No secrets in any commits

---

## Sprint 16: Real Sub-agents

> **Goal:** `bpsai-pair orchestrate task` actually routes to appropriate agent.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-096 | Agent invocation framework | Base class for invoking sub-agents | 45 |
| TASK-097 | Planner agent implementation | Invokes planner for design tasks | 35 |
| TASK-098 | Reviewer agent implementation | Invokes reviewer for code review | 35 |
| TASK-099 | Security agent implementation | Invokes security for pre-commit review | 40 |
| TASK-100 | Agent handoff protocol (real) | Actual context passing between agents | 40 |
| TASK-101 | Agent selection logic | Route tasks to appropriate agent | 30 |

### Agent Invocation Options

**Option A: Subprocess**
```python
class AgentInvoker:
    def invoke(self, agent_name: str, context: str) -> str:
        agent_prompt = self.load_agent(agent_name)
        result = subprocess.run([
            "claude", "-p", f"{agent_prompt}\n\nContext:\n{context}"
        ], capture_output=True)
        return result.stdout
```

**Option B: MCP Tool**
```python
@mcp.tool()
def invoke_agent(agent_name: str, task_context: str) -> str:
    """Invoke a sub-agent for specialized work."""
    # Load agent prompt
    # Execute with context
    # Return result
```

**Option C: Claude Code Native (if available)**
```
/agent planner "Design the authentication system"
```

### Agent Routing Logic

```python
def select_agent(task: Task) -> str:
    """Select appropriate agent based on task characteristics."""
    
    if task.type == "design" or "plan" in task.title.lower():
        return "planner"
    
    if task.type == "review" or "PR" in task.title:
        return "reviewer"
    
    if "security" in task.tags or "auth" in task.title.lower():
        return "security"
    
    # Default to main agent
    return "default"
```

### Success Criteria
- [ ] `bpsai-pair orchestrate task TASK-001` invokes correct agent
- [ ] Agent output captured and logged
- [ ] Handoff passes full context between agents
- [ ] Security agent can block unsafe operations

---

## Sprint 17: Time & Metrics Reality

> **Goal:** Know if estimates are accurate, track velocity.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-102 | Complexity → hours mapping | Convert complexity points to hour estimates | 20 |
| TASK-103 | Auto-timer that actually works | Timer starts/stops with task status changes | 30 |
| TASK-104 | Actual vs estimated tracking | Store and compare estimates to actuals | 35 |
| TASK-105 | Velocity calculation | Points completed per week/sprint | 25 |
| TASK-106 | Sprint burndown chart data | Generate data for burndown visualization | 30 |
| TASK-107 | Estimation accuracy report | "Your estimates are 20% optimistic" | 25 |

### Complexity → Hours Mapping

```yaml
# Suggested mapping (configurable)
complexity_to_hours:
  # Complexity: [min_hours, expected_hours, max_hours]
  0-15: [0.5, 1, 2]      # XS - under 2 hours
  16-30: [1, 2, 4]       # S - half day
  31-50: [2, 4, 8]       # M - full day
  51-75: [4, 8, 16]      # L - 1-2 days
  76-100: [8, 16, 32]    # XL - 2-4 days
```

### Metrics Schema

```yaml
# .paircoder/history/metrics.jsonl format
{
  "task_id": "TASK-081",
  "estimated_hours": 4,
  "actual_hours": 3.5,
  "complexity": 35,
  "started_at": "2025-12-16T10:00:00Z",
  "completed_at": "2025-12-16T13:30:00Z",
  "agent": "claude-code",
  "tokens_used": 45000,
  "cost_usd": 0.12
}
```

### Success Criteria
- [ ] Every task has estimated hours (derived from complexity)
- [ ] Timer auto-starts when task moves to in_progress
- [ ] Timer auto-stops when task completes
- [ ] Can generate "estimated vs actual" report
- [ ] Velocity tracked over sprints

---

## Sprint 18: Methodology Enforcement

> **Goal:** Claude cannot skip steps or forget updates.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-108 | Mandatory state.md update hook | Fails if state.md not updated | 25 |
| TASK-109 | Pre-commit validation | Block commit if tests fail or state stale | 30 |
| TASK-110 | Workflow gate enforcement | Cannot skip planning phase | 35 |
| TASK-111 | Compaction-resistant context | Key facts survive context compression | 40 |
| TASK-112 | Methodology compliance score | Score each task on process compliance | 30 |
| TASK-113 | Automated retrospective notes | Generate "what went well/wrong" per sprint | 25 |

### Enforcement Points

```
Task Start
├── Has task file? ✓ Required
├── Task has implementation plan? ✓ Required
├── State.md updated with "Current Focus"? ✓ Required
└── Trello card in "In Progress"? ✓ If Trello enabled

During Task
├── Running tests periodically? ✓ Recommended
├── Committing incrementally? ✓ Recommended
└── Adding comments to Trello? ✓ If Trello enabled

Task Complete
├── Tests passing? ✓ Required
├── State.md updated with "What Was Done"? ✓ Required
├── Trello card in "Done"? ✓ If Trello enabled
├── PR created? ✓ If GitHub enabled
└── Time logged? ✓ If timer enabled
```

### Compaction-Resistant Context

```markdown
<!-- CRITICAL: This section MUST survive context compaction -->
<!-- ALWAYS_INCLUDE_START -->

## Mandatory Actions
1. Update state.md after completing ANY task
2. Run tests before marking task done
3. Move Trello cards when status changes
4. Use bpsai-pair commands for all task management

## Current Task
- ID: TASK-081
- Title: Sync Trello custom fields
- Status: in_progress

<!-- ALWAYS_INCLUDE_END -->
```

### Success Criteria
- [ ] Cannot complete task without state.md update
- [ ] Cannot commit without tests passing
- [ ] Cannot skip planning phase
- [ ] Process compliance visible and tracked
- [ ] Key context survives compaction

---

## Sprint 19: Cross-Platform Skills 🔥

> **Goal:** PairCoder becomes a skill provider for ANY agent platform - Claude, OpenAI Codex, ChatGPT, and beyond.

### Context

OpenAI is adopting Anthropic's skills pattern (Dec 2025):
- Same folder + SKILL.md structure
- Works in ChatGPT Code Interpreter (`/home/oai/skills`)
- Works in Codex CLI (`~/.codex/skills`)
- Agentic AI Foundation may formalize the spec

**This means our skills could work everywhere.**

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-115 | Cross-platform skills directory | Support multiple skill locations, symlinks | 30 |
| TASK-116 | Skill validator | Validate SKILL.md format, required sections | 25 |
| TASK-117 | Skill installer CLI | `bpsai-pair skill install <url>` from GitHub/URL | 35 |
| TASK-118 | Skill discovery & registry | List available community skills | 40 |
| TASK-119 | Skill authoring skill | Meta-skill that helps create new skills | 30 |
| TASK-120 | Skill export for Codex | `bpsai-pair skill export --target codex` | 25 |
| TASK-121 | Skill sync across platforms | Keep skills in sync across .claude/, .codex/, etc. | 35 |

### Directory Structure Vision

```
my-project/
├── .paircoder/
│   └── skills/                    # PairCoder canonical skills
│       ├── design-plan-implement/
│       │   └── SKILL.md
│       ├── trello-workflow/
│       │   └── SKILL.md
│       └── bps-methodology/
│           └── SKILL.md
│
├── .claude/
│   └── skills/ → ../.paircoder/skills/  # Symlink for Claude
│
└── .codex/
    └── skills/ → ../.paircoder/skills/  # Symlink for Codex
```

Or global installation:
```bash
# Install PairCoder skills globally for all agents
bpsai-pair skill install --global

# Creates:
# ~/.claude/skills/paircoder-* 
# ~/.codex/skills/paircoder-*
```

### Skill Registry Vision

```bash
# Discover skills
bpsai-pair skill search "trello"
# Results:
#   paircoder/trello-workflow - Trello task management workflow
#   community/trello-automation - Advanced Trello automations

# Install from registry
bpsai-pair skill install paircoder/trello-workflow

# Install from GitHub
bpsai-pair skill install https://github.com/datasette/skill

# List installed
bpsai-pair skill list
# - design-plan-implement (local)
# - trello-workflow (local)
# - datasette-plugin (github:datasette/skill)
```

### Skill Validator

```bash
bpsai-pair skill validate .paircoder/skills/my-skill/

# Checks:
# ✓ SKILL.md exists
# ✓ Has ## Purpose section
# ✓ Has ## Triggers section  
# ✓ Has ## Workflow or ## Steps section
# ⚠ Missing ## Recording Your Work section (recommended)
# ✓ Valid markdown syntax
```

### Why This Is Strategic

1. **Network effects** - More skills = more value = more users
2. **Community contributions** - Others can create skills for PairCoder
3. **Platform agnostic** - Not locked to Claude if OpenAI gets better
4. **Ecosystem play** - PairCoder becomes infrastructure, not just a tool

### Success Criteria
- [ ] Skills work in Claude Code, Codex CLI, and ChatGPT
- [ ] `bpsai-pair skill install <url>` works
- [ ] Skill validator catches common issues
- [ ] At least 3 community skills published
- [ ] Documentation for skill authors

---

## Backlog: Remote Orchestration API 🔥

### TASK-114: Remote Orchestration API

**What it enables:**
```
You (talking to claude.ai): "Start Sprint 14"
         ↓
Me (claude.ai): calls your API
         ↓
Your Machine: PairCoder creates plan, syncs Trello, kicks off Claude Code
         ↓
Work happens while you sleep
         ↓
Me: checks progress via API, reports back
```

**Components:**
- HTTP server wrapping MCP tools
- API key authentication
- WebSocket for real-time updates
- Client library for easy integration

**When to build:** After Sprints 14-15 (Trello + Security) are solid.

---

## Other Backlog Items

| Task | Title | Category |
|------|-------|----------|
| - | VS Code extension | Developer Experience |
| - | Slack notifications | Communication |
| - | Multi-project support | Scale |
| - | Dashboard web UI | Optional (BPS has Trello app) |
| - | Codex/GPT-5 adapter | Multi-model support |
| - | Voice commands | Future |

---

## Implementation Order Rationale

```
Sprint 14 (Trello) - Your team uses Trello daily. Make it perfect.
     ↓
Sprint 15 (Security) - Before more autonomy, need safety.
     ↓
Sprint 16 (Sub-agents) - Enables security agent and specialized work.
     ↓
Sprint 17 (Metrics) - Know if the system is actually helping.
     ↓
Sprint 18 (Enforcement) - Ensure consistency and process compliance.
     ↓
Sprint 19 (Cross-Platform) - Skills work on ANY agent platform.
     ↓
Remote API - Full remote orchestration capability.
```

---

## Quick Reference: All Tasks

| Sprint | Theme | Tasks | IDs |
|--------|-------|-------|-----|
| 13 | Full Autonomy | ✅ Complete | TASK-066 - 080 |
| 14 | Trello Deep | 8 tasks | TASK-081 - 088 |
| 15 | Security | 7 tasks | TASK-089 - 095 |
| 16 | Sub-agents | 6 tasks | TASK-096 - 101 |
| 17 | Metrics | 6 tasks | TASK-102 - 107 |
| 18 | Enforcement | 6 tasks | TASK-108 - 113 |
| 19 | Cross-Platform | 7 tasks | TASK-115 - 121 |
| Backlog | Remote API | 1 task | TASK-114 |
| **Total New** | | **41** | |

---

## Known Issues

### GitHub CI Failing
**Error:** `SyntaxError: f-string expression part cannot include a backslash`
**Location:** `planning/cli_commands.py:852`
**Fix:** Replace `'\u2713'` with actual `✓` character or assign to variable first

### Trello Integration Gap
**Issue:** New `TrelloSyncManager` exists but not wired into commands
**Impact:** Labels and custom fields not being created on real cards
**Fix:** Update `plan sync-trello` to use `TrelloSyncManager`

---

## Notes

- All task IDs are sequential and assigned
- Complexity points are estimates - refine during planning
- Order within sprint can be adjusted based on dependencies
- Some tasks may split or merge during implementation
- Test coverage target: maintain 400+ tests
