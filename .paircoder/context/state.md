# Current State

> Last updated: 2025-12-23

## Active Plan

**Plan:** plan-2025-12-sprint-25.6-emergent-skills
**Sprint:** 25.6 - Emergent Skill Discovery + Flows Deprecation
**Status:** In Progress
**Goal:** AI-driven skill creation, gap detection, subagent discovery, and flows→skills migration planning
**Version Target:** v2.9.2

## Current Sprint Tasks (Sprint 25.6)

| ID     | Title | Status | Priority | Complexity | Effort |
|--------|-------|--------|----------|------------|--------|
| T25.17 | /update-skills Slash Command | done | P1 | 35 | M |
| T25.18 | Skill Gap Detection | done | P1 | 50 | L |
| T25.19 | Auto-Skill Creation | done | P1 | 55 | L |
| T25.20 | Skill Quality Scoring | pending | P2 | 45 | M |
| T25.21 | Skill Marketplace Foundation | pending | P2 | 45 | M |
| T25.22 | Flows → Skills Migration RFC | pending | P1 | 35 | M |
| T25.23 | Subagent Gap Detection | pending | P1 | 45 | M |
| T25.24 | Unified Gap Classifier | pending | P1 | 40 | M |
| T25.25 | Flow Commands Deprecation Warnings | pending | P2 | 25 | S |
| T25.26 | Codex/ChatGPT Skill Export Formats | pending | P2 | 30 | M |

**Progress:** 3/10 tasks (140/405 complexity points)

## Task Dependencies & Implementation Sequence

```
COMPLETED:
  T25.17 (/update-skills) ✓
  T25.18 (Skill Gap Detection) ✓
  T25.19 (Auto-Skill Creation) ✓

RECOMMENDED SEQUENCE:
  1. T25.22 (RFC) ─────────────► Documents migration plan, no code changes
        │
        └──► T25.25 (Deprecation) ─► Add warnings after RFC approved
  
  2. T25.23 (Subagent Gaps) ───► Extends T25.18 infrastructure
        │
        └──► T25.24 (Classifier) ─► Unifies skill + subagent detection
  
  3. T25.26 (Codex/ChatGPT) ───► Independent, extends T25.16
  
  4. T25.20, T25.21 ───────────► Can parallelize after core work done
```

### Priority Breakdown

**P1 (High) - Core Architecture:**
- T25.22: RFC first - documents breaking changes and timeline
- T25.23: Subagent gap detection - extends existing gap system  
- T25.24: Unified classifier - determines skill vs subagent

**P2 (Medium) - Enhancements:**
- T25.20: Skill quality scoring
- T25.21: Skill marketplace foundation
- T25.25: Deprecation warnings (low risk, after RFC)
- T25.26: Codex/ChatGPT export (independent work)

## Context: Industry Skills Adoption

OpenAI has adopted Agent Skills in Codex CLI and ChatGPT. The `agentskills.io` open standard is now supported by: Claude Code, OpenAI Codex, Cursor, VS Code, GitHub, Amp, Goose, and Letta.

**Key distinction (T25.23/T25.24):**
- **Skills**: Portable instructions, model-invoked, cross-platform
- **Subagents**: Context-isolated personas, Claude Code specific, resumable

## Previous Sprint Summary (Sprint 25.5)

**Sprint 25.5 COMPLETE:** Cross-Platform Skills
- T25.12: Skill naming conventions (gerund form)
- T25.13: Third-person voice descriptions
- T25.14: Creating-skills meta-skill
- T25.15: Skill install command
- T25.16: Skill export command (Cursor, Continue, Windsurf)

## Previous Sprint Summary (Sprint 25)

**Sprint 25 COMPLETE:** EPIC-003 + Token Budget System
- EPIC-003 CLI Architecture Refactor complete (Phases 1-5)
- Token Budget System with tiktoken integration
- 112 CLI commands, 1774 tests
- v2.8.0 ready for release

## Sprint History

Sprints 1-17.5 archived. See `.paircoder/history/sprint_archive.md`.

| Sprint | Theme | Version | Status |
|--------|-------|---------|--------|
| 1-12 | Foundation → Webhooks | v2.0-2.4 | Archived |
| 13 | Full Autonomy | v2.5 | Complete |
| 14 | Trello Deep Integration | v2.5.1 | Complete |
| 15 | Security & Sandboxing | v2.5.2 | Complete |
| 16 | Real Sub-agents | v2.5.3 | Complete |
| 17 | Time, Tokens & Metrics | v2.5.4 | Complete |
| 17.5 | Backlog Remediation | v2.6.0 | Complete |
| 17.6 | Trello Field Validation Hotfix | v2.6.1 | Complete |
| 18 | Release Engineering | v2.6.1 | Complete |
| 19 | Methodology & Session Management | v2.7.0 | Complete |
| 22 | CLI Refactor Phase 1 | v2.7.0 | Complete |
| 23 | CLI Refactor Phase 2 | v2.7.0 | Complete |
| 24 | CLI Refactor Phase 3 | v2.7.0 | Complete |
| 25 | EPIC-003 Complete + Token Budget | v2.8.0 | Complete |
| 25.5 | Cross-Platform Skills | v2.9 | Complete |
| 25.6 | Emergent Skill Discovery + Flows Deprecation | v2.9.2 | In Progress |
| 26 | UX Overhaul (EPIC-004) | v2.10.0 | Planned |

