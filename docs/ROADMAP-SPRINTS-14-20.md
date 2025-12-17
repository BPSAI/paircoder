# PairCoder Roadmap: Sprints 14-20

> Created: 2025-12-16
> Updated: 2025-12-16
> Focus: Trello perfection → Security → Real agents → Metrics → Enforcement → Cross-Platform → Self-Improvement

---

## Sprint Summary

| Sprint | Theme | Tasks | Est. Effort | Priority        |
|--------|-------|-------|-------------|-----------------|
| 14 | Trello Deep Integration | 8 tasks | 3-4 days | Complete|
| 15 | Security & Sandboxing | 7 tasks | 4-5 days | **Current**|
| 16 | Real Sub-agents | 6 tasks | 3-4 days | Medium          |
| 17 | Time, Tokens & Metrics | 8 tasks | 3-4 days | Medium          |
| 18 | Methodology, Sessions & Recovery | 12 tasks | 4-5 days | Medium          |
| 19 | Cross-Platform Skills 🔥 | 7 tasks | 3-4 days | Future          |
| 20 | Emergent Skill Discovery 🧠 | 9 tasks | 4-5 days | Future          |
| Backlog | Remote API (TASK-114) 🔥 | 1 task | 3-4 days | Future          |

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

## Sprint 14: Trello Deep Integration - Complete

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
| TASK-100 | Agent handoff protocol  | Actual context passing between agents | 40 |
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

## Sprint 17: Time, Tokens & Metrics

> **Goal:** Know how much things cost - time, tokens, accuracy of estimates.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-102 | Complexity → hours mapping | Convert complexity points to hour estimates | 20 |
| TASK-103 | Auto-timer that actually works | Timer starts/stops with task status changes | 30 |
| TASK-104 | Actual vs estimated tracking | Store and compare estimates to actuals | 35 |
| TASK-105 | Velocity calculation | Points completed per week/sprint | 25 |
| TASK-106 | Sprint burndown chart data | Generate data for burndown visualization | 30 |
| TASK-107 | Estimation accuracy report | "Your estimates are 20% optimistic" | 25 |
| TASK-133 | Token estimation model | Predict tokens from complexity + type + files | 35 |
| TASK-138 | Token estimation feedback loop | Improve estimates from actual usage data | 30 |

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

### Token Estimation Model

```yaml
# Learned from historical data
token_estimates:
  base_context: 15000  # Skills, state, project context
  
  per_complexity_point: 500  # Rough: 50 complexity ≈ 25k tokens
  
  by_task_type:
    feature: 1.2x  # More back-and-forth
    bugfix: 0.8x   # Usually focused
    docs: 0.6x     # Less code generation
    refactor: 1.5x # Lots of reading existing code
    
  by_file_count:
    per_file_touched: 2000  # Each file adds context
```

### Metrics Schema

```yaml
# .paircoder/history/metrics.jsonl format
{
  "task_id": "TASK-081",
  "estimated_hours": 4,
  "actual_hours": 3.5,
  "estimated_tokens": 35000,
  "actual_tokens": 42000,
  "complexity": 35,
  "task_type": "feature",
  "files_touched": 5,
  "started_at": "2025-12-16T10:00:00Z",
  "completed_at": "2025-12-16T13:30:00Z",
  "agent": "claude-code",
  "cost_usd": 0.12
}
```

### Estimation Feedback Loop

```
Plan session (with estimates)
         ↓
Execute tasks
         ↓
Measure actual tokens used
         ↓
Compare to estimates
         ↓
Adjust model coefficients:
  "Refactor tasks actually use 1.7x, not 1.5x"
  "File count impact is 2500 tokens, not 2000"
         ↓
Better estimates next sprint
```

### Success Criteria
- [ ] Every task has estimated hours (derived from complexity)
- [ ] Every task has estimated tokens (derived from complexity + type)
- [ ] Timer auto-starts when task moves to in_progress
- [ ] Timer auto-stops when task completes
- [ ] Can generate "estimated vs actual" report for both time and tokens
- [ ] Velocity tracked over sprints
- [ ] Token estimates improve over time (feedback loop working)

---

## Sprint 18: Methodology, Sessions & Recovery

