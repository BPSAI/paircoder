# Agents Guide — PairCoder Development Playbook

**Purpose:** Guide AI agents in developing and maintaining the PairCoder framework while demonstrating best practices for AI pair programming.

**Audience:** AI Agents (Claude, GPT-5, etc.) working on the PairCoder project.

---

## 0) Ground Rules (READ FIRST)

* **Dual Purpose:** This repo is BOTH the package source AND a reference implementation. Keep these concerns separate.
* **Package Files:** `tools/cli/` contains the installable package. Be careful with changes here.
* **Template Files:** `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` is what users receive. Only modify for template improvements.
* **Example Files:** Root-level files demonstrate proper usage. Keep them exemplary.
* **Context is King:** Always check `/context/development.md` for current state before starting work.

---

## 1) Repository Layout

**Authoritative structure:** Always refer to `/context/project_tree.md` for the current file structure. Key areas:

* **`/tools/cli/`** — The bpsai-pair package source
  - `bpsai_pair/` - Python package code
  - `bpsai_pair/data/cookiecutter-paircoder/` - User template (careful!)
  - `pyproject.toml` - Package configuration
  - `tests/` - Package tests

* **`/context/`** — Living project memory (canonical for agents)
  - `development.md` - Roadmap and Context Loop
  - `agents.md` - This file
  - `project_tree.md` - Auto-updated structure
  - `directory_notes/` - Component documentation

* **Root level** — Reference implementation
  - Demonstrates how users should structure their repos
  - Uses actual PairCoder workflows
  - Must stay aligned with what we ship

**Exclusions (.agentpackignore):**
- `tools/cli/dist/`, `tools/cli/build/` - Built artifacts
- `**/__pycache__`, `.venv/` - Python artifacts
- `assets/**` - Large files (if any)

---

## 2) Development Workflow

### For Package Changes (tools/cli/)

1. Create feature branch:
   ```bash
   bpsai-pair feature cli-enhancement --type refactor \
     --primary "Improve CLI feature X" \
     --phase "Add tests and implementation"
   ```

2. Make changes in `tools/cli/bpsai_pair/`
3. Run package tests:
   ```bash
   cd tools/cli && pytest
   ```

4. Test locally:
   ```bash
   pip install -e tools/cli
   bpsai-pair --help
   ```

5. Update Context Loop:
   ```bash
   bpsai-pair context-sync --last "Added feature X to CLI" \
     --next "Update documentation" --blockers ""
   ```

### For Template Changes (cookiecutter)

**CAREFUL:** Changes to `tools/cli/bpsai_pair/data/cookiecutter-paircoder/` affect what users receive!

1. Only modify if improving the template itself
2. Test with actual cookiecutter:
   ```bash
   cookiecutter tools/cli/bpsai_pair/data/cookiecutter-paircoder/
   ```
3. Ensure changes are generic (not specific to this repo)

### For Reference Implementation (root)

1. Follow standard PairCoder workflow
2. Keep files exemplary - they demonstrate best practices
3. Ensure alignment between what we do and what we ship

---

## 3) Testing Requirements

### Package Tests (Required)
- Unit tests for CLI commands: `tools/cli/tests/test_*.py`
- Smoke tests across platforms: `.github/workflows/cli-smoke.yml`
- Coverage target: ≥ 80% for core functionality

### Integration Tests
- Full workflow validation: `scripts/test_cli.sh`
- Must pass on Linux, macOS, Windows

### Manual Validation
- Test with actual AI agent before major releases
- Verify cookiecutter template produces working repo
- Ensure documentation matches implementation

---

## 4) Key Invariants

**Must Maintain:**
1. **Backward Compatibility:** Don't break existing CLI commands
2. **Cross-platform:** Pure Python, no shell dependencies
3. **Template Completeness:** Cookiecutter must produce fully functional repos
4. **Documentation Accuracy:** README, docstrings, and help text must be current
5. **Context Discipline:** Always update Context Loop after changes

**Must Avoid:**
1. Mixing package-specific files into the template
2. Hard-coding paths or assumptions about repo structure
3. Breaking the separation between package and reference implementation
4. Committing untested changes to CLI or template

---

## 5) Common Tasks

### Add New CLI Command
1. Add method to `tools/cli/bpsai_pair/cli.py`
2. Add tests to `tools/cli/tests/`
3. Update README with usage examples
4. Add to smoke test if critical path

### Update Template File
1. Edit in `tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/`
2. Test with fresh cookiecutter
3. Document in CHANGELOG.md
4. Consider if root example needs updating to match

### Fix Bug
1. Add failing test first
2. Fix in `tools/cli/bpsai_pair/`
3. Verify all tests pass
4. Update Context Loop

---

## 6) Context Loop (MANDATORY)

After EVERY meaningful change, update `/context/development.md`:

```bash
bpsai-pair context-sync \
  --last "Clear description of what changed and why" \
  --next "Immediate next step" \
  --blockers "Any issues or decisions needed"
```

This maintains continuity across agent sessions.

---

## 7) Release Process

1. Update version in `tools/cli/pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Build wheel: `cd tools/cli && python -m build`
5. Test wheel installation in fresh venv
6. Tag release: `git tag v0.X.Y`
7. Push to PyPI (when ready)

---

## 8) Architecture Decisions

Key decisions are documented in `/docs/adr/`:
- ADR-0001: Context Loop design
- (Add more as needed)

---

## 9) Getting Help

- Check `/context/development.md` for current goals and state
- Review `/docs/adr/` for design decisions
- Look at git history for implementation patterns
- Test changes thoroughly before committing

---

## 10) Quick Commands Reference

```bash
# Install for development
pip install -e tools/cli

# Run tests
cd tools/cli && pytest

# Create feature branch
bpsai-pair feature my-feature --type refactor

# Package context
bpsai-pair pack --out agent_pack.tgz

# Update context
bpsai-pair context-sync --last "..." --next "..."

# Test CLI end-to-end
./scripts/test_cli.sh

# Build package
cd tools/cli && python -m build
```
