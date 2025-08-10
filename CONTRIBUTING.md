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
  scripts/ci_local.sh
  
Add or update tests before implementing behavior changes.

Keep diffs small and focused; open PRs early.

Context Discipline (MANDATORY)

Keep /context/ as the canonical source for agent runs.

Update the Context Sync block at the end of /context/development.md after each meaningful change:

## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: <what changed and why> (commit SHA)
Next action will be: <smallest valuable step with owner>
Blockers/Risks: <if any>

Maintain /context/project_tree.md and add /context/directory_notes/<dir>.md for non-trivial areas (purpose, invariants, entry points, pitfalls).

Pull Requests

Fill out all sections of the PR template (risk, test plan, rollback, context diff).

PRs that affect public APIs, persistence, or infra must include/refresh an ADR in /docs/adr/.

High-risk PRs require sign-off from owners listed in CODEOWNERS.

Secrets & Data Safety

Never commit secrets. Provide .env.example and document variables.

Do not include binaries/media in agent packs. Maintain .agentpackignore.

Design Records (ADR)

Use /templates/adr.md as a starting point and place completed ADRs under /docs/adr/ADR-<ID>-<slug>.md.

ADRs should capture context, decision, alternatives, and consequences.
