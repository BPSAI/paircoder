# Sprint 29.2: Comprehensive Audit

> Pre-v3.0 quality gate - Know what works before building the wizard

**Goal:** Systematic audit of all PairCoder functionality to identify dead code, stale modules, broken features, and gaps between documentation and reality.

**Start Date:** After Sprint 29.1 (Hotfixes)
**Target:** Audit Report + Prioritized Fix List
**Effort:** ~24-32 hours

---

## Audit Methodology

For each module/feature:
1. **Exists?** - Is the code present?
2. **Tested?** - Are there tests? Do they pass?
3. **Documented?** - Does documentation match reality?
4. **Used?** - Is it actually invoked anywhere?
5. **Works?** - Manual verification
6. **Monolithic?** - Should this module be broken into several smaller components for ease of maintainability? 

---

## Part 1: CLI Command Inventory

### 1.1 Core Commands (commands/core.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `init` | `bpsai-pair init --help` | Shows help | ☐ | |
| `init --preset bps` | Create temp dir, run init | Creates .paircoder/, .claude/ | ☐ | |
| `feature` | `bpsai-pair feature test-branch` | Creates git branch | ☐ | |
| `pack` | `bpsai-pair pack` | Creates agent_pack.tgz | ☐ | |
| `pack --lite` | `bpsai-pair pack --lite` | Creates smaller pack | ☐ | |
| `context-sync` | `bpsai-pair context-sync --last "test"` | Updates state.md | ☐ | |
| `status` | `bpsai-pair status` | Shows project status | ☐ | |
| `validate` | `bpsai-pair validate` | Validates structure | ☐ | |
| `ci` | `bpsai-pair ci` | Runs CI checks | ☐ | |

### 1.2 Planning Commands (planning/commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `plan new` | `bpsai-pair plan new test --type feature` | Creates plan YAML | ☐ | |
| `plan list` | `bpsai-pair plan list` | Lists plans | ☐ | |
| `plan show` | `bpsai-pair plan show <id>` | Shows plan details | ☐ | |
| `plan tasks` | `bpsai-pair plan tasks <id>` | Lists plan tasks | ☐ | |
| `plan status` | `bpsai-pair plan status` | Shows plan progress | ☐ | |
| `plan sync-trello` | `bpsai-pair plan sync-trello <id>` | Syncs to Trello | ☐ | Requires Trello |
| `plan add-task` | `bpsai-pair plan add-task <id> --title "Test"` | Adds task | ☐ | |
| `plan estimate` | `bpsai-pair plan estimate <id>` | Shows estimates | ☐ | |

### 1.3 Task Commands (planning/commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `task list` | `bpsai-pair task list` | Lists tasks | ☐ | |
| `task show` | `bpsai-pair task show <id>` | Shows task | ☐ | |
| `task update` | `bpsai-pair task update <id> --status in_progress` | Updates status | ☐ | |
| `task next` | `bpsai-pair task next` | Suggests next task | ☐ | |
| `task auto-next` | `bpsai-pair task auto-next` | Auto-starts next | ☐ | |
| `task archive` | `bpsai-pair task archive <id>` | Archives task | ☐ | |
| `task restore` | `bpsai-pair task restore <id>` | Restores task | ☐ | |
| `task list-archived` | `bpsai-pair task list-archived` | Lists archived | ☐ | |
| `task cleanup` | `bpsai-pair task cleanup` | Cleans old tasks | ☐ | |
| `task changelog-preview` | `bpsai-pair task changelog-preview` | Preview changelog | ☐ | |

### 1.4 Trello Commands (trello/commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `trello connect` | `bpsai-pair trello connect` | Interactive setup | ☐ | |
| `trello status` | `bpsai-pair trello status` | Shows connection | ☐ | |
| `trello disconnect` | `bpsai-pair trello disconnect` | Removes connection | ☐ | |
| `trello boards` | `bpsai-pair trello boards` | Lists boards | ☐ | |
| `trello use-board` | `bpsai-pair trello use-board <id>` | Selects board | ☐ | |
| `trello lists` | `bpsai-pair trello lists` | Shows lists | ☐ | |
| `trello config` | `bpsai-pair trello config` | Shows config | ☐ | |
| `trello progress` | `bpsai-pair trello progress` | Posts progress | ☐ | |
| `trello webhook serve` | `bpsai-pair trello webhook serve` | Starts webhook | ☐ | |
| `trello webhook status` | `bpsai-pair trello webhook status` | Shows webhook | ☐ | |

