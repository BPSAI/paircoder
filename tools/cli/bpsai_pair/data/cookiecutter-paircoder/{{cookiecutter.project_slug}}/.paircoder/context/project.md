# Project Context

## Overview

**Project:** {{ cookiecutter.project_name }}
**Primary Goal:** {{ cookiecutter.primary_goal }}
**Test Coverage Target:** {{ cookiecutter.coverage_target }}

## Tech Stack

<!-- Update with your actual tech stack -->
- Language: TBD
- Framework: TBD
- Database: TBD
- Testing: TBD

## Architecture

<!-- Describe your architecture here -->

### Key Components

1. **Component 1** - Description
2. **Component 2** - Description
3. **Component 3** - Description

### Data Flow

```
[Input] -> [Processing] -> [Output]
```

## Constraints

### Must Have
- All code must have tests (minimum {{ cookiecutter.coverage_target }} coverage)
- Follow existing patterns in the codebase
- Documentation for public APIs

### Must Not
- Break backward compatibility without major version bump
- Introduce new dependencies without review
- Commit secrets or credentials

## Key Files

| Path | Purpose |
|------|---------|
| `src/` | Source code |
| `tests/` | Test files |
| `.paircoder/` | PairCoder configuration |

## Team

| Role | Handle |
|------|--------|
| Owner | @{{ cookiecutter.owner_gh_handle }} |
| Architect | @{{ cookiecutter.architect_gh_handle }} |
| Build | @{{ cookiecutter.build_gh_handle }} |
| QA | @{{ cookiecutter.qa_gh_handle }} |
| SRE | @{{ cookiecutter.sre_gh_handle }} |

## External Resources

<!-- Add links to relevant documentation, APIs, etc. -->
- Documentation: TBD
- Issue Tracker: TBD
- CI/CD: TBD