> **Goal:** Claude cannot skip steps, sessions restart before compaction, and recovery is automatic.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-108 | Mandatory state.md update hook | Fails if state.md not updated | 25 |
| TASK-109 | Pre-commit validation | Block commit if tests fail or state stale | 30 |
| TASK-110 | Workflow gate enforcement | Cannot skip planning phase | 35 |
| TASK-111 | Compaction-resistant context | Key facts survive context compression | 40 |
| TASK-112 | Methodology compliance score | Score each task on process compliance | 30 |
| TASK-113 | Automated retrospective notes | Generate "what went well/wrong" per sprint | 25 |
| TASK-129 | Session restart enforcement | Force new session after N tasks or token threshold | 35 |
| TASK-130 | Context checkpoint system | Save critical state before compaction risk | 40 |
| TASK-134 | Session budget calculator | Use token estimates to determine safe task count | 30 |
| TASK-135 | Batch planning algorithm | Group tasks into compaction-safe sessions | 40 |
| TASK-136 | Compaction detection | Detect when critical context was lost | 35 |
| TASK-137 | Compaction recovery | Auto-reload critical context from checkpoint | 40 |

### The Token-Aware Session Flow

```
Sprint 17 Metrics → Sprint 18 Planning

Token estimation model ──→ Session budget calculator
         ↓                         ↓
Estimation feedback ←──── Batch planning algorithm
                                   ↓
                          Session execution
                                   ↓
                    ┌──── Compaction detected? ────┐
                    ↓ No                      Yes ↓
               Continue                    Recovery
                    ↓                           ↓
              /update-skills              Reload checkpoint
                    ↓                           ↓
              Checkpoint & restart         Resume task
```

### Session Budget Calculator

```python
class SessionBudgetCalculator:
    def calculate_budget(self, context_window: int = 200000) -> int:
        """Calculate safe token budget for a session."""
        safe_threshold = 0.75  # Use 75% of context window
        base_context = 15000   # Skills, state, project files
        
        available = (context_window * safe_threshold) - base_context
        return int(available)  # ~135k tokens for work
    
    def tasks_that_fit(self, tasks: list[Task], budget: int) -> list[Task]:
        """Select tasks that fit within budget."""
        selected = []
        running_total = 0
        
        for task in tasks:
            estimated = self.estimate_tokens(task)
            if running_total + estimated <= budget:
                selected.append(task)
                running_total += estimated
            else:
                break  # Start new session for remaining
        
        return selected
```

### Batch Planning Algorithm

```python
class BatchPlanner:
    def plan_sprint_sessions(self, sprint_tasks: list[Task]) -> list[Session]:
        """Break sprint into compaction-safe sessions."""
        sessions = []
        remaining = sprint_tasks.copy()
        
        while remaining:
            budget = self.calculator.calculate_budget()
            batch = self.calculator.tasks_that_fit(remaining, budget)
            
            sessions.append(Session(
                tasks=batch,
                estimated_tokens=sum(self.estimate(t) for t in batch),
                checkpoint_before=True,
                run_update_skills_after=True,
            ))
            
            remaining = [t for t in remaining if t not in batch]
        
        return sessions
```

**Example output:**
```
Sprint 14 Session Plan:
  Session 1: [TASK-081, TASK-082, TASK-083] → ~60k tokens
  Session 2: [TASK-084, TASK-085] → ~55k tokens  
  Session 3: [TASK-086, TASK-087, TASK-088] → ~50k tokens
  
  Each session:
  ├── Checkpoint critical state before starting
  ├── Execute tasks
  ├── Run /update-skills to capture learnings
  ├── Checkpoint final state
  └── Restart with fresh context
```

### Compaction Detection

```python
class CompactionDetector:
    """Detect when context compaction caused information loss."""
    
    CRITICAL_MARKERS = [
        ("TRELLO_BOARD_ID", "694176ebf4b9d27c6e7a0e73"),
        ("CURRENT_TASK", None),  # Any value expected
        ("METHODOLOGY", "update state.md"),
    ]
    
    def check_context_health(self) -> CompactionStatus:
        """Check if critical context is still present."""
        missing = []
        
        for marker, expected in self.CRITICAL_MARKERS:
            if not self.context_contains(marker, expected):
                missing.append(marker)
        
        if missing:
            return CompactionStatus(
                compacted=True,
                missing_markers=missing,
                recovery_needed=True
            )
        
        return CompactionStatus(compacted=False)
```

### Compaction Recovery

