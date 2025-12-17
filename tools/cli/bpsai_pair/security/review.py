"""Pre-execution security review for PairCoder.

This module provides:
- ReviewResult: Result dataclass for security reviews
- SecurityReviewHook: Pre-execution command review
- CodeChangeReviewer: Code change security scanning
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .allowlist import AllowlistManager, CommandDecision


@dataclass
class ReviewResult:
    """Result of a security review.

    Attributes:
        allowed: Whether the operation is allowed to proceed
        reason: Explanation for blocking (if blocked)
        warnings: List of warnings that don't block execution
        suggested_fixes: List of suggested remediation steps
    """

    allowed: bool
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    suggested_fixes: list[str] = field(default_factory=list)

    @classmethod
    def allow(cls) -> "ReviewResult":
        """Create an allowed result with no issues."""
        return cls(allowed=True)

    @classmethod
    def block(
        cls,
        reason: str,
        suggested_fixes: Optional[list[str]] = None
    ) -> "ReviewResult":
        """Create a blocked result with reason.

        Args:
            reason: Why the operation is blocked
            suggested_fixes: Optional list of remediation steps
        """
        return cls(
            allowed=False,
            reason=reason,
            suggested_fixes=suggested_fixes or []
        )

    @classmethod
    def warn(cls, warnings: list[str]) -> "ReviewResult":
        """Create an allowed result with warnings.

        Args:
            warnings: List of warning messages
        """
        return cls(allowed=True, warnings=warnings)

    @property
    def is_blocked(self) -> bool:
        """Check if the result blocks execution."""
        return not self.allowed

    @property
    def has_warnings(self) -> bool:
        """Check if the result has any warnings."""
        return len(self.warnings) > 0

    def format_message(self) -> str:
        """Format the result as a human-readable message."""
        lines = []

        if self.is_blocked:
            lines.append(f"BLOCKED: {self.reason}")
            if self.suggested_fixes:
                lines.append("\nSuggested fixes:")
                for fix in self.suggested_fixes:
                    lines.append(f"  - {fix}")
        elif self.has_warnings:
            lines.append("ALLOWED with warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        else:
            lines.append("ALLOWED: Security checks passed.")

        return "\n".join(lines)

    def __repr__(self) -> str:
        if self.is_blocked:
            return f"ReviewResult(blocked: {self.reason})"
        elif self.has_warnings:
            return f"ReviewResult(allowed with {len(self.warnings)} warnings)"
        return "ReviewResult(allowed)"


@dataclass
class AuditLogEntry:
    """Entry in the security audit log."""
    timestamp: datetime
    command: str
    allowed: bool
    reason: str
    warnings: list[str]


class SecurityReviewHook:
    """Pre-execution security review hook.

    Reviews commands before execution using the allowlist
    and security patterns.

    Attributes:
        allowlist: AllowlistManager for command classification
        enable_logging: Whether to log reviews for audit
        audit_log: List of audit log entries
    """

    def __init__(
        self,
        allowlist: Optional[AllowlistManager] = None,
        enable_logging: bool = False
    ):
        """Initialize the security review hook.

        Args:
            allowlist: Custom AllowlistManager (uses default if None)
            enable_logging: Whether to enable audit logging
        """
        self.allowlist = allowlist or AllowlistManager()
        self.enable_logging = enable_logging
        self.audit_log: list[dict] = []

    def pre_execute(self, command: str) -> ReviewResult:
        """Review a command before execution.

        Args:
            command: The command string to review

        Returns:
            ReviewResult indicating if execution should proceed
        """
        # Check against allowlist
        check_result = self.allowlist.check_command_full(command)

        if check_result.decision == CommandDecision.BLOCK:
            result = ReviewResult.block(
                reason=check_result.reason or "Command is blocked",
                suggested_fixes=self._get_suggested_fixes(command)
            )
        elif check_result.decision == CommandDecision.REVIEW:
            # Commands requiring review get warnings
            result = ReviewResult.warn([
                f"Command requires review: {check_result.reason or 'Unknown command'}"
            ])
        else:
            result = ReviewResult.allow()

        # Log if enabled
        if self.enable_logging:
            self._log_review(command, result)

        return result

    def _get_suggested_fixes(self, command: str) -> list[str]:
        """Get suggested fixes for a blocked command."""
        fixes = []

        if "rm -rf" in command:
            fixes.append("Use 'rm -rf ./<directory>' for relative paths only")
            fixes.append("Verify the path before deletion")

        if "curl" in command and "|" in command:
            fixes.append("Download the script first: curl -o script.sh <url>")
            fixes.append("Review the script: cat script.sh")
            fixes.append("Then execute: bash script.sh")

        if "sudo" in command:
            fixes.append("Avoid sudo for autonomous operations")
            fixes.append("Use proper file permissions instead")

        return fixes

    def _log_review(self, command: str, result: ReviewResult) -> None:
        """Log a review result for audit."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "allowed": result.allowed,
            "reason": result.reason,
            "warnings": result.warnings
        })


