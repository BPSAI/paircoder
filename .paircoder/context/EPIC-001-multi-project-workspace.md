# Epic: Multi-Project Workspace Support

## Overview

Enable PairCoder to work across multiple related repositories while maintaining awareness of cross-project dependencies and contracts. The agent working in one repo will understand how changes impact sibling repos without needing to modify them directly.

**Epic ID:** EPIC-001
**Status:** Planned
**Estimated Sprints:** 2 (Sprint A + Sprint B)
**Total Estimated Complexity:** 350-400 points

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

# Sprint A: Workspace Core

**Goal:** Establish workspace configuration, project discovery, and contract loading.

**Sprint Complexity:** 175 points

## TASK-W01: Workspace Config Schema & Parser

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Define and implement the workspace configuration schema with YAML parsing and validation.

### Implementation Plan

1. Create Pydantic models for workspace config
2. Implement YAML parser with validation
3. Handle relative path resolution
4. Support environment variable substitution
5. Create config loader with caching

### Acceptance Criteria

- [ ] Pydantic models for WorkspaceConfig, ProjectConfig, ContractConfig
- [ ] YAML parsing with clear error messages for invalid configs
- [ ] Relative paths resolved from workspace root
- [ ] Environment variables supported: `${VAR}` syntax
- [ ] Config cached after first load
- [ ] Unit tests for parser edge cases

### Files to Create/Modify

- `bpsai_pair/workspace/config.py` (new)
- `bpsai_pair/workspace/models.py` (new)
- `tests/workspace/test_config.py` (new)

---

## TASK-W02: Project Discovery & Validation

**Complexity:** 20 | **Priority:** P0 | **Stack:** Backend

Implement project discovery from workspace config with path validation and health checks.

### Implementation Plan

1. Walk workspace config to find all projects
2. Validate each project path exists
3. Check for .paircoder directory in each project
4. Detect project type from markers (pyproject.toml, package.json, etc.)
5. Build project dependency graph

### Acceptance Criteria

- [ ] Discovers all projects defined in workspace config
- [ ] Validates paths exist and are directories
- [ ] Detects project type automatically if not specified
- [ ] Builds dependency graph from `consumes` declarations
- [ ] Reports missing or invalid projects clearly
- [ ] Handles circular dependency detection

### Files to Create/Modify

- `bpsai_pair/workspace/discovery.py` (new)
- `bpsai_pair/workspace/graph.py` (new)
- `tests/workspace/test_discovery.py` (new)

---

## TASK-W03: OpenAPI Contract Loader

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Load and parse OpenAPI specifications from sibling projects for contract awareness.

### Implementation Plan

1. Load openapi.json from configured paths
2. Parse into structured endpoint/schema representation
3. Extract endpoint signatures (path, method, request/response types)
4. Build searchable index of endpoints
5. Cache parsed contracts

### Acceptance Criteria

- [ ] Loads OpenAPI 3.0/3.1 JSON files
- [ ] Extracts all endpoint definitions with full signatures
- [ ] Parses request body and response schemas
- [ ] Builds endpoint index for fast lookup
- [ ] Handles $ref resolution within spec
- [ ] Graceful handling of malformed specs
- [ ] Unit tests with sample OpenAPI files

### Files to Create/Modify

- `bpsai_pair/workspace/contracts/openapi.py` (new)
- `bpsai_pair/workspace/contracts/models.py` (new)
- `tests/workspace/contracts/test_openapi.py` (new)
- `tests/fixtures/sample_openapi.json` (new)

---

## TASK-W04: Python Model Scanner

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Scan Python files for dataclass and Pydantic model definitions to build type contracts.

### Implementation Plan

1. Glob configured model file patterns
2. Parse Python AST to find class definitions
3. Identify dataclasses and Pydantic BaseModel subclasses
4. Extract field names, types, and defaults
5. Build model registry with relationships

### Acceptance Criteria

- [ ] Finds dataclass decorated classes
- [ ] Finds Pydantic BaseModel subclasses
- [ ] Extracts field definitions with types
- [ ] Handles Optional, List, Dict type hints
- [ ] Detects model inheritance relationships
- [ ] Handles import aliases (from pydantic import BaseModel as BM)
- [ ] Unit tests for various model patterns

### Files to Create/Modify

- `bpsai_pair/workspace/contracts/python_models.py` (new)
- `tests/workspace/contracts/test_python_models.py` (new)
- `tests/fixtures/sample_models.py` (new)