```python
class CompactionRecovery:
    """Recover from unexpected context compaction."""
    
    def recover(self, status: CompactionStatus):
        """Reload critical context from checkpoint."""
        
        # 1. Load latest checkpoint
        checkpoint = self.load_checkpoint()
        
        # 2. Inject critical context
        self.inject_credentials(checkpoint.credentials)
        self.inject_current_task(checkpoint.current_task)
        self.inject_methodology_reminders()
        
        # 3. Log for learning
        self.log_compaction_event(
            missing=status.missing_markers,
            recovered_from=checkpoint.timestamp
        )
        
        # 4. Resume from last known state
        return checkpoint.current_task
```

### The Compaction Problem

**Symptoms:**
- Claude "forgets" to update state.md after compaction
- Credentials stop working mid-session
- Methodology steps get skipped
- Earlier learnings lost

**Root Cause:** Context compaction discards information Claude deemed less important, but that info was actually critical (credentials, methodology rules, current task state).

### Session Management Strategy

```
Option A: Task-Based Restart (Simple)
- After every 3-5 tasks, force session restart
- Save state to files before restart
- New session reads state files to resume

Option B: Token-Based Restart (Smart) ← Preferred
- Monitor estimated token usage per task
- Calculate session budget from context window
- Batch tasks to stay under 75% threshold
- Restart proactively, never hit compaction

Option C: Hybrid (Safest)
- Use token estimates for planning
- Also hard-cap at 5 tasks regardless
- Detect compaction as fallback
- Auto-recover if detection triggers
```

### Compaction-Resistant Context

```markdown
<!-- CRITICAL: This section MUST survive context compaction -->
<!-- ALWAYS_INCLUDE_START -->

## Mandatory Actions (NEVER SKIP)
1. Update state.md after completing ANY task
2. Run tests before marking task done
3. Move Trello cards when status changes
4. Use bpsai-pair commands for all task management

## Active Credentials
- Trello: Board ID 694176ebf4b9d27c6e7a0e73
- GitHub: Authenticated via gh CLI

## Current Task
- ID: TASK-081
- Title: Sync Trello custom fields
- Status: in_progress

<!-- ALWAYS_INCLUDE_END -->
```

### Enforcement Points

```
Session Start
├── Load checkpoint if exists
├── Verify credentials working
├── Check session budget
└── Plan task batch

Task Start
├── Has task file? ✓ Required
├── Task has implementation plan? ✓ Required
├── State.md updated with "Current Focus"? ✓ Required
├── Session token check? ✓ Warn if >70% estimated
└── Trello card in "In Progress"? ✓ If Trello enabled

During Task
├── Running tests periodically? ✓ Recommended
├── Committing incrementally? ✓ Recommended
├── Adding comments to Trello? ✓ If Trello enabled
├── Compaction check? ✓ Verify critical markers
└── Token threshold check? ✓ Checkpoint if >80%

Task Complete
├── Tests passing? ✓ Required
├── State.md updated with "What Was Done"? ✓ Required
├── Trello card in "Done"? ✓ If Trello enabled
├── PR created? ✓ If GitHub enabled
├── Time logged? ✓ If timer enabled
└── Session restart needed? ✓ Check batch plan

Session End
├── Run /update-skills ✓ Capture learnings
├── Checkpoint state ✓ Save for next session
├── Log metrics ✓ Actual tokens used
└── Start new session ✓ Fresh context
```

### Success Criteria
- [ ] Cannot complete task without state.md update
- [ ] Cannot commit without tests passing
- [ ] Cannot skip planning phase
- [ ] Process compliance visible and tracked
- [ ] Sessions planned using token estimates
- [ ] Batch sizes respect context window budget
- [ ] Compaction detected within 1 exchange if it happens
- [ ] Recovery restores critical context automatically
- [ ] Credentials persist across session restarts
- [ ] Key context survives compaction (if it happens despite planning)

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

## Sprint 20: Emergent Skill Discovery 🧠

> **Goal:** Self-improving system that discovers missing skills from failures and creates them.

### The Vision (Credit: EricGT)

```
Plan (uses Skills) → Execute → Miss → New Skill → Better Next Plan
         ↑                                              ↓
         └──────────── Feedback Loop ──────────────────┘
```

**"The loop is like a gear on a clock, and then a new gear emerges for creating skills that are more fundamental but of more value."**

### Working Reference Implementation

A community member shared a working `/update-skills` command that does exactly this:

```
.claude/skills/skill-creation/
├── SKILL.md          # Skill creation best practices
└── refactoring.md    # Patterns for improving existing skills

.claude/commands/
└── update-skills.md  # Slash command that captures session learnings
```