### 1.5 Trello Task Commands (trello/task_commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `ttask list` | `bpsai-pair ttask list` | Lists cards | ☐ | |
| `ttask show` | `bpsai-pair ttask show TRELLO-XX` | Shows card | ☐ | |
| `ttask start` | `bpsai-pair ttask start TRELLO-XX` | Starts task | ☐ | Budget check? |
| `ttask done` | `bpsai-pair ttask done TRELLO-XX` | Completes task | ☐ | AC check? |
| `ttask block` | `bpsai-pair ttask block TRELLO-XX` | Blocks task | ☐ | |
| `ttask comment` | `bpsai-pair ttask comment TRELLO-XX "msg"` | Adds comment | ☐ | |
| `ttask move` | `bpsai-pair ttask move TRELLO-XX "List"` | Moves card | ☐ | |

### 1.6 GitHub Commands (github/commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `github status` | `bpsai-pair github status` | Shows GH status | ☐ | |
| `github create` | `bpsai-pair github create --help` | Shows help | ☐ | |
| `github list` | `bpsai-pair github list` | Lists PRs | ☐ | |
| `github merge` | `bpsai-pair github merge <pr>` | Merges PR | ☐ | |
| `github link` | `bpsai-pair github link <pr> <task>` | Links PR to task | ☐ | |
| `github auto-pr` | `bpsai-pair github auto-pr` | Creates PR | ☐ | |
| `github archive-merged` | `bpsai-pair github archive-merged` | Archives tasks | ☐ | |

### 1.7 Skills Commands (skills/cli_commands.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `skill list` | `bpsai-pair skill list` | Lists skills | ☐ | |
| `skill validate` | `bpsai-pair skill validate` | Validates skills | ☐ | |
| `skill export` | `bpsai-pair skill export <name> --format cursor` | Exports skill | ☐ | |
| `skill install` | `bpsai-pair skill install <url>` | Installs skill | ☐ | |
| `skill suggest` | `bpsai-pair skill suggest "build feature"` | Suggests skill | ☐ | |
| `skill gaps` | `bpsai-pair skill gaps` | Shows gaps | ☐ | |
| `skill generate` | `bpsai-pair skill generate` | Generates skill | ☐ | |

### 1.8 Orchestration Commands (commands/orchestrate.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `orchestrate task` | `bpsai-pair orchestrate task <id>` | Orchestrates task | ☐ | |
| `orchestrate analyze` | `bpsai-pair orchestrate analyze <id>` | Analyzes complexity | ☐ | |
| `orchestrate handoff` | `bpsai-pair orchestrate handoff` | Creates handoff | ☐ | |
| `orchestrate auto-run` | `bpsai-pair orchestrate auto-run` | Auto runs | ☐ | |
| `orchestrate auto-session` | `bpsai-pair orchestrate auto-session` | Auto session | ☐ | |
| `orchestrate workflow-status` | `bpsai-pair orchestrate workflow-status` | Shows status | ☐ | |

### 1.9 Metrics Commands (commands/metrics.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `metrics summary` | `bpsai-pair metrics summary` | Shows summary | ☐ | |
| `metrics task` | `bpsai-pair metrics task <id>` | Task metrics | ☐ | |
| `metrics breakdown` | `bpsai-pair metrics breakdown` | Breakdown | ☐ | |
| `metrics budget` | `bpsai-pair metrics budget` | Budget info | ☐ | |
| `metrics export` | `bpsai-pair metrics export` | Exports CSV | ☐ | |
| `metrics velocity` | `bpsai-pair metrics velocity` | Velocity | ☐ | |
| `metrics burndown` | `bpsai-pair metrics burndown` | Burndown | ☐ | |
| `metrics accuracy` | `bpsai-pair metrics accuracy` | Accuracy | ☐ | |
| `metrics tokens` | `bpsai-pair metrics tokens` | Token usage | ☐ | |

