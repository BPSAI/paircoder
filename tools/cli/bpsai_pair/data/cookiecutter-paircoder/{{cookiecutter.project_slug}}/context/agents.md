# Agents Guide — AI Pair Coding Playbook

**Purpose:** Make GPT-5 / Claude / CodeX effective partners for {{ cookiecutter.primary_goal }} while improving modularity, maintainability, and testability.

**Audience:** Engineers, Tech Leads, and AI Agents connected to this repo.

---

## 0) Ground Rules (READ FIRST)

* **Single Source of Truth:** This repository and the files in `/context` are canonical for all agent runs.
* **Safety First:** No destructive ops without backups and a PR. Agents must create `*.bak` or use Git branches.
* **Tests Before Changes:** Add/extend tests that fail *before* implementing a fix/refactor.
* **Small, Reviewable Diffs:** Keep changes scoped; open PRs early; link to the relevant roadmap task.
* **Update Context Every Run:** Always persist “Overall/Last/Next” (see §6) after actions.

---

## 1) Repo Layout & Context Discipline

> Keep the agent’s attention on code that matters. Avoid token waste and blind spots.

* **Project Tree (authoritative sketch):**

  ```
  .
  ├─ /src                # Application code
  ├─ /tests              # Unit/integration tests
  ├─ /services           # External adapters, API clients
  ├─ /infra              # IaC / deployment (optional)
  ├─ /docs               # Human-readable docs
  ├─ /context            # Agent context files (canonical)
  │   ├─ development.md
  │   ├─ agents.md
  │   ├─ project_tree.md
  │   └─ directory_notes/
  ├─ /assets/images      # Large/media (EXCLUDED from agent context)
  └─ ...
  ```

* **Explicit Exclusions:** `/assets/images`, `/dist`, `/build`, `/node_modules`, binaries, large JSON/CSV.
  Agents must **assume these exist** and avoid recommending moves/rewrites.

* **Directory Notes (optional but powerful):**
  Add `/context/directory_notes/<dir>.md` with:

  * Purpose, entry points, invariants, dependency direction.
  * “Do/Don’t” for this directory.
  * Local glossary (domain terms, DTOs).
  * Known pitfalls.

---

## 2) Branching & PR Conventions

* **Branch names:** `feature/<short-goal>` or `refactor/<module>` or `fix/<ticket-id>`
* **Create branch from:** `main`
* **PR template must include:**

  * Goal link to `<PHASE N TASK>`
  * Risk level (Low/Med/High)
  * Test plan (automated + manual)
  * Rollback plan
  * Context update diff (what changed in `/context` files)

---

## 3) Operating Modes

### A) Non-Scripted (Live Collaboration)

1. Create branch: `git checkout -b feature/<FEATURE>`
2. Connect agent (Claude or GPT-5) to repo URL.
3. Attach context: `/context/development.md`, `/context/agents.md`, relevant `/context/directory_notes/*`.
4. **Prompt:**

   ```
   PHASE 1 GOAL: <PHASE 1 GOAL>
   Constraints: preserve public APIs, add tests first, no destructive ops.
   Output: stepwise plan + minimal diffs per step.
   ```

### B) Scripted (One-Pass Implementation)

1. Create branch: `git checkout -b feature/<FEATURE>`
2. Attach **only** relevant context files.
3. **Prompt:**

   ```
   Create a comprehensive script/commit plan to accomplish <PHASE 1 GOAL> in one pass.
   Requirements:
   - Zero breakage; create backups where needed.
   - Generate/modify tests first to capture intended behavior.
   - Respect repo conventions, linting, and formatting.
   - Produce: (a) ordered commit plan, (b) code patches, (c) updated docs, (d) updated context (see §6).
   ```

---

## 4) Canonical Prompts

### 4.1 Deep Research (Kickoff)

```
You are a staff-level engineer embedded in this codebase.
Objective: Produce a comprehensive plan to improve modularity, maintainability, and achieve {{ cookiecutter.primary_goal }}.
Deliverables:
- Architecture review (current vs. target), explicit trade-offs.
- Refactoring map (by module), dependency inversion opportunities, interface boundaries.
- Test posture upgrade plan (unit/integration/contract), coverage deltas.
- Risks, complexity hotspots, and rollback strategies.
- 3-phase roadmap with measurable outcomes.
Constraints:
- Respect exclusions listed in agents.md.
- Assume assets exist where excluded.
- Prefer small, reversible changes; maximize seam creation for safe refactors.
```

### 4.2 Roadmap → Files

```
Convert the roadmap into:
- /context/development.md   (engineering tasks, test plans, risks)
- /context/agents.md        (this file; update Operating Modes, Prompts if needed)
Ensure clear Phase 1/2/3 breakdown with milestone checklists and acceptance criteria.
```

### 4.3 Implementation Guardrails (per task)

```
For TASK: <task-name>
- Propose minimal diff solution.
- Add/adjust tests first to lock behavior.
- Provide code patches and commands to run tests/lints.
- Call out risks + rollback.
- Update context loop (Overall/Last/Next).
```

---

## 5) Testing & Quality Gates

* **Unit tests:** focus on pure logic and interfaces.
* **Integration tests:** external boundaries (DB, queues, HTTP) via testcontainers/mocks.
* **Contract tests:** for service clients with provider/consumer pacts if applicable.
* **Coverage targets:** raise or maintain ≥ <TARGET>% lines/branches where practical.
* **CI gates:** lint, type-check, build, test, basic security scan (SAST/dep audit).

---

## 6) Context Loop (Mandatory)

Agents **must** persist this block at the end of every session in `/context/development.md` (and in any relevant directory note):

```
## Context Sync (AUTO-UPDATED)
Overall goal is: {{ cookiecutter.primary_goal }}
Last action was: <what changed and why> (commit SHA if available)
Next action will be: <smallest valuable step with owner>
Blockers/Risks: <if any>
```

---

## 7) Failure Modes & Rollback

* **If tests fail:** revert last commit or apply backup. Fix tests first, then code.
* **If unintended API change:** restore interface, add regression test.
* **If scope creep:** park in `Phase N Backlog` with rationale.

---

## 8) Example Exclusion Prompt

> *Drop into your agent prompt when large dirs are omitted.*

“Relevant image/media assets exist under `/assets/images` but are intentionally excluded from your context to conserve tokens. **Do not** propose changes that relocate, inline, or re-encode assets. Assume paths referenced in code are valid. Focus your analysis on `/src`, `/services`, and `/tests`. If a change seems to require asset inspection, propose an interface-level abstraction instead.”

---

## 9) Definitions

* **Seam:** a point in code where behavior can be changed without editing the code (e.g., via interface, DI, adapter).
* **Backwards compatibility window:** period where both old and new APIs coexist with deprecation notices.

---

## 10) Tools & Commands (fill per repo)

* **Install:** `<cmd>`
* **Format/Lint:** `<cmd>`
* **Test (unit):** `<cmd>`
* **Test (integration):** `<cmd>`
* **Type check:** `<cmd>`
* **Local CI bundle:** `<cmd>`

