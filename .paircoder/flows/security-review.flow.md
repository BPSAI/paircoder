---
name: security-review
version: 1
description: >
  Pre-execution security review flow. Run before commits, PRs, or risky operations
  to catch security issues before they happen.
when_to_use:
  - Before committing code with sensitive changes
  - Before creating a PR
  - When adding new dependencies
  - When modifying auth/permission code
  - Before running unfamiliar commands
roles:
  security:
    primary: true
    description: Reviews operations for security issues
triggers:
  - pre_commit
  - pre_pr
  - new_dependency
  - auth_change
  - user_request
requires:
  tools:
    - git
    - grep
  context:
    - .paircoder/context/state.md
  agents:
    - security
tags:
  - security
  - compliance
  - soc2
  - pre-execution
---

# Security Review Flow

## Purpose

This flow ensures security is checked **before** risky operations execute, not after. It acts as a gatekeeper that blocks dangerous patterns and warns on risky ones.

## Preconditions

Before starting this flow:

- [ ] You have changes to review (staged, committed, or proposed)
- [ ] You understand what operation is about to happen
- [ ] Security agent is available

---

## Phase 1 — Identify Review Scope

### Step 1.1: Determine What to Review

Identify the type of operation:

| Trigger | Scope |
|---------|-------|
| Pre-commit | Staged changes (`git diff --staged`) |
| Pre-PR | All commits on branch (`git diff main..HEAD`) |
| New dependency | Package being added |
| Auth change | Auth/permission related files |
| Command | Specific command to execute |

### Step 1.2: Gather Context

```bash
# For commits - get staged changes
git diff --staged

# For PRs - get all branch changes
git diff main..HEAD

# For files - identify changed files
git diff --staged --name-only
```

---

## Phase 2 — Secret Detection

### Step 2.1: Scan for Hardcoded Secrets

Check for common secret patterns:

```bash
# API keys
git diff --staged | grep -E "AKIA[0-9A-Z]{16}|api_key.*=.*['\"][^'\"]+['\"]"

# Tokens
git diff --staged | grep -E "ghp_[A-Za-z0-9]{36}|xox[baprs]-"

# Passwords
git diff --staged | grep -iE "password\s*[=:]\s*['\"][^'\"]+['\"]"

# Private keys
git diff --staged | grep -E "BEGIN.*PRIVATE KEY"
```

### Step 2.2: Check for Sensitive Files

```bash
# Check for common sensitive file patterns
git diff --staged --name-only | grep -E "\.(env|pem|key|p12|pfx|credentials)$"
```

**Gate:** If secrets detected → BLOCK with location and remediation.

---

## Phase 3 — Vulnerability Scan

### Step 3.1: Check for Injection Vulnerabilities

Scan for:

- [ ] SQL injection (unparameterized queries)
- [ ] Command injection (string interpolation in shell commands)
- [ ] Path traversal (user input in file paths)
- [ ] XSS (unescaped user input in HTML)

### Step 3.2: Check Input Validation

For each function that accepts external input:

- [ ] Input is validated before use
- [ ] Validation is appropriate for the data type
- [ ] Error cases are handled

### Step 3.3: Check for Dangerous Patterns

```bash
# eval/exec usage
git diff --staged | grep -E "eval\(|exec\(|os\.system\("

# Shell command construction
git diff --staged | grep -E "subprocess.*shell=True|os\.popen"

# Path construction with user input
git diff --staged | grep -E "open\(.*\+|Path\(.*\+"
```

**Gate:** If critical vulnerabilities found → BLOCK with explanation.

---

## Phase 4 — Dependency Review

### Step 4.1: Identify New Dependencies

```bash
# Python
git diff --staged -- requirements.txt pyproject.toml setup.py | grep "^+"

# Node
git diff --staged -- package.json | grep "^+"
```

### Step 4.2: Check Dependency Safety

For each new dependency:

- [ ] Is it from a trusted source?
- [ ] Is the version pinned?
- [ ] Are there known vulnerabilities?

```bash
# Python vulnerability check
pip-audit 2>/dev/null

# Node vulnerability check
npm audit 2>/dev/null
```

**Gate:** New dependencies → WARN and require acknowledgment.

---

## Phase 5 — Permission & Auth Review

### Step 5.1: Identify Auth Changes

Check if changes touch:

- [ ] Authentication code
- [ ] Authorization/permission checks
- [ ] Session management
- [ ] Token handling
- [ ] Password handling

### Step 5.2: Verify Security Controls

For auth-related changes:

- [ ] Passwords are hashed (bcrypt, argon2)
- [ ] Tokens are validated server-side
- [ ] Sessions have appropriate expiry
- [ ] Permission checks are present

**Gate:** Auth changes → WARN and flag for careful review.

---

## Phase 6 — Command Review (if applicable)

### Step 6.1: Parse Command

For commands about to execute:

1. Identify the base command
2. Parse all arguments
3. Check for pipes and redirects

### Step 6.2: Check Against Allowlist

```yaml
always_allowed:
  - git status, git diff, git log
  - pytest, bpsai-pair
  - cat, ls, grep (without shell pipes)

requires_review:
  - git push, git commit
  - pip install, npm install
  - docker commands

always_blocked:
  - rm -rf (outside current dir)
  - curl|bash, wget|sh
  - sudo rm
```

### Step 6.3: Return Decision

- ALLOW: Command is safe
- WARN: Command needs acknowledgment
- BLOCK: Command is dangerous

---

## Phase 7 — Generate Security Report

### Step 7.1: Compile Findings

```markdown
## Security Review Report

**Scope:** [What was reviewed]
**Date:** [Timestamp]

### Findings

#### 🛑 Blocking Issues
[List of issues that block proceeding]

#### ⚠️ Warnings
[List of items requiring acknowledgment]

#### ✅ Passed Checks
[List of security checks that passed]

### SOC2 Compliance
- [ ] CC6.1 - Logical access: [Status]
- [ ] CC6.6 - External threats: [Status]
- [ ] CC7.1 - System changes: [Status]

### Decision
[ ] BLOCKED - Cannot proceed
[ ] WARN - Proceed with acknowledgment
[ ] ALLOW - Safe to proceed
```

### Step 7.2: Take Action

Based on findings:

1. **BLOCKED:** Stop execution, explain why, provide remediation
2. **WARN:** Present concerns, request explicit acknowledgment
3. **ALLOW:** Proceed with operation

---

## Quick Reference

### Blocking Triggers
| Pattern | Why Blocked |
|---------|-------------|
| Hardcoded secrets | Credential exposure |
| `rm -rf /` | System destruction |
| `curl \| bash` | Arbitrary code execution |
| SQL without params | Injection vulnerability |
| `eval(user_input)` | Code injection |

### Warning Triggers
| Pattern | Why Warning |
|---------|-------------|
| New dependency | Supply chain risk |
| Auth code change | Security critical |
| Permission change | Access control |
| External API call | Data exposure |

### SOC2 Controls
| Control | What We Check |
|---------|---------------|
| CC6.1 | Command allowlists |
| CC6.6 | Dependency scanning |
| CC7.1 | Pre-commit review |
| CC7.2 | Change detection |

---

## Completion

After security review:

1. If BLOCKED: Address issues before proceeding
2. If WARNED: Get explicit acknowledgment
3. If ALLOWED: Proceed with operation
4. Log review decision for audit trail