### 1.10 Session/Budget Commands (commands/session.py, commands/budget.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `session check` | `bpsai-pair session check` | Checks session | ☐ | |
| `session status` | `bpsai-pair session status` | Session status | ☐ | |
| `budget estimate` | `bpsai-pair budget estimate <task>` | Estimates | ☐ | |
| `budget status` | `bpsai-pair budget status` | Budget status | ☐ | |
| `budget check` | `bpsai-pair budget check --task <id>` | Checks budget | ☐ | |

### 1.11 Security Commands (commands/security.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `security scan-secrets` | `bpsai-pair security scan-secrets` | Scans secrets | ☐ | |
| `security pre-commit` | `bpsai-pair security pre-commit` | Pre-commit check | ☐ | |
| `security install-hook` | `bpsai-pair security install-hook` | Installs hook | ☐ | |
| `security scan-deps` | `bpsai-pair security scan-deps` | Scans deps | ☐ | |
| `scan-secrets` (shortcut) | `bpsai-pair scan-secrets` | Same as above | ☐ | |
| `scan-deps` (shortcut) | `bpsai-pair scan-deps` | Same as above | ☐ | |

### 1.12 Containment Commands (commands/session.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `contained-auto` | `bpsai-pair contained-auto --help` | Shows help | ☐ | |
| `containment status` | `bpsai-pair containment status` | Shows status | ☐ | |
| `containment rollback` | `bpsai-pair containment rollback --help` | Shows help | ☐ | |
| `containment checkpoints` | `bpsai-pair containment checkpoints` | Lists checkpoints | ☐ | |

### 1.13 Other Commands

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `preset list` | `bpsai-pair preset list` | Lists presets | ☐ | |
| `preset show` | `bpsai-pair preset show bps` | Shows preset | ☐ | |
| `preset preview` | `bpsai-pair preset preview bps` | Previews preset | ☐ | |
| `intent detect` | `bpsai-pair intent detect "build feature"` | Detects intent | ☐ | |
| `intent should-plan` | `bpsai-pair intent should-plan "fix bug"` | Advises | ☐ | |
| `standup generate` | `bpsai-pair standup generate` | Generates standup | ☐ | |
| `standup post` | `bpsai-pair standup post` | Posts standup | ☐ | |
| `sprint list` | `bpsai-pair sprint list` | Lists sprints | ☐ | |
| `sprint complete` | `bpsai-pair sprint complete <id>` | Completes sprint | ☐ | |
| `release plan` | `bpsai-pair release plan` | Plans release | ☐ | |
| `release checklist` | `bpsai-pair release checklist` | Shows checklist | ☐ | |
| `release prep` | `bpsai-pair release prep` | Preps release | ☐ | |
| `template check` | `bpsai-pair template check` | Checks templates | ☐ | |
| `template list` | `bpsai-pair template list` | Lists templates | ☐ | |
| `timer start` | `bpsai-pair timer start` | Starts timer | ☐ | |
| `timer stop` | `bpsai-pair timer stop` | Stops timer | ☐ | |
| `timer status` | `bpsai-pair timer status` | Timer status | ☐ | |
| `timer show` | `bpsai-pair timer show` | Shows timer | ☐ | |
| `timer summary` | `bpsai-pair timer summary` | Summary | ☐ | |
| `benchmark run` | `bpsai-pair benchmark run` | Runs benchmark | ☐ | |
| `benchmark results` | `bpsai-pair benchmark results` | Shows results | ☐ | |
| `benchmark compare` | `bpsai-pair benchmark compare` | Compares | ☐ | |
| `benchmark list` | `bpsai-pair benchmark list` | Lists benchmarks | ☐ | |
| `cache stats` | `bpsai-pair cache stats` | Cache stats | ☐ | |
| `cache clear` | `bpsai-pair cache clear` | Clears cache | ☐ | |
| `cache invalidate` | `bpsai-pair cache invalidate` | Invalidates | ☐ | |
| `audit bypasses` | `bpsai-pair audit bypasses` | Shows bypasses | ☐ | |
| `audit summary` | `bpsai-pair audit summary` | Summary | ☐ | |
| `audit clear` | `bpsai-pair audit clear` | Clears audit | ☐ | |
| `state show` | `bpsai-pair state show` | Shows state | ☐ | |
| `state list` | `bpsai-pair state list` | Lists states | ☐ | |
| `state history` | `bpsai-pair state history` | State history | ☐ | |
| `state reset` | `bpsai-pair state reset` | Resets state | ☐ | |
| `state advance` | `bpsai-pair state advance` | Advances state | ☐ | |
| `upgrade` | `bpsai-pair upgrade --help` | Shows help | ☐ | |
| `migrate` | `bpsai-pair migrate --help` | Shows help | ☐ | |
| `migrate status` | `bpsai-pair migrate status` | Shows status | ☐ | |

