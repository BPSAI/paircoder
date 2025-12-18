---
id: TASK-095
title: Dependency vulnerability scan
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P1
complexity: 25
status: done
sprint: sprint-15
tags:
- security
- dependencies
- cve
- vulnerabilities
---

# Objective

Implement dependency vulnerability scanning to check for known CVEs in project dependencies.

# Implementation Plan

1. Create DependencyScanner class:
   ```python
   class DependencyScanner:
       def scan_python(self, requirements: Path) -> list[Vulnerability]:
           """Scan Python dependencies using pip-audit or safety."""
           # Use pip-audit for scanning
           result = subprocess.run(
               ["pip-audit", "-r", str(requirements), "--format", "json"],
               capture_output=True
           )
           return self.parse_pip_audit(result.stdout)

       def scan_npm(self, package_json: Path) -> list[Vulnerability]:
           """Scan npm dependencies using npm audit."""
           result = subprocess.run(
               ["npm", "audit", "--json"],
               cwd=package_json.parent,
               capture_output=True
           )
           return self.parse_npm_audit(result.stdout)

       def scan_all(self) -> ScanReport:
           """Scan all detected dependency files."""
   ```

2. Create vulnerability report:
   ```python
   @dataclass
   class Vulnerability:
       package: str
       version: str
       cve_id: str
       severity: str  # low, medium, high, critical
       description: str
       fixed_version: Optional[str]

   @dataclass
   class ScanReport:
       vulnerabilities: list[Vulnerability]
       scanned_at: datetime
       packages_scanned: int

       def has_critical(self) -> bool:
           return any(v.severity == "critical" for v in self.vulnerabilities)
   ```

3. Add CLI commands:
   ```bash
   bpsai-pair scan-deps                    # Scan all dependencies
   bpsai-pair scan-deps --fail-on high     # Fail if high+ severity found
   bpsai-pair scan-deps --fix              # Auto-update to fixed versions
   ```

4. Integrate with CI and pre-commit:
   - Run on dependency file changes
   - Block commits with critical vulnerabilities
   - Generate report for PR comments

# Acceptance Criteria

- [ ] Python dependencies scanned (requirements.txt, pyproject.toml)
- [ ] npm dependencies scanned (package.json)
- [ ] CVE details shown with severity levels
- [ ] Fixed versions suggested when available
- [ ] Can fail CI on high/critical vulnerabilities
- [ ] Report suitable for PR comments
- [ ] Caching to avoid repeated scans

# Files to Create/Modify

- `tools/cli/bpsai_pair/security/dependencies.py` (new)
- `tests/test_security_dependencies.py` (new)