**Key insight:** The entire workflow (Plan → Execute → Learn → Update Skills) must happen in ONE conversation so context is preserved when `/update-skills` runs.

### Tasks

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| TASK-122 | Execution failure categorization | Classify WHY tasks fail (missing knowledge, wrong approach, etc.) | 35 |
| TASK-123 | Skill gap detection | Identify patterns in failures that suggest missing skills | 45 |
| TASK-124 | Skill proposal generator | Auto-generate skill proposals from failure patterns | 50 |
| TASK-125 | Skill authoring agent | Agent that writes SKILL.md files from proposals | 40 |
| TASK-126 | Skill effectiveness tracking | Measure if new skills improve success rate | 35 |
| TASK-127 | Skill refinement loop | Iterate on skills that underperform | 40 |
| TASK-128 | Skill genealogy tracking | Track which skills spawned which (the "clock gears") | 30 |
| TASK-131 | `/update-skills` command | Slash command to capture session learnings as skills | 35 |
| TASK-132 | Skill refactoring automation | Auto-generalize overly specific skills | 40 |

### The `/update-skills` Command

At the end of a session (before context loss), run:

```
/update-skills
```

This command:
1. Analyzes what was learned in the session
2. Checks existing skills for overlap
3. Creates new skills or extends existing ones
4. Updates skill README.md index
5. Follows skill structure best practices

### Skill Structure Requirements (from Community)

```yaml
# Every skill MUST be a directory with SKILL.md
skill-name/
├── SKILL.md              # REQUIRED: YAML frontmatter + entry point (<500 lines)
├── reference.md          # Optional: detailed content
└── examples.md           # Optional: examples

# SKILL.md frontmatter is REQUIRED:
---
name: skill-name-lowercase-hyphens
description: Third person description (max 1024 chars). Includes WHAT it does AND WHEN to use it.
---
```

### Skill Quality Checklist

**Discovery & Metadata:**
- [ ] Name: lowercase, hyphens, gerund form (analyzing- not analyze-)
- [ ] Name: descriptive and specific (not helper, utils, tools)
- [ ] Description: under 1024 chars, third-person voice
- [ ] Description: includes WHAT it does AND WHEN to use it

**Token Efficiency:**
- [ ] SKILL.md body: under 500 lines
- [ ] No information Claude already knows
- [ ] Progressive disclosure: supporting files for details

**Actionability:**
- [ ] "When to Use" section with clear triggers
- [ ] Quick reference tables or checklists
- [ ] Concrete examples (input/output pairs)

### How It Works

```
1. Agent attempts task using existing skills
         ↓
2. Task fails or succeeds with friction
         ↓
3. Failure analyzer categorizes the issue:
   - "Didn't know how to X" → Knowledge gap
   - "Tried wrong approach" → Methodology gap
   - "Kept repeating mistake" → Pattern gap
         ↓
4. At session end, run /update-skills
         ↓
5. Skill gap detector looks for patterns:
   - "3 tasks failed due to missing Trello webhook knowledge"
   - "Pattern: agents keep forgetting to update state.md"
         ↓
6. Skill proposal generated:
   - "Proposed: trello-webhook-debugging skill"
   - "Proposed: mandatory-state-update skill"
         ↓
7. Human reviews OR auto-approved if confidence high
         ↓
8. Skill authoring agent writes SKILL.md
         ↓
9. New skill available for next session
         ↓
10. Effectiveness tracked over time
```

### Critical Workflow Note

> **All of this must happen in ONE conversation.** The learnings that inform skill creation are in the context. If you start a new session, the context is lost and `/update-skills` won't know what was learned.

**Solution:** Run `/update-skills` BEFORE ending a session, not after starting a new one.

### Failure Categories

| Category | Example | Skill Type Needed |
|----------|---------|-------------------|
| Knowledge Gap | "Didn't know Trello API rate limits" | Reference skill |
| Methodology Gap | "Skipped planning phase" | Process skill |
| Pattern Gap | "Repeated same bug 3 times" | Checklist skill |
| Tool Gap | "No command for X exists" | New CLI command |
| Integration Gap | "A and B don't work together" | Integration skill |

### Skill Genealogy (The Clock Gears)

```
Level 0: Manual skills (human-written)
    ↓
Level 1: First-order skills (from direct failures)
    - "trello-card-debugging" (from Trello sync failures)
    ↓
Level 2: Meta-skills (from skill creation patterns)  
    - "skill-authoring" (how to write good skills)
    ↓
Level 3: Fundamental skills (emerge from meta-patterns)
    - "failure-pattern-recognition" 
    - "self-documentation"
```