### 1.14 MCP Commands (commands/mcp.py)

| Command | Test Command | Expected | Status | Notes |
|---------|--------------|----------|--------|-------|
| `mcp serve` | `bpsai-pair mcp serve --help` | Shows help | ☐ | |
| `mcp tools` | `bpsai-pair mcp tools` | Lists tools | ☐ | |
| `mcp test` | `bpsai-pair mcp test <tool>` | Tests tool | ☐ | |

---

## Part 2: Module Health Check

### 2.1 Core Modules

| Module | File | Lines | Tests? | Last Updated | Status | Notes |
|--------|------|-------|--------|--------------|--------|-------|
| Config | core/config.py | ? | ☐ | ? | ☐ | |
| Hooks | core/hooks.py | ? | ☐ | ? | ☐ | |
| Operations | core/ops.py | ? | ☐ | ? | ☐ | |
| Presets | core/presets.py | ? | ☐ | ? | ☐ | |
| Utils | core/utils.py | ? | ☐ | ? | ☐ | |

### 2.2 Security Modules

| Module | File | Lines | Tests? | Last Updated | Status | Notes |
|--------|------|-------|--------|--------------|--------|-------|
| Allowlist | security/allowlist.py | ? | ☐ | ? | ☐ | |
| Review | security/review.py | ? | ☐ | ? | ☐ | |
| Sandbox | security/sandbox.py | ? | ☐ | ? | ☐ | |
| Checkpoint | security/checkpoint.py | ? | ☐ | ? | ☐ | |

### 2.3 Planning Modules

| Module | File | Lines | Tests? | Last Updated | Status | Notes |
|--------|------|-------|--------|--------------|--------|-------|
| Models | planning/models.py | ? | ☐ | ? | ☐ | |
| Parser | planning/parser.py | ? | ☐ | ? | ☐ | |
| State | planning/state.py | ? | ☐ | ? | ☐ | |
| Commands | planning/commands.py | ? | ☐ | ? | ☐ | 2,119 lines! |

### 2.4 Integration Modules

| Module | File | Lines | Tests? | Last Updated | Status | Notes |
|--------|------|-------|--------|--------------|--------|-------|
| Trello Commands | trello/commands.py | ? | ☐ | ? | ☐ | |
| Trello Tasks | trello/task_commands.py | ? | ☐ | ? | ☐ | 965 lines |
| GitHub | github/commands.py | ? | ☐ | ? | ☐ | |
| MCP Server | mcp/ | ? | ☐ | ? | ☐ | Stale? |

### 2.5 Other Modules

| Module | File | Lines | Tests? | Last Updated | Status | Notes |
|--------|------|-------|--------|--------------|--------|-------|
| Tokens | tokens.py | ? | ☐ | ? | ☐ | |
| Session | session.py | ? | ☐ | ? | ☐ | |
| Metrics | metrics.py | ? | ☐ | ? | ☐ | |
| Compaction | compaction.py | ? | ☐ | ? | ☐ | |
| Upgrade | migrate.py | ? | ☐ | ? | ☐ | Stale? |

---

## Part 3: Config.yaml Field Audit

For each field in config.yaml, determine:
1. Is it documented?
2. Is it actually used in code?
3. Does changing it have any effect?

```bash
# Generate list of all config fields
grep -E "^\s+\w+:" .paircoder/config.yaml | sort | uniq
```

### 3.1 Top-Level Sections