# Secret detection patterns
SECRET_PATTERNS = [
    # API Keys
    (r'api[_-]?key\s*[=:]\s*["\']([^"\']{10,})["\']', "Hardcoded API key detected"),
    (r'apikey\s*[=:]\s*["\']([^"\']{10,})["\']', "Hardcoded API key detected"),

    # Passwords
    (r'password\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded password detected"),
    (r'passwd\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded password detected"),
    (r'db_password\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded database password detected"),

    # AWS Credentials
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID detected"),
    (r'aws_secret_access_key\s*[=:]\s*["\']([^"\']{20,})["\']', "AWS Secret Access Key detected"),
    (r'AWS_SECRET_ACCESS_KEY\s*[=:]\s*["\']([^"\']{20,})["\']', "AWS Secret Access Key detected"),

    # Private Keys
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key detected"),
    (r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----', "SSH private key detected"),

    # Tokens
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token detected"),
    (r'github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}', "GitHub PAT (fine-grained) detected"),
    (r'gho_[A-Za-z0-9]{36}', "GitHub OAuth Token detected"),

    # JWT Tokens
    (r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "JWT token detected"),

    # Database Connection Strings
    (r'(postgresql|mysql|mongodb)://[^:]+:[^@]+@', "Database connection string with credentials detected"),

    # Slack Webhooks
    (r'https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+', "Slack webhook URL detected"),

    # Generic Secrets
    (r'secret\s*[=:]\s*["\']([^"\']{8,})["\']', "Hardcoded secret detected"),
    (r'token\s*[=:]\s*["\']([^"\']{20,})["\']', "Hardcoded token detected"),
]

# Injection vulnerability patterns
INJECTION_PATTERNS = [
    # SQL Injection
    (r'f["\']SELECT\s+.*\{', "Potential SQL injection: f-string in SELECT query"),
    (r'f["\']INSERT\s+.*\{', "Potential SQL injection: f-string in INSERT query"),
    (r'f["\']UPDATE\s+.*\{', "Potential SQL injection: f-string in UPDATE query"),
    (r'f["\']DELETE\s+.*\{', "Potential SQL injection: f-string in DELETE query"),
    (r'\.format\(.*\).*execute', "Potential SQL injection: string format in query"),

    # Command Injection
    (r'os\.system\s*\(\s*f["\']', "Command injection: os.system with f-string"),
    (r'os\.popen\s*\(\s*f["\']', "Command injection: os.popen with f-string"),
    (r'subprocess\..*shell\s*=\s*True', "Potential command injection: shell=True"),
    (r'subprocess\.call\s*\(\s*[^,\[\]]+,\s*shell\s*=\s*True', "Command injection: subprocess.call with shell=True"),

    # Path Traversal
    (r'\.\./', "Potential path traversal: '../' detected"),
]

# Patterns to ignore (false positives)
IGNORE_PATTERNS = [
    r'os\.environ\.get\s*\(["\']',  # Reading from env vars
    r'os\.getenv\s*\(["\']',  # Reading from env vars
    r'environ\[["\']',  # Accessing environ dict
    r'#.*password',  # Comments about passwords
    r'#.*secret',  # Comments about secrets
]


class CodeChangeReviewer:
    """Reviews code changes for security vulnerabilities.

    Scans code for:
    - Hardcoded secrets (API keys, passwords, tokens)
    - Injection vulnerabilities (SQL, command, path traversal)
    - Other security issues
    """

    def __init__(self):
        """Initialize the code change reviewer."""
        self.secret_patterns = [
            (re.compile(pattern, re.IGNORECASE), message)
            for pattern, message in SECRET_PATTERNS
        ]
        self.injection_patterns = [
            (re.compile(pattern, re.IGNORECASE), message)
            for pattern, message in INJECTION_PATTERNS
        ]
        self.ignore_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in IGNORE_PATTERNS
        ]

    def _should_ignore_line(self, line: str) -> bool:
        """Check if a line should be ignored (false positive)."""
        for pattern in self.ignore_patterns:
            if pattern.search(line):
                return True
        return False

    def scan_code(self, code: str) -> list[str]:
        """Scan code for security issues.

        Args:
            code: The code to scan

        Returns:
            List of security findings
        """
        findings = []

        # Split into lines for line-by-line analysis
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip lines that match ignore patterns
            if self._should_ignore_line(line):
                continue

            # Check for secrets
            for pattern, message in self.secret_patterns:
                if pattern.search(line):
                    findings.append(f"Line {line_num}: {message}")
                    break  # One finding per line for secrets

            # Check for injection vulnerabilities
            for pattern, message in self.injection_patterns:
                if pattern.search(line):
                    findings.append(f"Line {line_num}: {message}")

        # Deduplicate findings
        return list(dict.fromkeys(findings))

    def review_diff(self, diff: str) -> ReviewResult:
        """Review a git diff for security issues.

        Args:
            diff: The git diff output

        Returns:
            ReviewResult with findings
        """
        # Extract added lines (lines starting with +)
        added_lines = []
        for line in diff.split('\n'):
            # Strip leading whitespace to handle indented diffs
            stripped = line.lstrip()
            if stripped.startswith('+') and not stripped.startswith('+++'):
                added_lines.append(stripped[1:])  # Remove the + prefix

        code = '\n'.join(added_lines)
        findings = self.scan_code(code)

        if findings:
            # Check severity - secrets are blocking, injections are warnings
            secrets = [f for f in findings if any(
                word in f.lower() for word in ['key', 'password', 'secret', 'token', 'credential']
            )]

            if secrets:
                return ReviewResult.block(
                    reason="Security issues found in diff",
                    suggested_fixes=[
                        "Remove hardcoded secrets",
                        "Use environment variables instead",
                        "Add sensitive files to .gitignore"
                    ] + findings
                )
            else:
                return ReviewResult.warn(findings)

        return ReviewResult.allow()

    def review_code(self, code: str, filename: str = "") -> ReviewResult:
        """Review code content for security issues.

        Args:
            code: The code content to review
            filename: Optional filename for context

        Returns:
            ReviewResult with findings
        """
        findings = self.scan_code(code)

        if findings:
            # Secrets should block, other issues warn
            secrets = [f for f in findings if any(
                word in f.lower() for word in ['key', 'password', 'secret', 'token', 'credential']
            )]

            if secrets:
                reason = f"Security issues found"
                if filename:
                    reason = f"Security issues found in {filename}"
                return ReviewResult.block(
                    reason=reason,
                    suggested_fixes=findings + [
                        "Use environment variables for secrets",
                        "Use a secrets manager"
                    ]
                )
            else:
                return ReviewResult.warn(findings)

        return ReviewResult.allow()