### Community Resources

- [Anthropic's skill authoring best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [anthropics/skills GitHub repo](https://github.com/anthropics/skills)
- [obra/superpowers](https://github.com/obra/superpowers) - TDD patterns
- [lean4-skills](https://github.com/cameronfreer/lean4-skills) - Theorem proving skills (worth studying structure)

### Success Criteria

- [ ] `/update-skills` command exists and works
- [ ] System detects when tasks fail due to missing skills
- [ ] At least 3 skills auto-proposed from failure patterns
- [ ] At least 1 auto-generated skill improves success rate
- [ ] Skill genealogy shows emergence of meta-skills
- [ ] Human can review/approve proposed skills before creation
- [ ] Skills get auto-refactored from specific to general over time

### Why This Is Transformative

1. **Self-improving** - Gets better without manual intervention
2. **Discovers unknown unknowns** - Finds gaps humans didn't anticipate
3. **Compounds over time** - Each skill makes future tasks easier
4. **Creates fundamental knowledge** - The "second gear" emergence
5. **Community-proven** - Pattern already working in production

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
Sprint 17 (Metrics + Tokens) - Measure everything, estimate token usage.
     ↓
Sprint 18 (Sessions + Recovery) - Use metrics to plan safe sessions, recover from failures.
     ↓
Sprint 19 (Cross-Platform) - Skills work on ANY agent platform.
     ↓
Sprint 20 (Skill Discovery) - System improves itself from failures.
     ↓
Remote API - Full remote orchestration capability.
```

### The Token-Aware Pipeline

```
Sprint 17 outputs → Sprint 18 inputs

Complexity → Token estimate ──→ Session budget calculator
                                        ↓
Task type multiplier ──────────→ Batch planning algorithm
                                        ↓
Historical actuals ←─────────── Session execution metrics
       ↓
Improved estimates
```

### Critical Workflow Insight

> **From community experience:** The entire Plan → Execute → Learn → Update Skills workflow must happen in ONE conversation. If you start a new session, the context is lost and skill discovery won't work.

**Sprint 17-18 solve this by:**
1. Estimating tokens per task (Sprint 17)
2. Planning sessions to stay under compaction threshold (Sprint 18)
3. Forcing `/update-skills` BEFORE session restart (Sprint 18)
4. Checkpointing critical state (Sprint 18)
5. Detecting and recovering from unexpected compaction (Sprint 18)

---

## Quick Reference: All Tasks

| Sprint | Theme | Tasks | IDs |
|--------|-------|-------|-----|
| 13 | Full Autonomy | ✅ Complete | TASK-066 - 080 |
| 14 | Trello Deep | 8 tasks | TASK-081 - 088 |
| 15 | Security | 7 tasks | TASK-089 - 095 |
| 16 | Sub-agents | 6 tasks | TASK-096 - 101 |
| 17 | Metrics & Tokens | 8 tasks | TASK-102 - 107, 133, 138 |
| 18 | Sessions & Recovery | 12 tasks | TASK-108 - 113, 129-130, 134-137 |
| 19 | Cross-Platform | 7 tasks | TASK-115 - 121 |
| 20 | Skill Discovery 🧠 | 9 tasks | TASK-122 - 128, 131-132 |
| Backlog | Remote API | 1 task | TASK-114 |
| **Total New** | | **58** | |

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
**Status:** Being addressed in current Sprint 14 work

### Context Compaction Problem
**Issue:** Claude "forgets" critical info after context compaction
**Symptoms:**
- Credentials stop working mid-session
- state.md updates get skipped
- Methodology steps forgotten
**Root Cause:** Compaction discards info Claude deemed less important
**Workaround:** Restart sessions every 3-5 tasks
**Permanent Fix:** 
- Sprint 17: Token estimation model (predict when we're at risk)
- Sprint 18: Batch planning + compaction detection + recovery

### Skill Discovery Context Loss
**Issue:** `/update-skills` needs full session context to work
**Impact:** Can't discover skills from learnings if session restarted too early
**Fix:** 
- Run `/update-skills` BEFORE ending session
- Sprint 18 enforces this in the session restart protocol

---

## Notes

- All task IDs are sequential and assigned
- Complexity points are estimates - refine during planning
- Order within sprint can be adjusted based on dependencies
- Some tasks may split or merge during implementation
- Test coverage target: maintain 400+ tests