| Section | Used? | Where? | Notes |
|---------|-------|--------|-------|
| version | ☐ | | |
| project | ☐ | | |
| workflow | ☐ | | |
| pack | ☐ | | |
| models | ☐ | | |
| routing | ☐ | | |
| metrics | ☐ | | |
| estimation | ☐ | | |
| token_estimates | ☐ | | |
| token_budget | ☐ | | |
| hooks | ☐ | | |
| release | ☐ | | |
| trello | ☐ | | |
| enforcement | ☐ | | |
| containment | ☐ | | |

### 3.2 Enforcement Fields

| Field | Used? | Where? | Effect Verified? |
|-------|-------|--------|------------------|
| state_machine | ☐ | | ☐ |
| strict_ac_verification | ☐ | | ☐ |
| require_budget_check | ☐ | | ☐ |
| block_no_hooks | ☐ | | ☐ |

### 3.3 Hooks Configuration

| Hook | Registered? | Actually Fires? | Does Something? |
|------|-------------|-----------------|-----------------|
| check_token_budget | ☐ | ☐ | ☐ |
| start_timer | ☐ | ☐ | ☐ |
| stop_timer | ☐ | ☐ | ☐ |
| record_metrics | ☐ | ☐ | ☐ |
| record_task_completion | ☐ | ☐ | ☐ |
| record_velocity | ☐ | ☐ | ☐ |
| record_token_usage | ☐ | ☐ | ☐ |
| log_trello_activity | ☐ | ☐ | ☐ |
| sync_trello | ☐ | ☐ | ☐ |
| update_state | ☐ | ☐ | ☐ |
| check_unblocked | ☐ | ☐ | ☐ |

---

## Part 4: Enforcement Reality Check

### 4.1 Security Gates

| Gate | Code Exists? | Actually Blocks? | Bypass Logged? |
|------|--------------|------------------|----------------|
| AC verification before done | ☐ | ☐ | ☐ |
| Budget check before start | ☐ | ☐ | ☐ |
| Local task update blocked for Trello | ☐ | ☐ | ☐ |
| State machine transitions | ☐ | ☐ | ☐ |

### 4.2 Test Enforcement

```bash
# Test 1: Does AC verification block completion?
bpsai-pair ttask done TRELLO-XXX --strict
# Expected: Blocked if AC items unchecked

# Test 2: Does budget check warn on start?
bpsai-pair ttask start TRELLO-XXX
# Expected: Warning if over budget threshold

# Test 3: Does local update get blocked for Trello tasks?
bpsai-pair task update T29.1 --status done
# Expected: Error message, suggests ttask done

# Test 4: Are bypasses logged?
cat .paircoder/history/bypass_log.jsonl
# Expected: Shows bypass attempts with reasons
```

---

## Part 5: First-Run Experience

### 5.1 Fresh Install Test

```bash
# Simulate fresh install (in temp directory)
mkdir /tmp/paircoder-test && cd /tmp/paircoder-test
git init
pip install bpsai-pair

# Test basic init
bpsai-pair init --preset bps

# Verify created files
ls -la .paircoder/
ls -la .claude/

# Test basic commands work
bpsai-pair status
bpsai-pair skill list
bpsai-pair plan list
```

### 5.2 Known Issues to Check

| Issue | Test | Status | Notes |
|-------|------|--------|-------|
| python vs python3 | `which python && which python3` | ☐ | |
| Missing deps errors | Run commands, check errors | ☐ | |
| Unclear error messages | Note any confusing errors | ☐ | |
| Trello without config | `bpsai-pair ttask list` | ☐ | |
| GitHub without config | `bpsai-pair github status` | ☐ | |

---

## Part 6: Documentation Sync

### 6.1 FEATURE_MATRIX.md Accuracy

| Claimed Feature | Actually Works? | Notes |
|-----------------|-----------------|-------|
| 127+ CLI commands | ☐ | Count actual commands |
| 13 MCP tools | ☐ | Verify tools exist |
| 11 hooks | ☐ | Verify all fire |
| 6+ skills | ☐ | Verify all valid |

### 6.2 Skills Validation

```bash
bpsai-pair skill validate
```

