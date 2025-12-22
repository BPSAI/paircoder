# Contributing Guide

Thanks for contributing! This repo is optimized for AI pair coding and human review. Please follow these steps to keep changes safe and maintainable.

## Branching & Commits
- Branch from `main` using: `feature/<short-goal>`, `refactor/<module>`, or `fix/<ticket>`.
- Use Conventional Commits:
  - `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `build:`, `ci:`
  - Example: `refactor(auth): inject interface for token validation`

## Local Dev & CI
- Run the local CI bundle before pushing:
  ```bash
  bpsai-pair ci
  ```
- Add or update tests before implementing behavior changes.
- Keep diffs small and focused; open PRs early.

## Context Discipline (MANDATORY)

Keep `/context/` as the canonical source for agent runs.

Update the Context Sync block at the end of `/context/development.md` after each meaningful change:

```markdown
## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: <what changed and why> (commit SHA)
Next action will be: <smallest valuable step with owner>
Blockers/Risks: <if any>
```

Maintain `/context/project_tree.md` and add `/context/directory_notes/<dir>.md` for non-trivial areas (purpose, invariants, entry points, pitfalls).

## Pull Requests

Fill out all sections of the PR template (risk, test plan, rollback, context diff).

PRs that affect public APIs, persistence, or infra must include/refresh an ADR in `/docs/adr/`.

High-risk PRs require sign-off from owners listed in CODEOWNERS.

## Secrets & Data Safety

Never commit secrets. Provide `.env.example` and document variables.

Do not include binaries/media in agent packs. Maintain `.agentpackignore`.

## Design Records (ADR)

Use `/templates/adr.md` as a starting point and place completed ADRs under `/docs/adr/ADR-<ID>-<slug>.md`.

ADRs should capture context, decision, alternatives, and consequences.

#### Example: Refactor branch via CLI

```bash
bpsai-pair feature auth-cleanup --type refactor \
  --primary "Extract auth adapter seam" \
  --phase "Phase 1: Scaffolding"
```

> This repository itself is scaffolded and maintained using PairCoder. Follow the Context Loop (Overall/Last/Next/Blockers) and branch conventions when contributing.

## Testing
This repo includes both smoke tests (GitHub Actions) and pytest-based validation. Contributors should:
- Run `pytest` locally before opening a PR.
- Use `bpsai-pair context-sync` after each change to keep the Context Loop updated.

## Releases

### Who Can Release

Releases are managed by maintainers with write access to the repository.

### Release Cadence

- **Patch releases (X.Y.Z):** As needed for bug fixes
- **Minor releases (X.Y.0):** At sprint boundaries (typically weekly)
- **Major releases (X.0.0):** For breaking changes (rare, with migration guide)

### Pre-Release Checklist

Before creating a release:

1. **Run release prep:**
   ```bash
   bpsai-pair release prep
   ```

2. **Verify all checks pass:**
   - Version bumped in `tools/cli/pyproject.toml`
   - CHANGELOG.md updated with new version entry
   - Cookie cutter template synced (`bpsai-pair template check`)
   - All tests passing

3. **For version bump PRs**, use the release checklist in the PR template.

See [docs/RELEASING.md](docs/RELEASING.md) for the complete step-by-step release process.