---

## TASK-W05: JSON Schema Loader

**Complexity:** 20 | **Priority:** P1 | **Stack:** Backend

Load JSON Schema files for message queue and other contract definitions.

### Implementation Plan

1. Load .json schema files from configured paths
2. Parse and validate as JSON Schema draft-07/2020-12
3. Extract type definitions and required fields
4. Build schema registry by name/path

### Acceptance Criteria

- [ ] Loads JSON Schema files (draft-07 and 2020-12)
- [ ] Validates schema syntax
- [ ] Extracts property definitions
- [ ] Handles $ref to other schema files
- [ ] Builds searchable schema index
- [ ] Unit tests with sample schemas

### Files to Create/Modify

- `bpsai_pair/workspace/contracts/json_schema.py` (new)
- `tests/workspace/contracts/test_json_schema.py` (new)
- `tests/fixtures/sample_schema.json` (new)

---

## TASK-W06: CLI - workspace init

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Interactive command to create a new workspace configuration.

### Implementation Plan

1. Detect sibling directories that look like projects
2. Prompt user to select which to include
3. Auto-detect project types
4. Ask about relationships (what consumes what)
5. Generate .paircoder-workspace.yaml

### Acceptance Criteria

- [ ] Detects potential projects in parent directory
- [ ] Interactive prompts with sensible defaults
- [ ] Auto-detects FastAPI, React, Python projects
- [ ] Asks about project relationships
- [ ] Generates valid workspace YAML
- [ ] Validates generated config
- [ ] Supports --non-interactive mode with flags

### CLI Signature

```bash
bpsai-pair workspace init [--parent PATH] [--non-interactive]
```

### Files to Create/Modify

- `bpsai_pair/workspace/cli.py` (new)
- Register in main CLI app
- `tests/workspace/test_cli.py` (new)

---

## TASK-W07: CLI - workspace status

**Complexity:** 20 | **Priority:** P0 | **Stack:** Backend

Display workspace overview with project status and contract health.

### Implementation Plan

1. Load and validate workspace config
2. Check each project's health (path exists, contracts loadable)
3. Display dependency graph
4. Show contract statistics
5. Highlight any issues

### Acceptance Criteria

- [ ] Shows all projects with status indicators
- [ ] Displays dependency relationships
- [ ] Shows contract counts (endpoints, models, schemas)
- [ ] Highlights missing or invalid contracts
- [ ] Shows last contract update timestamps
- [ ] Pretty table output with Rich

### CLI Signature

```bash
bpsai-pair workspace status [--json]
```

### Example Output

```
Workspace: BPS Platform
═══════════════════════

Projects:
  ✓ api-server (fastapi)
    └─ Contracts: 47 endpoints, 23 models
    └─ Consumers: frontend, workers
    
  ✓ client-app (frontend)
    └─ Consumes: api-server (openapi)
    └─ API calls: 31 endpoints used
    
  ✓ workers (worker)
    └─ Contracts: 8 message schemas
    └─ Consumes: api-server (models)

Health: All contracts valid ✓
```

### Files to Create/Modify

- `bpsai_pair/workspace/cli.py`
- `bpsai_pair/workspace/health.py` (new)

---

## TASK-W08: CLI - workspace export-contracts

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Auto-export contracts from FastAPI applications.

### Implementation Plan

1. Detect FastAPI app entry point
2. Import app and call app.openapi()
3. Write to configured contract path
4. Handle apps that need startup (database, etc.)
5. Support custom export commands per project

### Acceptance Criteria

- [ ] Auto-detects FastAPI app from common patterns
- [ ] Exports OpenAPI JSON without running server
- [ ] Creates contracts directory if missing
- [ ] Supports custom export command in config
- [ ] Handles import errors gracefully
- [ ] Shows diff if contract changed
- [ ] Updates contract timestamp

### CLI Signature

```bash
bpsai-pair workspace export-contracts [--project NAME] [--all]
```

### Files to Create/Modify

- `bpsai_pair/workspace/export.py` (new)
- `bpsai_pair/workspace/cli.py`

---

# Sprint B: Awareness & Validation

**Goal:** Implement change detection, impact analysis, and developer warnings.

**Sprint Complexity:** 175 points

## TASK-W09: Consumer Detection

**Complexity:** 35 | **Priority:** P0 | **Stack:** Backend

Analyze consumer projects to find what endpoints/models they use.

### Implementation Plan