## What's Next

**Sprint 25.6: Emergent Skill Discovery** (10 tasks, 405 pts) - IN PROGRESS

Phase 1 - Core (Complete):
- ✓ T25.17: /update-skills command
- ✓ T25.18: Skill gap detection
- ✓ T25.19: Auto-skill creation

Phase 2 - Migration Planning (Next):
- T25.22: Flows → Skills Migration RFC **(START HERE)**
- T25.23: Subagent gap detection
- T25.24: Unified gap classifier (skill vs subagent)

Phase 3 - Implementation:
- T25.25: Flow commands deprecation warnings
- T25.26: Codex/ChatGPT skill export formats

Phase 4 - Quality & Distribution:
- T25.20: Skill quality scoring
- T25.21: Skill marketplace foundation

**Sprint 26: UX Overhaul (EPIC-004)** (10 tasks, 230 pts)
Make PairCoder usable by non-technical "vibe-coders". Tasks: T26.1-T26.10 - Interactive welcome wizard, Trello setup wizard with pre-checks, post-setup guidance, Claude prompts, /get-started slash command, board creation from template, contextual doc links, documentation updates, user retest session.

## Backlog (Deprioritized)

See `.paircoder/tasks/backlog/`:
- HF-001: Context sync hotfix
- RFE-001: Remote API Orchestration

## Future: EPIC-005 (Flows Removal)

After Sprint 25.6 deprecation warnings, full removal planned for v2.11.0:
- Flow commands removed entirely
- `flows_dir` config option removed
- `capabilities.yaml` flow_triggers removed
- Migration utility for legacy projects

## Session Log

_Add entries here as work is completed._

### 2025-12-23 - Sprint 25.6 Extended with Skills/Subagent Strategy

- **Sprint 25.6 Scope Extended**
  - Added 5 new tasks (T25.22-T25.26) for flows deprecation and subagent discovery
  - Total complexity increased from 230 to 405 points
  - Sprint now addresses industry convergence on Agent Skills standard
  - Research: OpenAI adopted skills in Codex CLI and ChatGPT
  - Research: agentskills.io now supported by 10+ AI coding tools
  
- **New Tasks Added:**
  - T25.22: Flows → Skills Migration RFC (P1, 35 pts)
  - T25.23: Subagent Gap Detection (P1, 45 pts)
  - T25.24: Unified Gap Classifier (P1, 40 pts)
  - T25.25: Flow Commands Deprecation Warnings (P2, 25 pts)
  - T25.26: Codex/ChatGPT Skill Export Formats (P2, 30 pts)

- **Key Architecture Decision:**
  - Skills = portable, cross-platform, model-invoked workflows
  - Subagents = context-isolated personas, Claude Code specific
  - Gap detector will classify patterns into appropriate category

### 2025-12-23 - T25.19 Complete (Auto-Skill Creation)

- **T25.19: Auto-Skill Creation** ✓
  - Created `bpsai_pair/skills/generator.py` module with:
    - `GeneratedSkill` dataclass for skill drafts
    - `SkillGenerator` class for generating from gaps
    - `save_generated_skill()` for saving to disk
    - `generate_skill_from_gap_id()` high-level function
  - Added `bpsai-pair skill generate` CLI command:
    - Lists available gaps if no ID provided
    - `--preview` flag to preview without saving
    - `--auto-approve` flag to save without confirmation
    - `--force` flag to overwrite existing skill
  - Generated skills include:
    - Valid YAML frontmatter (name, description)
    - Third-person voice descriptions
    - Observed commands as workflow steps
    - Placeholders for customization
    - Auto-generation notice
  - All generated skills pass validation
  - 19 new tests, all 123 skill-related tests pass

### 2025-12-23 - T25.18 Complete (Skill Gap Detection)

