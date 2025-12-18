---
id: TASK-089
title: Security agent definition
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P0
complexity: 30
status: done
sprint: sprint-15
tags:
- security
- agent
- soc2
---

# Objective

Create a security agent definition file that reviews code changes and commands for security issues before execution, with SOC2 compliance focus.

# Implementation Plan

1. Create `.claude/agents/security.md` with:
   - Role definition for security review
   - Security checklist (credentials, injection, dependencies, etc.)
   - Blocking conditions (when to halt execution)
   - SOC2 control mapping

2. Define security review triggers:
   - Before git commit
   - Before PR creation
   - When adding new dependencies
   - When modifying auth/permission code

3. Create agent prompt template:
   ```markdown
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
   ```

# Acceptance Criteria

- [ ] Security agent definition file created at `.claude/agents/security.md`
- [ ] Agent has clear checklist of security concerns
- [ ] Blocking conditions defined (credentials, dangerous commands)
- [ ] Warning conditions defined (new dependencies, permission changes)
- [ ] SOC2 control references included
- [ ] Agent can be invoked by other agents/flows

# Files to Create/Modify

- `.claude/agents/security.md` (new)
- `.paircoder/flows/security-review.flow.md` (new)
- `docs/SECURITY.md` (new)