# Epic: Multi-Project Workspace Support

## Overview

Enable PairCoder to work across multiple related repositories while maintaining awareness of cross-project dependencies and contracts. The agent working in one repo will understand how changes impact sibling repos without needing to modify them directly.

**Epic ID:** EPIC-001
**Status:** Planned (Post-Sprint 21)
**Estimated Sprints:** 2 (Sprint 22 + Sprint 23)
**Total Estimated Complexity:** 350-400 points
**Task Naming:** `TASK-W{nn}` (e.g., TASK-W01, TASK-W15)

---

## Prerequisites from Sprints 18-21

| Sprint | Task | Dependency | Impact on Epic |
|--------|------|------------|----------------|
| Sprint 19 | T19.1 | Mandatory state.md hook | TASK-W11 builds on enhanced hooks |
| Sprint 20 | T20.1-T20.2 | Skill conventions | TASK-W12 follows gerund naming, third-person voice |
| Sprint 20 | T20.3 | Skill creation skill | Used to create workspace-aware skill |
| Sprint 21 | T21.4 | Skill quality scoring | Validate workspace-aware skill quality |

---

## Problem Statement

BPS projects often consist of multiple repositories:
- Frontend (React/Vue)
- Backend API (FastAPI/Flask)
- Workers (Celery/Lambda)
- Shared infrastructure

Currently, an agent working in one repo has no awareness of sibling repos. This leads to:
- Breaking API changes that affect frontend consumers
- Message schema changes that break workers
- Duplicated types drifting out of sync
- Manual coordination required before merge (Mike reviews for conflicts)

## Solution

Implement a **workspace-aware** system that:
1. Defines relationships between repos in a workspace config
2. Loads contracts (OpenAPI, schemas, types) from sibling repos
3. Warns before changes that would break consumers
4. Generates impact summaries for PRs

## Non-Goals (Out of Scope)

- Multi-repo writes (agent modifies multiple repos simultaneously)
- Atomic commits across repos
- Shared package generation (future Epic)
- Monorepo migration

## Architecture

```
~/projects/bps-platform/
├── .paircoder-workspace.yaml    # Workspace definition
├── api-server/                  
│   ├── .paircoder/              # Project state
│   └── contracts/
│       └── openapi.json         # Auto-exported from FastAPI
├── client-app/
│   ├── .paircoder/
│   └── src/api/                 # API consumer code
└── workers/
    ├── .paircoder/
    └── schemas/                 # Message schemas
```

## Workspace Config Schema

```yaml
# .paircoder-workspace.yaml
version: "1.0"
name: "BPS Platform"

projects:
  api:
    path: ./api-server
    type: fastapi
    description: "Main backend API"
    contracts:
      openapi: ./contracts/openapi.json
      models: ./src/models/**/*.py
    
  frontend:
    path: ./client-app
    type: frontend
    description: "React frontend application"
    consumes:
      - project: api
        contract: openapi
    sources:
      api_calls: ./src/api/**/*.ts
    
  workers:
    path: ./workers
    type: worker
    description: "Background job processors"
    contracts:
      messages: ./schemas/*.json
    consumes:
      - project: api
        contract: models

# Validation rules
rules:
  - id: api-stability
    description: "API endpoint changes require frontend impact check"
    trigger: 
      project: api
      files: ["*/routes/*", "*/endpoints/*"]
    check: consumers
    
  - id: message-compat
    description: "Message schema changes must be backward compatible"
    trigger:
      project: workers
      files: ["schemas/*.json"]
    check: schema-compat

# Shared Trello board
trello:
  board_id: "your-board-id"
  workspace_label: "BPS Platform"
```

---

# Sprint 22 (Sprint A): Workspace Core

**Goal:** Establish workspace configuration, project discovery, and contract loading.

**Sprint Complexity:** 175 points

## TASK-W01: Workspace Config Schema & Parser

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Define and implement the workspace configuration schema with YAML parsing and validation.

### Acceptance Criteria

- [ ] Pydantic models for WorkspaceConfig, ProjectConfig, ContractConfig
- [ ] YAML parsing with clear error messages for invalid configs
- [ ] Relative paths resolved from workspace root
- [ ] Environment variables supported: `${VAR}` syntax
- [ ] Config cached after first load
- [ ] Unit tests for parser edge cases