- **T25.18: Skill Gap Detection** ✓
  - Created `bpsai_pair/skills/gap_detector.py` module with:
    - `SkillGap` dataclass with serialization support
    - `SkillGapDetector` class for session analysis
    - `GapPersistence` class for saving/loading gaps to history
    - `detect_gaps_from_history()` high-level function
    - `format_gap_notification()` for user notifications
  - Added `bpsai-pair skill gaps` CLI command:
    - Lists detected gaps from history
    - `--analyze` flag to run fresh detection
    - `--json` flag for JSON output
    - `--clear` flag to clear gap history
  - Gap detection features:
    - Detects repeated command sequences (3+ occurrences)
    - Calculates confidence scores based on frequency
    - Reduces confidence for overlaps with existing skills
    - Generates gerund-form skill names
    - Estimates time savings
  - Persists gaps to `.paircoder/history/skill-gaps.jsonl`
  - 22 new tests, all 104 skill-related tests pass

### 2025-12-23 - T25.17 Complete (/update-skills Slash Command)

- **T25.17: /update-skills Slash Command** ✓
  - Created `.claude/commands/update-skills.md` slash command
  - Created `bpsai_pair/skills/suggestion.py` module with:
    - `HistoryParser` - parses session history files
    - `PatternDetector` - detects repeated command sequences
    - `SkillSuggester` - generates skill suggestions with confidence scores
    - `SkillDraftCreator` - creates skill drafts from suggestions
    - `suggest_skills()` - high-level function for pattern analysis
  - Added `bpsai-pair skill suggest` CLI command:
    - Shows suggestions with confidence scores (0-100%)
    - Detects overlap with existing skills
    - `--create N` flag to create draft for suggestion N
    - `--json` flag for JSON output
    - `--min` flag to set minimum pattern occurrences
  - Integrates with existing skill validator for draft validation
  - Added slash command to cookiecutter template
  - 19 new tests, all passing
  - All 82 skill-related tests pass

### 2025-12-23 - T25.16 Complete (Cross-Platform Skill Structure) - SPRINT 25.5 COMPLETE!

- **T25.16: Cross-Platform Skill Structure** ✓
  - Created `bpsai_pair/skills/exporter.py` module with:
    - `ExportFormat` enum (CURSOR, CONTINUE, WINDSURF)
    - `export_skill()` - export single skill to target format
    - `export_all_skills()` - export all skills
    - `check_portability()` - detect platform-specific features
  - Added `bpsai-pair skill export` CLI command:
    - `skill export <n> --format cursor` - Cursor AI (.cursor/rules/)
    - `skill export <n> --format continue` - Continue.dev (.continue/context/)
    - `skill export <n> --format windsurf` - Windsurf (.windsurfrules)
    - `--all` flag to export all skills
    - `--dry-run` flag to preview without creating
  - Export formats:
    - Cursor: Individual .md files with metadata comments
    - Continue: Individual .md files with context headers
    - Windsurf: Appends to single file with section markers
  - Portability warnings for:
    - Skills with scripts/ directory
    - Skills referencing bpsai-pair commands
    - Skills referencing Claude Code features
  - Created `docs/CROSS_PLATFORM_SKILLS.md` documentation
  - 22 new tests, all 63 skill-related tests pass

**Sprint 25.5: Cross-Platform Skills - COMPLETE!**
- T25.12: Skill naming conventions (gerund form)
- T25.13: Third-person voice descriptions
- T25.14: Creating-skills meta-skill
- T25.15: Skill install command
- T25.16: Skill export command

### 2025-12-23 - T25.15 Complete (Skill Installer Command)

- **T25.15: Skill Installer Command** ✓
  - Created `bpsai_pair/skills/installer.py` module with:
    - `parse_source()` - detect URL vs local path
    - `parse_github_url()` - extract owner/repo/branch/path from GitHub URLs
    - `install_from_path()` - install from local directory
    - `install_from_url()` - download and install from GitHub
    - `check_conflicts()` - detect naming conflicts
    - `get_target_dir()` - get project or personal target
  - Added `bpsai-pair skill install` CLI command:
    - `skill install <path>` - install from local path
    - `skill install <url>` - install from GitHub URL
    - `--name` flag to rename skill during install
    - `--force` flag to overwrite existing skill
    - `--project` / `--personal` flags for target selection
  - Validates skills before installation using existing validator
  - GitHub URL parsing handles tree/blob formats and branches with slashes
  - 25 new tests covering all installation scenarios
  - All 41 skill-related tests pass

### 2025-12-23 - T25.14 Complete (Create skill-creation Skill)

- **T25.14: Create skill-creation Skill** ✓
  - Created `.claude/skills/creating-skills/SKILL.md` (153 lines)
  - Follows Agent Skills specification exactly
  - Includes:
    - Gerund naming convention guidance
    - Third-person voice examples
    - SKILL.md template with frontmatter
    - Validation checklist
    - Common mistakes to avoid
  - Skill triggers on: "create a skill", "new skill", "write a skill"
  - Added to cookiecutter template for new projects
  - Validated with `bpsai-pair skill validate`

### Earlier Session Logs

_See `.paircoder/history/session_archive.md` for entries prior to 2025-12-23._
