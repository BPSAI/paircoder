# EPIC-004: First-Time User Experience & Vibe-Coder UX

> **Goal:** A non-technical user ("vibe-coder") can go from `pip install` to productive in under 10 minutes without reading documentation.

> **Source:** K-Masty's first-time user testing (2025-12-22)

---

## Executive Summary

K-Masty, a non-coder user, attempted to set up PairCoder for the first time. His experience exposed significant UX gaps that would block adoption by the "vibe-coder" audience - people who want AI-augmented development without deep technical knowledge.

**Key Quote:**
> "For those of us who are not coders, and doing this for the first time, it is hard as shit to figure out."

**Critical Finding:** PairCoder was built by coders for coders. The UX assumes knowledge that vibe-coders don't have.

---

## Problems Discovered

### P1: Welcome Experience is Unhelpful

**Current behavior:**
```
PairCoder initialized in /path/to/project
Read .paircoder/context/state.md to understand the project.
```

**K-Masty's reaction:** "That doesn't really tell me anything."

**Impact:** User immediately lost, doesn't know next steps.

---

### P2: Trello Setup is a Nightmare

**Issues encountered:**

| Step | Problem | Time Wasted |
|------|---------|-------------|
| Start setup | py-trello not installed, no warning | Had to restart entire flow |
| Get API key | Couldn't find Trello admin page | 10+ min googling |
| New vs existing | No guidance on creating Power-Up | Confusion |
| After connect | "What do I do now?" | Lost again |

**K-Masty's feedback:**
> "You need to include a link to the admin page, that shit is super hard to find: https://trello.com/power-ups/admin/"

> "Really need interactive mode prompts for each of the next steps."

---

### P3: Config is Barebones After Connect

**What happened:** After `trello connect`, config.yaml only has 5 lines:
```yaml
trello:
  enabled: true
  board_id: "..."
```

**Missing:** hooks, estimation, metrics, routing, models - everything from the BPS preset.

**Root cause:** `trello connect` doesn't apply a preset. User should have run `init --preset bps` first, but didn't know.

**Fix needed:** Either:
- `trello connect` offers to apply preset
- `upgrade` command adds missing sections
- Better init flow that guides preset choice

---

### P4: Windows Compatibility Broken 🚨

**Error:**
```
'true' is not recognized as an internal or external command
The system cannot find the path specified.
```

**Root cause:** Unix shell syntax in hooks:
```bash
bpsai-pair context-sync --auto 2>/dev/null || true
```

**Impact:** Hooks fail on Windows. Non-blocking, but scary error messages.

**Fix:** Replace shell commands with pure Python subprocess calls.

---

### P5: Missing Reference Files

**Error:** `bps-board-conventions.md` not found

**Context:** This is a BPS-specific doc created for PairCoder's own development. Not in the template.