### Files to Create

- `bpsai_pair/workspace/config.py`
- `bpsai_pair/workspace/models.py`
- `tests/workspace/test_config.py`

---

## TASK-W02: Project Discovery & Validation

**Complexity:** 20 | **Priority:** P0 | **Stack:** Backend

Implement project discovery from workspace config with path validation and health checks.

### Acceptance Criteria

- [ ] Discovers all projects defined in workspace config
- [ ] Validates paths exist and are directories
- [ ] Detects project type automatically if not specified
- [ ] Builds dependency graph from `consumes` declarations
- [ ] Reports missing or invalid projects clearly
- [ ] Handles circular dependency detection

### Files to Create

- `bpsai_pair/workspace/discovery.py`
- `bpsai_pair/workspace/graph.py`
- `tests/workspace/test_discovery.py`

---

## TASK-W03: OpenAPI Contract Loader

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Load and parse OpenAPI specifications from sibling projects for contract awareness.

### Acceptance Criteria

- [ ] Loads OpenAPI 3.0/3.1 JSON files
- [ ] Extracts all endpoint definitions with full signatures
- [ ] Parses request body and response schemas
- [ ] Builds endpoint index for fast lookup
- [ ] Handles $ref resolution within spec
- [ ] Graceful handling of malformed specs
- [ ] Unit tests with sample OpenAPI files

### Files to Create

- `bpsai_pair/workspace/contracts/openapi.py`
- `bpsai_pair/workspace/contracts/models.py`
- `tests/workspace/contracts/test_openapi.py`
- `tests/fixtures/sample_openapi.json`

---

## TASK-W04: Python Model Scanner

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Scan Python files for dataclass and Pydantic model definitions to build type contracts.

### Acceptance Criteria

- [ ] Finds dataclass decorated classes
- [ ] Finds Pydantic BaseModel subclasses
- [ ] Extracts field definitions with types
- [ ] Handles Optional, List, Dict type hints
- [ ] Detects model inheritance relationships
- [ ] Handles import aliases
- [ ] Unit tests for various model patterns

### Files to Create

- `bpsai_pair/workspace/contracts/python_models.py`
- `tests/workspace/contracts/test_python_models.py`
- `tests/fixtures/sample_models.py`

---

## TASK-W05: JSON Schema Loader

**Complexity:** 20 | **Priority:** P1 | **Stack:** Backend

Load JSON Schema files for message queue and other contract definitions.

### Acceptance Criteria

- [ ] Loads JSON Schema files (draft-07 and 2020-12)
- [ ] Validates schema syntax
- [ ] Extracts property definitions
- [ ] Handles $ref to other schema files
- [ ] Builds searchable schema index
- [ ] Unit tests with sample schemas

### Files to Create

- `bpsai_pair/workspace/contracts/json_schema.py`
- `tests/workspace/contracts/test_json_schema.py`
- `tests/fixtures/sample_schema.json`

---

## TASK-W06: CLI - workspace init

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Interactive command to create a new workspace configuration.

### CLI Signature

```bash
bpsai-pair workspace init [--parent PATH] [--non-interactive]
```

### Acceptance Criteria

- [ ] Detects potential projects in parent directory
- [ ] Interactive prompts with sensible defaults
- [ ] Auto-detects FastAPI, React, Python projects
- [ ] Asks about project relationships
- [ ] Generates valid workspace YAML
- [ ] Validates generated config
- [ ] Supports --non-interactive mode with flags

### Files to Create

- `bpsai_pair/workspace/cli.py`
- `tests/workspace/test_cli.py`

---

## TASK-W07: CLI - workspace status

**Complexity:** 20 | **Priority:** P0 | **Stack:** Backend

Show current workspace status with project health and contract freshness.

### CLI Signature

```bash
bpsai-pair workspace status [--json]
```

### CLI Output

```bash
$ bpsai-pair workspace status

Workspace: BPS Platform
Projects: 3

┌─────────────┬────────────┬──────────────┬──────────────┐
│ Project     │ Type       │ Status       │ Contracts    │
├─────────────┼────────────┼──────────────┼──────────────┤
│ api         │ fastapi    │ ✅ healthy   │ openapi (2h) │
│ frontend    │ react      │ ✅ healthy   │ -            │
│ workers     │ worker     │ ⚠️ stale     │ schemas (7d) │
└─────────────┴────────────┴──────────────┴──────────────┘

Dependencies:
  frontend → api (openapi)
  workers → api (models)
```

