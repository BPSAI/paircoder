---
id: TASK-090
title: Command allowlist system
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P0
complexity: 35
status: done
sprint: sprint-15
tags:
- security
- allowlist
- commands
depends_on:
- TASK-089
---

# Objective

Implement a command allowlist system that defines safe vs unsafe commands for autonomous execution.

# Implementation Plan

1. Create allowlist configuration file:
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

2. Create AllowlistManager class:
   - `load_allowlist()` - Load from config file
   - `check_command(cmd)` - Returns allow/review/block status
   - `get_blocked_reason(cmd)` - Explain why command is blocked
   - `add_to_allowlist(cmd)` - Add trusted command

3. Integrate with Claude Code hooks:
   - Pre-execution check for bash commands
   - Return block message with explanation

# Acceptance Criteria

- [ ] Allowlist config file created and documented
- [ ] AllowlistManager class with check/explain methods
- [ ] Always-allowed commands execute without prompt
- [ ] Review-required commands trigger confirmation
- [ ] Blocked commands rejected with clear explanation
- [ ] Pattern matching works for complex commands
- [ ] Config can be customized per-project

# Files to Create/Modify

- `.paircoder/security/allowlist.yaml` (new)
- `tools/cli/bpsai_pair/security/__init__.py` (new)
- `tools/cli/bpsai_pair/security/allowlist.py` (new)
- `tests/test_security_allowlist.py` (new)