1. For frontend: parse TypeScript/JavaScript for fetch/axios calls
2. Extract URL patterns and map to OpenAPI endpoints
3. For Python consumers: parse imports and usage
4. Build consumer registry: "endpoint X is used by [frontend, workers]"
5. Cache results with file hash invalidation

### Acceptance Criteria

- [ ] Parses TypeScript fetch/axios calls
- [ ] Extracts API endpoint URLs from frontend code
- [ ] Maps URLs to OpenAPI endpoint definitions
- [ ] Parses Python imports from sibling projects
- [ ] Builds reverse index: endpoint → consumers
- [ ] Caches results, invalidates on file changes
- [ ] Unit tests with sample consumer code

### Files to Create/Modify

- `bpsai_pair/workspace/consumers/typescript.py` (new)
- `bpsai_pair/workspace/consumers/python.py` (new)
- `bpsai_pair/workspace/consumers/registry.py` (new)
- `tests/workspace/consumers/` (new directory)

---

## TASK-W10: Change Impact Analyzer

**Complexity:** 40 | **Priority:** P0 | **Stack:** Backend

Analyze proposed changes and determine cross-project impact.

### Implementation Plan

1. Take file path + change type as input
2. Map changed file to contract (endpoint, model, schema)
3. Look up consumers of that contract
4. Classify impact: breaking, compatible, additive
5. Generate impact report

### Acceptance Criteria

- [ ] Maps file changes to affected contracts
- [ ] Identifies all consumer projects
- [ ] Classifies changes: breaking vs non-breaking
- [ ] Breaking: removed field, changed type, removed endpoint
- [ ] Compatible: added optional field, new endpoint
- [ ] Generates structured impact report
- [ ] Unit tests for various change scenarios

### Impact Classification Rules

| Change Type | Breaking? |
|-------------|-----------|
| Remove endpoint | Yes |
| Remove required field | Yes |
| Change field type | Yes |
| Rename endpoint | Yes |
| Add required field | Yes |
| Add optional field | No |
| Add new endpoint | No |
| Add new model | No |

### Files to Create/Modify

- `bpsai_pair/workspace/impact.py` (new)
- `bpsai_pair/workspace/changes.py` (new)
- `tests/workspace/test_impact.py` (new)

---

## TASK-W11: Pre-Change Warning System

**Complexity:** 30 | **Priority:** P0 | **Stack:** Backend

Warn developers before making breaking changes.

### Implementation Plan

1. Hook into file change detection
2. Run impact analysis on pending changes
3. Display warnings for breaking changes
4. Allow override with confirmation
5. Log warnings for audit trail

### Acceptance Criteria

- [ ] Triggers on file save/change in watched directories
- [ ] Runs impact analysis automatically
- [ ] Displays clear warning with affected consumers
- [ ] Shows specific files in consumer that will break
- [ ] Allows proceeding with acknowledgment
- [ ] Logs warnings to activity log
- [ ] Can be disabled per-session

### Warning Output Example

```
⚠️  BREAKING CHANGE DETECTED
═══════════════════════════

You are modifying: api-server/src/routes/users.py

This will affect:
  • DELETE /api/users/{id} - REMOVED
    └─ Used by: client-app/src/api/users.ts:47
    └─ Used by: client-app/src/components/UserAdmin.tsx:123

  • PATCH /api/users/{id} - Response changed
    └─ Field 'email' type changed: string → EmailStr
    └─ Used by: client-app/src/api/users.ts:52

Proceed anyway? [y/N]
```

### Files to Create/Modify

- `bpsai_pair/workspace/warnings.py` (new)
- `bpsai_pair/workspace/hooks.py` (new)
- Integration with existing hooks system

---

## TASK-W12: Skill - workspace-aware

**Complexity:** 20 | **Priority:** P0 | **Stack:** Documentation

Create skill that loads workspace context before Claude starts working.

### Implementation Plan

1. Define skill with workspace triggers
2. Load workspace config and contracts
3. Generate context summary for Claude
4. Include consumer information
5. Add rules about checking impact

### Acceptance Criteria

- [ ] Skill triggers when working in workspace project
- [ ] Loads relevant contracts from siblings
- [ ] Generates concise context summary
- [ ] Lists consumers of current project
- [ ] Reminds to check impact before changes
- [ ] Includes CLI commands for validation

### Skill Content