### Acceptance Criteria

- [ ] Shows all projects with status
- [ ] Shows contract freshness
- [ ] Displays dependency relationships
- [ ] Warns about stale contracts
- [ ] JSON output option

---

# Sprint 23 (Sprint B): Impact Analysis

**Goal:** Implement impact analysis, warnings, and PR integration.

**Sprint Complexity:** 175 points

## TASK-W08: Contract Change Detector

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Detect changes to contracts (API endpoints, models, schemas) from git diff.

### Acceptance Criteria

- [ ] Detects added/modified/deleted contract files
- [ ] Identifies endpoint changes in OpenAPI
- [ ] Identifies field changes in models
- [ ] Classifies changes (breaking, non-breaking, additive)
- [ ] Works with staged and unstaged changes
- [ ] Unit tests for various change types

### Files to Create

- `bpsai_pair/workspace/changes.py`
- `tests/workspace/test_changes.py`

---

## TASK-W09: Consumer Impact Analyzer

**Complexity:** 35 | **Priority:** P0 | **Stack:** Backend

Analyze how contract changes impact consuming projects.

### Impact Assessment

| Change Type | Impact |
|-------------|--------|
| Endpoint deleted | 🔴 Breaking |
| Required field removed | 🔴 Breaking |
| Endpoint path changed | 🔴 Breaking |
| New required field | 🟡 Potentially Breaking |
| Optional field removed | 🟡 Warning |
| New optional field | 🟢 Safe |
| New endpoint | 🟢 Safe |

### Acceptance Criteria

- [ ] Finds consumers of changed contracts
- [ ] Searches consumer code for affected usages
- [ ] Classifies impact severity correctly
- [ ] Reports specific file:line locations in consumers
- [ ] Handles projects with no consumers gracefully
- [ ] Unit tests with mock projects

### Files to Create

- `bpsai_pair/workspace/impact.py`
- `tests/workspace/test_impact.py`

---

## TASK-W10: TypeScript API Consumer Scanner

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Scan TypeScript/JavaScript files to find API endpoint usages.

### Patterns to Detect

```typescript
// Direct fetch
fetch('/api/users')
fetch(`${API_URL}/users/${id}`)

// Axios
axios.get('/api/users')
api.post('/users', data)

// Generated client
apiClient.users.list()
```

### Acceptance Criteria

- [ ] Finds fetch() calls with string/template paths
- [ ] Finds axios calls
- [ ] Handles common patterns (api clients, constants)
- [ ] Extracts HTTP methods when possible
- [ ] Reports file:line for each usage
- [ ] Unit tests with sample TS files

### Files to Create

- `bpsai_pair/workspace/contracts/typescript.py`
- `tests/workspace/contracts/test_typescript.py`
- `tests/fixtures/sample_api_calls.ts`

---

## TASK-W11: Workspace Warning Hooks

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

**Depends on:** T19.1 (enhanced hooks system from Sprint 19)

Hook into file saves to warn about breaking changes before commit.

### Warning Output

```
⚠️ Workspace Impact Warning

Your changes to api/routes/users.py affect consumers:

Breaking Changes:
  DELETE /api/users/{id}
    ↳ client-app/src/api/users.ts:47

Run `bpsai-pair workspace check-impact` for full analysis.
```

### Acceptance Criteria

- [ ] Hook fires on contract file save
- [ ] Quick impact analysis (< 2 seconds)
- [ ] Shows breaking changes clearly
- [ ] Non-blocking (warning, not error)
- [ ] Integrates with existing hooks.py

### Files to Create

- `bpsai_pair/workspace/warnings.py`
- `bpsai_pair/workspace/hooks.py`

---

## TASK-W12: Skill - working-with-workspaces

**Complexity:** 20 | **Priority:** P0 | **Stack:** Documentation

**Depends on:** T20.1-T20.3 (Sprint 20 skill conventions)

Create skill that loads workspace context before Claude starts working.

### SKILL.md Content

