# Sprint 26: UX Overhaul (EPIC-004)

> **Version:** v2.9.0
> **Duration:** 5-7 days
> **Theme:** "Vibe-coder friendly"
> **Source:** EPIC-004-vibe-coder-ux-comprehensive.md

---

## Sprint Goal

Make PairCoder usable by non-technical users ("vibe-coders"). A user should go from `pip install` to productive in under 10 minutes without reading documentation.

**Success Metric:** K-Masty can set up a new project without getting stuck.

---

## Background

K-Masty's first-time user testing exposed critical UX gaps:

| Problem | Impact |
|---------|--------|
| Welcome screen unhelpful | User immediately lost |
| Trello setup nightmare | 10+ min wasted, had to restart |
| No post-setup guidance | "What do I do now?" |
| No dependency pre-checks | py-trello not installed, flow broken |
| Documentation not discovered | Nobody reads docs before trying |

**Key Quote:** "For those of us who are not coders, and doing this for the first time, it is hard as shit to figure out."

---

## Prerequisites

**Completed:**
- ✅ EPIC-003 CLI Refactor (all 5 phases)
- ✅ Sprint 23 critical fixes (Windows, ttask enforcement, upgrade)
- ✅ Sprint 25 token budget system
- ✅ Sprint 25 project root detection fix

---

## Task List

### Part A: Interactive Setup Experience (3 tasks)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T26.1 | Interactive welcome wizard | feature | M | 40 |
| T26.2 | Trello setup wizard with pre-checks | feature | M | 45 |
| T26.3 | Post-setup "what's next" guidance | feature | S | 20 |

**T26.1 Details - Welcome Wizard:**

Replace boring init message with interactive experience:

```
╔═══════════════════════════════════════════════════════════════╗
║   🤖 Welcome to PairCoder v2.9!                               ║
║   AI-Augmented Pair Programming Framework                     ║
╚═══════════════════════════════════════════════════════════════╝

How would you like to use PairCoder?

  [1] 🚀 Quick Start      - File-based tasks, no integrations
  [2] 📋 With Trello      - Full board integration (recommended)
  [3] 🏢 BPS Workflow     - BPS AI preset with all features
  [4] ⚙️  Custom           - Choose your own options

Enter choice [2]: 
```

Each choice leads to guided flow:
- Quick Start → Basic init, show next steps
- With Trello → T26.2 wizard
- BPS Workflow → Apply bps preset + Trello wizard
- Custom → Existing behavior with prompts

**T26.2 Details - Trello Wizard:**

1. **Pre-flight checks:**
   ```
   Checking requirements...
     ✅ bpsai-pair installed
     ❌ py-trello not found
   
   Install py-trello? [Y/n]: 
   ```

2. **Guided credentials:**
   ```
   Step 1: Get your API key and token
   
   Go to: https://trello.com/power-ups/admin/
   
   📋 If you don't have a Power-Up yet:
      1. Click "New" in the top right
      2. Name it "PairCoder" (or anything)
      3. Click "Generate a new API key"
   
   📋 If you have an existing Power-Up:
      1. Click on it
      2. Click "Generate a new API key" (or copy existing)
   
   Paste your API key: 
   ```

3. **Board selection:**
   ```
   Step 3: Select a board
   
   Found 5 boards:
     [1] PairCoder
     [2] BPS Support App
     [3] Personal Tasks
     [4] → Create new board
   
   Select board [1]: 
   ```

4. **Verification:**
   ```
   Verifying connection...
     ✅ API key valid
     ✅ Token valid
     ✅ Board "PairCoder" accessible
     ✅ Lists found: 7
   
   Trello connected! ✨
   ```

**T26.3 Details - Post-Setup Guidance:**

After any setup, show contextual next steps:

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
```

**Acceptance Criteria:**
- [ ] `bpsai-pair init` shows interactive wizard
- [ ] Wizard checks dependencies before prompting
- [ ] Trello setup provides admin page link
- [ ] Board selection from list (not manual ID entry)
- [ ] Post-setup shows contextual next steps
- [ ] Non-interactive mode still works (`--non-interactive`)

---

### Part B: Claude Integration Helpers (2 tasks)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T26.4 | Generate Claude prompts after setup | feature | S | 15 |
| T26.5 | Create /get-started slash command | feature | XS | 10 |

**T26.4 Details:**

After setup, print a ready-to-paste Claude prompt:

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

This prompt is saved to: .claude/prompts/get-started.txt
```

**T26.5 Details:**

Create `.claude/commands/get-started.md`:

```markdown
---
description: Get oriented with this PairCoder project
---

Please review this project's PairCoder setup:

1. Read .paircoder/capabilities.yaml to understand your capabilities
2. Read .paircoder/context/state.md for current status
3. List available tasks with `bpsai-pair task list` or `bpsai-pair ttask list`
4. Help me understand what I should work on next

Start by telling me:
- What's the current project status?
- What tasks are available?
- What would you recommend I focus on?
```

**Acceptance Criteria:**
- [ ] Claude prompt displayed after setup
- [ ] Prompt saved to file for easy access
- [ ] `/get-started` slash command exists in template
- [ ] Slash command works in Claude Code

---

### Part C: Board & Template Creation (1 task)

| ID | Title | Type | Effort | Complexity |
|----|-------|------|--------|------------|
| T26.6 | Create board from template command | feature | M | 40 |

**T26.6 Details:**

```bash
# Create board with BPS structure
bpsai-pair trello init-board --name "My Project" --preset bps

# Create from existing template board
bpsai-pair trello init-board --name "My Project" --from-template "BPS Template"
```

When using `--preset bps`:
1. Create board with standard BPS lists
2. Add custom fields (Project, Stack, Status, Effort)
3. Add labels with correct colors
4. Configure Butler rules (if possible via API)
5. Save board_id to config

**Acceptance Criteria:**
- [ ] `trello init-board --name X --preset bps` creates board
- [ ] Board has correct list structure
- [ ] Custom fields created
- [ ] Labels created with correct colors
- [ ] Board ID saved to config.yaml

---

### Part D: Documentation & Polish (4 tasks)

| ID | Title                           | Type | Effort | Complexity |
|----|---------------------------------|------|--------|------------|
| T26.7 | Contextual doc links in output  | feature | S | 15 |
| T26.8 | Update USER_GUIDE.md for new UX | docs | M | 30 |
| T26.9 | Update README.md quick start    | docs | S | 15 |
| T26.10 | K-Masty retest session          | chore | - | - |

**T26.7 Details:**

Instead of "See USER_GUIDE.md", link to specific sections:

```python
# Bad
console.print("See USER_GUIDE.md for more info")

# Good
console.print("📖 Trello setup: docs/USER_GUIDE.md#trello-integration")
console.print("📖 Creating plans: docs/USER_GUIDE.md#creating-plans")
```

**T26.10 Details:**

Schedule session with K-Masty to:
1. Fresh install from pip
2. Run through setup wizard
3. Connect to Trello
4. Start first task
5. Document any remaining friction

**Acceptance Criteria:**
- [ ] Error messages include relevant doc links
- [ ] USER_GUIDE.md updated with wizard screenshots
- [ ] README.md quick start reflects new UX
- [ ] K-Masty can set up in < 10 minutes

---

## Sprint Summary

| Part | Description | Tasks | Complexity |
|------|-------------|-------|------------|
| A | Interactive Setup | 3 | 105 |
| B | Claude Helpers | 2 | 25 |
| C | Board Creation | 1 | 40 |
| D | Documentation | 4 | 60 |
| **Total** | | **10** | **230** |

---

## Task Dependencies

```
T26.1 (welcome wizard)
   │
   ├── T26.2 (Trello wizard) ── T26.6 (board creation)
   │
   └── T26.3 (what's next) ── T26.4 (Claude prompts)
                                    │
                              T26.5 (slash command)

T26.7 (doc links) ── T26.8 (USER_GUIDE) ── T26.9 (README)
                                                 │
                                           T26.10 (K-Masty retest)
```

---

## Files to Create/Modify

**New Files:**
- `.claude/commands/get-started.md`
- `.claude/prompts/get-started.txt` (template)

**Modified Files:**
- `commands/core.py` - Add wizard to init
- `trello/commands.py` - Add init-board, improve connect
- `docs/USER_GUIDE.md`
- `README.md`
- Cookie cutter template files

---

## Definition of Done

- [ ] `bpsai-pair init` has interactive wizard
- [ ] Trello setup checks dependencies first
- [ ] Trello setup provides admin page link
- [ ] Board can be created from preset
- [ ] Post-setup shows contextual next steps
- [ ] Claude prompt generated after setup
- [ ] `/get-started` slash command exists
- [ ] Documentation updated
- [ ] K-Masty can set up in < 10 minutes
- [ ] Version bumped to v2.9.0
- [ ] CHANGELOG.md updated

---

## EPIC-004 Coverage

This sprint completes EPIC-004 except for the following items which are deferred:

**Deferred to future sprints:**
- Multi-project workspace support (EPIC-001)
- Skill discovery and recommendations
- AI-powered task suggestions

**Partially addressed:**
- Error message improvements (T26.7 adds doc links, full overhaul deferred)
