## /SECURITY.md

```markdown
# Security Policy

## Supported Versions
We aim to keep `main` secure. Security fixes are backported case-by-case to the latest tagged minor release.

## Reporting a Vulnerability
- Email: security@<your-domain> (or open a private security advisory in GitHub)
- Include: affected versions/commit, reproduction steps, impact, and proposed severity.
- We will acknowledge within 2 business days and provide status updates until resolution.

## Expectations
- No secrets in the repository or context packs.
- Dependency updates are automated weekly; critical advisories may be fast-tracked.
- For breaking security fixes, we will publish an ADR and migration notes.

## Handling Sensitive Data
- Do not upload PII or production data to AI agents.
- Use redacted fixtures and synthetic datasets for tests and context.
