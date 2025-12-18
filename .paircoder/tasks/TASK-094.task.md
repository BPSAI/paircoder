---
id: TASK-094
title: Secret detection
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P0
complexity: 30
status: done
sprint: sprint-15
tags:
- security
- secrets
- scanning
depends_on:
- TASK-089
---

# Objective

Implement secret detection to scan for leaked credentials before commits.

# Implementation Plan

1. Create SecretScanner class:
   ```python
   class SecretScanner:
       # Patterns for common secrets
       PATTERNS = {
           'aws_key': r'AKIA[0-9A-Z]{16}',
           'aws_secret': r'[A-Za-z0-9/+=]{40}',
           'github_token': r'ghp_[A-Za-z0-9]{36}',
           'slack_token': r'xox[baprs]-[A-Za-z0-9-]+',
           'generic_secret': r'(?i)(password|secret|api_key|token)\s*[=:]\s*[\'"][^\'"]+[\'"]',
           'private_key': r'-----BEGIN (RSA |EC |DSA |)PRIVATE KEY-----',
       }

       def scan_file(self, path: Path) -> list[SecretMatch]:
           """Scan file for potential secrets."""

       def scan_diff(self, diff: str) -> list[SecretMatch]:
           """Scan git diff for secrets in new lines."""

       def scan_staged(self) -> list[SecretMatch]:
           """Scan all staged changes for secrets."""
   ```

2. Create pre-commit hook integration:
   ```bash
   # .git/hooks/pre-commit
   bpsai-pair scan-secrets --staged
   ```

3. Implement allowlist for false positives:
   ```yaml
   # .paircoder/security/secret-allowlist.yaml
   allowed_patterns:
     - "EXAMPLE_API_KEY"  # Documentation example
     - "test_token_*"     # Test fixtures
   allowed_files:
     - "tests/fixtures/*"
     - "docs/examples/*"
   ```

4. Add CLI commands:
   ```bash
   bpsai-pair scan-secrets             # Scan all files
   bpsai-pair scan-secrets --staged    # Scan staged changes
   bpsai-pair scan-secrets --diff HEAD # Scan since commit
   ```

# Acceptance Criteria

- [ ] Common secret patterns detected (AWS, GitHub, Slack, etc.)
- [ ] Scan runs on staged changes before commit
- [ ] Allowlist prevents false positives
- [ ] Clear output shows file, line, and secret type
- [ ] Exit code non-zero when secrets found
- [ ] Can integrate with CI/CD pipelines
- [ ] Private keys detected and blocked

# Files to Create/Modify

- `tools/cli/bpsai_pair/security/secrets.py` (new)
- `.paircoder/security/secret-allowlist.yaml` (new)
- `tests/test_security_secrets.py` (new)