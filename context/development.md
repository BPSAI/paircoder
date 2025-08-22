# Development Roadmap — PairCoder

**Primary Goal:** Develop and maintain the PairCoder AI pair programming framework while serving as its own reference implementation  
**Owner:** BPS AI Software Team  
**Last Updated:** 2025-01-24

---

## KPIs & Non-Functional Targets

- **Package Quality:** Zero critical bugs, comprehensive test coverage
- **Documentation:** Complete user docs, clear API references
- **Dogfooding:** This repo fully implements PairCoder practices
- **Cross-platform:** Windows, macOS, Linux compatibility
- **Test Coverage:** ≥ 80% for core CLI functionality

---

## Phase 1 — Repository Alignment & Documentation (Current)

**Objectives**
- Align repository structure to properly demonstrate PairCoder principles
- Separate package development concerns from reference implementation
- Create clear, non-conflicting agent guidance

**Tasks**
- [x] Identify structural issues and inconsistencies
- [ ] Create proper root pointer files (AGENTS.md, CLAUDE.md)
- [ ] Update context files with actual project values
- [ ] Fix project structure references to use project_tree.md
- [ ] Clarify package vs. project separation

**Testing Plan**
- Unit: CLI command tests (pytest)
- Integration: Full workflow smoke tests
- Manual: Agent interaction validation

**Risks & Rollback**
- Risk: Breaking existing agent workflows — mitigation: test with actual agent before committing
- Rollback: Git revert to previous working state

**Definition of Done**
- Agents can navigate from root to context without confusion
- No placeholder values in context files
- Clear separation between package and project concerns

---

## Phase 2 — Package Enhancement & API Development

**Objectives**
- Add JSON output mode for all commands
- Implement Python API mirroring CLI
- Add template variable substitution to init command
- Enhance pack command with preview/filtering options

**Tasks**
- [ ] Add --json flag to all CLI commands
- [ ] Create Python API in bpsai_pair.api module
- [ ] Implement cookiecutter variable substitution in init
- [ ] Add --dry-run and --list to pack command
- [ ] Write comprehensive API documentation

**Testing Plan**
- Unit: API method tests
- Integration: CLI-to-API parity tests
- Contract: JSON schema validation

---

## Phase 3 — Advanced Features & Ecosystem

**Objectives**
- Path-filtered CI workflows
- Integration with external tools (Trello, Jira)
- Web UI prototype (separate repo)

**Tasks**
- [ ] Implement path filters in CI workflows
- [ ] Create plugin architecture for integrations
- [ ] Document extension points and APIs
- [ ] Prototype paircoder-ui repository

---

## Backlog (Deferred / Parking Lot)

- [ ] GitHub Actions marketplace action — deferred: focus on core CLI first
- [ ] VSCode extension — deferred: await stable API
- [ ] Cloud-hosted context storage — deferred: security considerations

---

## Runbooks & Commands

- **Install package (dev):** `pip install -e tools/cli`
- **Run tests:** `cd tools/cli && pytest`
- **Build wheel:** `cd tools/cli && python -m build`
- **Local smoke test:** `./scripts/test_cli.sh`
- **Update context:** `bpsai-pair context-sync --last "..." --next "..."`

---

## Context Sync (AUTO-UPDATED)

**Overall goal is:** Develop and maintain PairCoder while dogfooding our own practices  
**Last action was:** Repository analysis and structural issues identification  
**Next action will be:** Implement proper agent guidance files and fix context  
**Blockers/Risks:** None currently

**Phase:** Phase 1: Repository Alignment & Documentation