```markdown
---
name: workspace-aware
description: Multi-project workspace awareness. Use when working in a project 
  that is part of a larger workspace with sibling projects.
---

# Workspace Awareness

## Before Starting Work

Load workspace context:
\`\`\`bash
bpsai-pair workspace status
\`\`\`

## Current Workspace Context

{Dynamically loaded workspace summary}

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

### Files to Create/Modify

- `.claude/skills/workspace-aware/SKILL.md` (new)
- Dynamic context loader integration

---

## TASK-W13: CLI - workspace check-impact

**Complexity:** 25 | **Priority:** P0 | **Stack:** Backend

Manual command to check impact of current changes.

### Implementation Plan

1. Detect uncommitted changes in current project
2. Run impact analysis on changed files
3. Display detailed impact report
4. Exit with non-zero code if breaking changes

### Acceptance Criteria

- [ ] Detects git uncommitted changes
- [ ] Analyzes each changed file
- [ ] Shows impact per file
- [ ] Aggregates total impact summary
- [ ] Returns exit code 1 if breaking changes
- [ ] Supports --file flag for specific file
- [ ] JSON output option for CI

### CLI Signature

```bash
bpsai-pair workspace check-impact [--file PATH] [--json] [--fail-on-breaking]
```

### Files to Create/Modify

- `bpsai_pair/workspace/cli.py`

---

## TASK-W14: PR Impact Summary Generator

**Complexity:** 25 | **Priority:** P1 | **Stack:** Backend

Auto-generate cross-project impact summary for PRs.

### Implementation Plan

1. Compare current branch to target branch
2. Run impact analysis on all changes
3. Generate markdown summary
4. Include affected files in sibling projects
5. Suggest coordination steps

### Acceptance Criteria

- [ ] Compares branches to find all changes
- [ ] Generates markdown impact summary
- [ ] Lists all affected sibling projects
- [ ] Shows specific files that consume changed contracts
- [ ] Suggests test commands to run
- [ ] Can be copied to PR description
- [ ] Outputs to stdout or file

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

### Files to Create/Modify

- `bpsai_pair/workspace/pr.py` (new)
- `bpsai_pair/workspace/cli.py`

---

## TASK-W15: Type Drift Detector

**Complexity:** 30 | **Priority:** P1 | **Stack:** Backend

Detect when duplicated types across repos have drifted out of sync.

### Implementation Plan

1. Find same-named models across projects
2. Compare field definitions
3. Identify drift (different fields, types)
4. Report discrepancies
5. Suggest fixes

### Acceptance Criteria

- [ ] Finds models with same name across projects
- [ ] Compares field names and types
- [ ] Reports missing fields in either direction
- [ ] Reports type mismatches
- [ ] Suggests which version is authoritative
- [ ] Outputs report for review
- [ ] Tracks known acceptable differences

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

### Files to Create/Modify

- `bpsai_pair/workspace/drift.py` (new)
- `bpsai_pair/workspace/cli.py`

---

# Future Enhancements (Out of Scope)

These are potential future additions after the core Epic is complete:

## Shared Package Generation

- Extract common types to a shared package
- Auto-generate package from drift report
- Manage versioning across projects

## CI/CD Integration

- GitHub Action for impact checking
- Block PRs with unacknowledged breaking changes
- Auto-comment impact summary on PRs

## Real-time Sync

- Watch mode for contract changes
- Auto-export on model file save
- Webhook notifications to sibling projects

## Visual Dependency Graph

- Generate mermaid diagram of project relationships
- Interactive web view of contracts
- Impact visualization

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

# Dependencies

| Dependency | Purpose | Required? |
|------------|---------|-----------|
| PyYAML | Workspace config parsing | Yes |
| Pydantic | Config validation | Yes |
| OpenAPI-core | OpenAPI parsing | Yes |
| jsonschema | JSON Schema validation | Yes |
| GitPython | Branch comparison | Yes |
| Rich | CLI output | Yes (existing) |

---

# Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAPI export requires running app | Medium | Support custom export commands |
| TypeScript parsing complex | Medium | Start with common patterns, iterate |
| False positives annoy developers | High | Tune detection, allow suppressions |
| Large codebases slow analysis | Medium | Caching, incremental analysis |
| Circular dependencies | Low | Detect and warn, don't block |

---

# Timeline

| Sprint | Duration | Deliverable |
|--------|----------|-------------|
| Sprint A | 1 week | Workspace config, contract loading, basic CLI |
| Sprint B | 1 week | Impact analysis, warnings, PR integration |
| Buffer | 2-3 days | Testing, documentation, edge cases |

**Total: ~2.5 weeks**