```markdown
---
name: working-with-workspaces
description: Provides multi-project workspace awareness for developers working in 
  repositories that are part of a larger system. Loads sibling project contracts,
  warns about breaking changes, and generates impact summaries.
---

# Working with Workspaces

## Before Starting Work

Load workspace context:
\`\`\`bash
bpsai-pair workspace status
\`\`\`

## Before Changing APIs or Models

Check impact on sibling projects:
\`\`\`bash
bpsai-pair workspace check-impact <file>
\`\`\`

## Rules

- Never remove or rename API endpoints without checking consumers
- Never remove required fields from models
- Always add new fields as optional with defaults
- Run consumer tests after API changes
```

### Acceptance Criteria

- [ ] Skill triggers when working in workspace project
- [ ] Follows gerund naming convention
- [ ] Description in third-person voice
- [ ] Passes `bpsai-pair skill validate`
- [ ] Loads relevant contracts from siblings
- [ ] Lists consumers of current project
- [ ] Includes CLI commands for validation

### Files to Create

- `.claude/skills/working-with-workspaces/SKILL.md`

---

## TASK-W13: CLI - workspace check-impact

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Manual command to check impact of current changes.

### CLI Signature

```bash
bpsai-pair workspace check-impact [--file PATH] [--json] [--fail-on-breaking]
```

### Acceptance Criteria

- [ ] Detects git uncommitted changes
- [ ] Analyzes each changed file
- [ ] Shows impact per file
- [ ] Aggregates total impact summary
- [ ] Returns exit code 1 if breaking changes
- [ ] Supports --file flag for specific file
- [ ] JSON output option for CI

---

## TASK-W14: PR Impact Summary Generator

**Complexity:** 25 | **Priority:** P1 | **Stack:** Backend

Auto-generate cross-project impact summary for PRs.

### CLI Signature

```bash
bpsai-pair workspace pr-impact [--target BRANCH] [--output FILE]
```

### Example Output

```markdown
## Cross-Project Impact

### Affected Projects

| Project | Impact | Details |
|---------|--------|---------|
| client-app | ⚠️ Breaking | 3 API calls affected |
| workers | ✅ Compatible | No breaking changes |

### Breaking Changes

**DELETE /api/users/{id}** (removed)
- `client-app/src/api/users.ts:47`
- `client-app/src/components/UserAdmin.tsx:123`

### Recommended Actions

1. Coordinate release with frontend team
2. Run: `cd ../client-app && npm test`
3. Update frontend to remove deleted endpoint usage
```

### Acceptance Criteria

- [ ] Compares branches to find all changes
- [ ] Generates markdown impact summary
- [ ] Lists all affected sibling projects
- [ ] Shows specific files that consume changed contracts
- [ ] Suggests test commands to run
- [ ] Can be copied to PR description
- [ ] Outputs to stdout or file

---

## TASK-W15: Type Drift Detector

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Detect when duplicated types across repos have drifted out of sync.

### CLI Signature

```bash
bpsai-pair workspace check-drift [--ignore FILE]
```

### Example Output

```
Type Drift Report
═════════════════

User model has drifted:

  api-server/src/models/user.py:
    id: int
    email: str
    name: str
    created_at: datetime

  workers/src/models/user.py:
    id: int
    email: str
    name: str
    # MISSING: created_at

Recommendation: Add 'created_at' to workers model
```

### Acceptance Criteria

- [ ] Finds models with same name across projects
- [ ] Compares field names and types
- [ ] Reports missing fields in either direction
- [ ] Reports type mismatches
- [ ] Suggests which version is authoritative
- [ ] Outputs report for review
- [ ] Tracks known acceptable differences

---

# Success Metrics

| Metric | Target |
|--------|--------|
| Breaking changes caught before merge | 90%+ |
| False positive rate | <10% |
| Contract export time | <5 seconds |
| Impact analysis time | <10 seconds |
| Developer adoption | Used on all multi-repo PRs |

---

# Timeline

| Sprint | Duration | Deliverable |
|--------|----------|-------------|
| Sprint 22 (A) | 1 week | Workspace config, contract loading, basic CLI |
| Sprint 23 (B) | 1 week | Impact analysis, warnings, PR integration |
| Buffer | 2-3 days | Testing, documentation, edge cases |

**Total: ~2.5 weeks**
