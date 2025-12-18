---
id: TASK-091
title: Pre-execution security review
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P0
complexity: 45
status: done
sprint: sprint-15
tags:
- security
- review
- hooks
depends_on:
- TASK-089
- TASK-090
---

# Objective

Implement pre-execution security review where the security agent reviews commands and code changes before they run.

# Implementation Plan

1. Create security review hook:
   ```python
   class SecurityReviewHook:
       def pre_execute(self, command: str) -> ReviewResult:
           """Review command before execution."""
           allowlist_check = self.allowlist.check_command(command)
           if allowlist_check == "blocked":
               return ReviewResult.block(self.allowlist.get_blocked_reason(command))
           if allowlist_check == "review":
               return self.security_agent.review_command(command)
           return ReviewResult.allow()
   ```

2. Create code change reviewer:
   - Review staged git changes before commit
   - Check for hardcoded secrets
   - Check for injection vulnerabilities
   - Verify input validation

3. Integrate with Claude Code:
   - Hook into Bash tool calls
   - Hook into git commit operations
   - Hook into PR creation

4. Create review result types:
   ```python
   @dataclass
   class ReviewResult:
       allowed: bool
       reason: str
       warnings: list[str]
       suggested_fixes: list[str]
   ```

# Acceptance Criteria

- [ ] Security review runs before blocked/review commands
- [ ] Blocked commands show clear explanation
- [ ] Review commands show security analysis
- [ ] Code changes scanned for common vulnerabilities
- [ ] Warnings shown for risky patterns
- [ ] Can bypass with explicit user confirmation
- [ ] Review results logged for audit

# Files to Create/Modify

- `tools/cli/bpsai_pair/security/review.py` (new)
- `tools/cli/bpsai_pair/security/hooks.py` (new)
- `.claude/hooks/security-review.md` (new)
- `tests/test_security_review.py` (new)