| Skill | Valid? | Tested? |
|-------|--------|---------|
| designing-and-implementing | ☐ | ☐ |
| implementing-with-tdd | ☐ | ☐ |
| reviewing-code | ☐ | ☐ |
| finishing-branches | ☐ | ☐ |
| managing-task-lifecycle | ☐ | ☐ |
| planning-with-trello | ☐ | ☐ |

### 6.3 Slash Commands

| Command | File Exists? | Works in Claude Code? |
|---------|--------------|----------------------|
| /pc-plan | ☐ | ☐ |
| /start-task | ☐ | ☐ |
| /prep-release | ☐ | ☐ |

---

## Part 7: Agent/Subagent Integration

### 7.1 Agent Files

| Agent | File Exists? | Referenced? | Ever Invoked? |
|-------|--------------|-------------|---------------|
| planner.md | ☐ | ☐ | ☐ |
| reviewer.md | ☐ | ☐ | ☐ |
| security.md | ☐ | ☐ | ☐ |
| security-auditor.md | ☐ | ☐ | ☐ |

### 7.2 Native Claude Capabilities

| Feature | PairCoder Uses? | Or Overrides? |
|---------|-----------------|---------------|
| Multi-agent planning | ☐ | ☐ |
| Navigator role | ☐ | ☐ |
| Driver role | ☐ | ☐ |
| Reviewer role | ☐ | ☐ |

---

## Part 8: MCP Server Audit

### 8.1 Tool Inventory

```bash
bpsai-pair mcp tools
```

| Tool | Exists? | Tested? | Matches CLI? |
|------|---------|---------|--------------|
| paircoder_task_list | ☐ | ☐ | ☐ |
| paircoder_task_next | ☐ | ☐ | ☐ |
| paircoder_task_start | ☐ | ☐ | ☐ |
| paircoder_task_complete | ☐ | ☐ | ☐ |
| paircoder_context_read | ☐ | ☐ | ☐ |
| paircoder_plan_status | ☐ | ☐ | ☐ |
| paircoder_plan_list | ☐ | ☐ | ☐ |
| paircoder_orchestrate_analyze | ☐ | ☐ | ☐ |
| paircoder_orchestrate_handoff | ☐ | ☐ | ☐ |
| paircoder_metrics_record | ☐ | ☐ | ☐ |
| paircoder_metrics_summary | ☐ | ☐ | ☐ |
| paircoder_trello_sync_plan | ☐ | ☐ | ☐ |
| paircoder_trello_update_card | ☐ | ☐ | ☐ |

### 8.2 MCP vs CLI Drift

Are MCP tools calling current CLI commands or outdated ones? Do new MCP tool calls need introduced to make MCP use current with all capabilities? 

---

## Part 9: Test Coverage Analysis

```bash
# Run with coverage
cd tools/cli
pytest --cov=bpsai_pair --cov-report=html

# Check coverage report
open htmlcov/index.html
```

### 9.1 Coverage by Module

| Module | Coverage % | Critical Gaps |
|--------|------------|---------------|
| core/ | ? | |
| commands/ | ? | |
| planning/ | ? | |
| trello/ | ? | |
| security/ | ? | |
| skills/ | ? | |

---

## Deliverables

After completing this audit:

1. **Audit Report** - Summary of findings
2. **Dead Code List** - Modules/commands to remove
3. **Refactor List** - What modules need broken down from monolithic to modular to ensure ease of maintainability and extensibility
4. **Fix Priority List** - Ordered by impact
5. **Documentation Updates** - What needs changing
6. **Wizard Requirements** - What config fields matter

---

## Audit Commands Cheatsheet

```bash
# Count all commands
bpsai-pair --help | grep -E "^\s+\w+" | wc -l

# Count lines per module
find tools/cli/bpsai_pair -name "*.py" -exec wc -l {} \; | sort -n

# Find unused imports
cd tools/cli && ruff check --select F401 .

# Find unused functions (approximate)
grep -r "def " bpsai_pair/ | wc -l

# Run all tests
cd tools/cli && pytest -v

# Check for TODOs/FIXMEs
grep -rn "TODO\|FIXME\|XXX\|HACK" bpsai_pair/
```