**Decision needed:** 
- Is this BPS-specific (don't include)?
- Or general (should generate/include)?

---

### P6: No Guided "First Run" Experience

**K-Masty's feedback:**
> "After the Trello integration is complete, what comes next? What exactly should I do next to test out these new superpowers?"

> "If I already have Claude Code installed, are there specific prompts that I could give him to tell him to review the PairCoder framework and get everything set up properly for me?"

**Missing:**
- Post-setup "what's next" guidance
- Ready-to-use Claude prompts
- "Your first 5 minutes" tutorial

---

### P7: Documentation Not Discovered

**K-Masty's admission:**
> "I did not read the user guide at all as I just wanted to see what it was all about and assume most people won't."

**Reality:** Nobody reads docs before trying. Docs should be linked contextually, not assumed.

---

### P8: Feature Matrix Stale

**K-Masty noticed** skill references and features that don't match current state.

**Action:** Update FEATURE_MATRIX.md after Sprint 19 completes.

---

## Proposed Solutions

### UX-001: Interactive Welcome & Setup Wizard

**Priority:** 🔴 Critical  
**Effort:** M (4-6 hours)  
**Sprint:** 23 or 24

**Proposed flow:**
```
╔═══════════════════════════════════════════════════════════════╗
║   🤖 Welcome to PairCoder v2.7!                               ║
║   AI-Augmented Pair Programming Framework                     ║
╚═══════════════════════════════════════════════════════════════╝

How would you like to use PairCoder?

  [1] 🚀 Quick Start      - File-based tasks, no integrations
  [2] 📋 With Trello      - Full board integration (recommended)
  [3] 🏢 BPS Workflow     - BPS AI preset with all features
  [4] ⚙️  Custom           - Choose your own options

Enter choice [2]: 
```

Each choice leads to a guided wizard that:
- Checks dependencies FIRST
- Provides links and instructions
- Confirms each step before proceeding
- Ends with "What's Next" specific to their setup

---

### UX-002: Trello Setup Wizard with Dependency Pre-Check

**Priority:** 🔴 Critical  
**Effort:** M (4-6 hours)  
**Sprint:** 23

**Requirements:**
1. Check py-trello installed BEFORE prompting for credentials
2. Offer to install missing dependencies
3. Provide direct link: `https://trello.com/power-ups/admin/`
4. Guide through new vs existing Power-Up
5. Explain each field being requested
6. List boards and let user select (or create new)
7. Verify connection works
8. Print specific next steps

**Implementation notes:**
- Use `questionary` or `rich.prompt` for interactive prompts
- Store partial progress in temp file so restarts don't lose work
- `--non-interactive` flag for CI/scripts with env vars

---

### UX-003: Post-Setup "What's Next" Guidance

**Priority:** 🔴 Critical  
**Effort:** S (2-3 hours)  
**Sprint:** 23

**After any setup completes, print contextual guidance:**

```python
def print_whats_next(config):
    console.print("\n[bold]🎯 What's Next?[/bold]\n")
    
    if config.trello.enabled:
        console.print("  View available tasks:")
        console.print("    [cyan]bpsai-pair ttask list[/cyan]\n")
        console.print("  Start working on a task:")
        console.print("    [cyan]bpsai-pair ttask start <card-id>[/cyan]\n")
    else:
        console.print("  Create your first plan:")
        console.print("    [cyan]bpsai-pair plan new my-feature --type feature[/cyan]\n")
    
    console.print("  [dim]Or open Claude Code and say:[/dim]")
    console.print("  [green]'What can I work on next?'[/green]\n")
    
    console.print("  📖 Full guide: .paircoder/docs/USER_GUIDE.md")
```

---

### UX-004: Ready-to-Paste Claude Prompts

**Priority:** 🟡 High  
**Effort:** S (1-2 hours)  
**Sprint:** 23

**After setup, print a Claude prompt:**

```
🤖 Quick Start with Claude Code
───────────────────────────────

Open Claude Code in this project and paste:

┌────────────────────────────────────────────────────────────────┐
│ Review this project's PairCoder setup:                        │
│ 1. Read .paircoder/capabilities.yaml                          │
│ 2. Read .paircoder/context/state.md                           │
│ 3. Tell me what tasks are available                           │
│ 4. Help me get started with my first task                     │
└────────────────────────────────────────────────────────────────┘
```

**Also create:** `/get-started` slash command in `.claude/commands/`

---

### UX-005: `upgrade` Command (Content Updates)

**Priority:** 🔴 Critical  
**Effort:** M (4-6 hours)  
**Sprint:** 19 (already spec'd as T19.11)

**Solves:** K-Masty's barebones config problem

```bash
# Show what's outdated
bpsai-pair upgrade --dry-run

# Update to latest
bpsai-pair upgrade

# Apply specific preset's config additions
bpsai-pair upgrade --preset bps
```

**Note:** Full spec in T19.11 (T-upgrade-command-spec.md)

---

### UX-006: Windows Compatibility Fix

**Priority:** 🔴 Critical (Bug)  
**Effort:** S (2-3 hours)  
**Sprint:** 19 or 20

**Files to fix:**
- `hooks.py` - Any shell commands
- Anywhere using `2>/dev/null || true`

**Pattern:**
```python
# Before (Unix only)
os.system("bpsai-pair context-sync --auto 2>/dev/null || true")

# After (cross-platform)
try:
    subprocess.run(
        ["bpsai-pair", "context-sync", "--auto"],
        capture_output=True,
        check=False,
        timeout=30
    )
except Exception:
    pass  # Non-blocking
```

---

### UX-007: BPS Board Conventions Decision

**Priority:** 🟢 Low  
**Effort:** XS (30 min)  
**Sprint:** 24+

**Options:**
1. **BPS-specific** - Only include with `--preset bps`, not general template
2. **Auto-generate** - Detect board structure, generate conventions doc
3. **Skip** - Just remove the reference, Claude works without it

**Recommendation:** Option 1 - make it BPS preset-specific

---

### UX-008: Contextual Doc Links

**Priority:** 🟢 Low  
**Effort:** XS (1 hour)  
**Sprint:** 24+

**Instead of:** "See USER_GUIDE.md"

**Do:** Link to specific sections:
```python
console.print("📖 Trello setup: .paircoder/docs/USER_GUIDE.md#trello-integration")
```

---

### UX-009: "Create Board from Template" Command

**Priority:** 🟡 High  
**Effort:** M (4-6 hours)  
**Sprint:** 24

```bash
# Create board with BPS structure
bpsai-pair trello init-board --name "My Project" --preset bps

# Create from existing template board
bpsai-pair trello init-board --name "My Project" --from-template "BPS Template"
```

**Note:** This was ENH-001 in PAIRCODER-BACKLOG.md

---

## Sprint Allocation

### Sprint 19 (Current)
- T19.11: `upgrade` command (already spec'd)
- UX-006: Windows compatibility fix (critical bug)

### Sprint 23 (After Refactor Phase 2)
- UX-001: Interactive welcome wizard
- UX-002: Trello setup wizard
- UX-003: Post-setup guidance
- UX-004: Claude prompts

### Sprint 24 (After Refactor Phase 3)
- UX-009: Create board from template
- UX-007: BPS board conventions decision
- UX-008: Contextual doc links

### Sprint 25 (Polish)
- Feature Matrix update
- User Guide improvements
- Final UX testing with K-Masty

---

## Success Criteria

- [ ] K-Masty can set up a new project in < 10 minutes
- [ ] No "what do I do now?" moments after any command
- [ ] Works on Windows without shell errors
- [ ] Non-coder can get productive without reading docs
- [ ] Trello setup works first try (no restarts)
- [ ] Config is complete after setup (not barebones)

---

## Dependencies

| Item | Depends On |
|------|------------|
| UX-001 (wizard) | EPIC-003 refactor complete (cli.py clean) |
| UX-002 (Trello wizard) | UX-006 (Windows fix) |
| UX-005 (upgrade cmd) | Nothing - can do now |
| UX-006 (Windows fix) | Nothing - should do ASAP |

---

## Testing Plan

1. **K-Masty retest** - Have K-Masty try again after Sprint 23
2. **Fresh Windows VM** - Test full flow on Windows
3. **"Mom test"** - Can a non-technical person follow the prompts?
4. **Time trial** - Measure time from `pip install` to first task started

---

## Appendix: K-Masty's Raw Feedback

### Round 1
- Welcome screen should be WAY cooler
- Welcome message just says read state.md - doesn't tell me anything
- Need prompts to select choices (preset, as-is, Trello)
- Had to install py-trello manually, duplicated efforts
- Need link to admin page: https://trello.com/power-ups/admin/
- Need instructions for new vs existing Power-Up
- Need interactive prompts for each step
- After Trello complete, what comes next?
- What specific docs need filled out?
- What prompts can I give Claude to set up for me?
- User guide link in prompts would help

### Round 2
- Config.yaml only has basic Trello stuff (5 lines)
- Windows error: `'true' is not recognized`
- bps-board-conventions.md doesn't exist error
- Feature matrix may be behind reality

---

## Document History

| Date | Author | Changes                                |
|------|--------|----------------------------------------|
| 2025-12-22 | Claude (Opus 4.5) | Initial compilation from user feedback |
