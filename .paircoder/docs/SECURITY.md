# PairCoder Security

This document describes PairCoder's security features, controls, and compliance considerations.

## Overview

PairCoder includes security controls to enable safe autonomous execution:

1. **Security Agent** - Pre-execution gatekeeper that blocks dangerous operations
2. **Security Auditor** - Post-hoc reviewer that identifies vulnerabilities
3. **Command Allowlists** - Define safe vs unsafe commands (Sprint 15)
4. **Secret Detection** - Scan for leaked credentials (Sprint 15)

## Security Agents

### Security Agent (`.claude/agents/security.md`)

The security agent is a **gatekeeper** that reviews operations before execution:

| Action | Description |
|--------|-------------|
| **BLOCK** | Stop execution of dangerous operations |
| **WARN** | Flag risky operations for human review |
| **ALLOW** | Permit safe operations to proceed |

**Use cases:**
- Pre-commit review of code changes
- Pre-execution review of shell commands
- Pre-PR security scanning
- Dependency addition review

### Security Auditor (`.claude/agents/security-auditor.md`)

The security auditor is a **reviewer** that identifies issues in existing code:

- Vulnerability scanning
- Code audit reports
- SOC2 compliance checks
- Dependency vulnerability assessment

**Key difference:** The auditor reports findings; it doesn't block operations.

## What Gets Blocked

### Always Blocked

| Pattern | Reason |
|---------|--------|
| Hardcoded credentials | Credential exposure |
| `rm -rf /` or `rm -rf *` | System destruction |
| `curl \| bash`, `wget \| sh` | Arbitrary code execution |
| `sudo rm` | Dangerous privileged operation |
| SQL without parameters | Injection vulnerability |
| `eval(user_input)` | Code injection |

### Requires Review

| Pattern | Reason |
|---------|--------|
| `pip install`, `npm install` | Supply chain risk |
| `git push`, `git commit` | Change propagation |
| Auth/permission changes | Security critical |
| New external API calls | Data exposure risk |
| `docker` commands | Container escape risk |

### Always Allowed

| Pattern | Reason |
|---------|--------|
| `git status`, `git diff`, `git log` | Read-only operations |
| `pytest`, `bpsai-pair` | Safe tooling |
| `cat`, `ls`, `grep` | Read-only utilities |

## Secret Detection

PairCoder scans for common secret patterns:

| Type | Pattern |
|------|---------|
| AWS Keys | `AKIA[0-9A-Z]{16}` |
| AWS Secrets | 40-character base64 strings |
| GitHub Tokens | `ghp_[A-Za-z0-9]{36}` |
| Slack Tokens | `xox[baprs]-*` |
| Generic Secrets | `password\|secret\|api_key` assignments |
| Private Keys | `BEGIN.*PRIVATE KEY` |

### False Positive Handling

Add exceptions to `.paircoder/security/secret-allowlist.yaml`:

```yaml
allowed_patterns:
  - "EXAMPLE_API_KEY"  # Documentation example
  - "test_token_*"     # Test fixtures

allowed_files:
  - "tests/fixtures/*"
  - "docs/examples/*"
```

## SOC2 Compliance

PairCoder security controls map to SOC2 Trust Service Criteria:

| Control | Description | PairCoder Feature |
|---------|-------------|-------------------|
| CC6.1 | Logical access security | Command allowlists |
| CC6.6 | External threat protection | Block dangerous downloads |
| CC6.7 | Transmission integrity | Require HTTPS |
| CC7.1 | System change management | Pre-commit review |
| CC7.2 | Change detection | Scan all code changes |
| CC8.1 | Infrastructure integrity | Block destructive operations |

## Best Practices

### For Developers

1. **Never commit secrets** - Use environment variables
2. **Pin dependencies** - Specify exact versions
3. **Validate all input** - Never trust user data
4. **Use parameterized queries** - Prevent SQL injection

### For AI Agents

1. **Always check allowlist** before executing commands
2. **Scan staged changes** before committing
3. **Block and explain** rather than silently failing
4. **Log security decisions** for audit trail
5. **Request human review** when uncertain

## Integration

### CI/CD Pipeline

```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    bpsai-pair scan-secrets --staged
    bpsai-pair scan-deps --fail-on high
```

### Claude Code Integration

The security agent is automatically invoked:
- Before Bash tool execution (when enabled)
- Before git commit operations
- Before PR creation

## Reporting Security Issues

If you discover a security vulnerability in PairCoder:

1. **Do not** open a public issue
2. Email security concerns to the maintainers
3. Include steps to reproduce
4. Allow time for a fix before disclosure

## Sprint 15 Security Features

### Completed ✅

- [x] **Security Agent Definition** (TASK-089) — `.claude/agents/security.md` with SOC2 focus
- [x] **Command Allowlist System** (TASK-090) — `tools/cli/bpsai_pair/security/allowlist.py`
  - Safe vs unsafe command classification
  - Configurable via `.paircoder/security/allowlist.yaml`
  - Decisions: ALLOW, REVIEW, BLOCK
- [x] **Pre-execution Security Review** (TASK-091) — `tools/cli/bpsai_pair/security/review.py`
  - `SecurityReviewHook` for command review before execution
  - `CodeChangeReviewer` for vulnerability scanning
  - Secret detection patterns (API keys, AWS, GitHub tokens, etc.)
- [x] **Docker Sandbox Runner** (TASK-092) — `tools/cli/bpsai_pair/security/sandbox.py`
  - Execute commands in isolated containers
  - Network isolation, resource limits
  - File change tracking
- [x] **Git Checkpoint/Rollback** (TASK-093) — `tools/cli/bpsai_pair/security/checkpoint.py`
  - `GitCheckpoint` class for automatic checkpointing
  - Rollback support with stash handling
  - Retention policy enforcement

### Pending

- [ ] **Secret Detection CLI** (TASK-094) — Pre-commit secret scanning
- [ ] **Dependency Vulnerability Scan** (TASK-095) — CVE scanning for dependencies
