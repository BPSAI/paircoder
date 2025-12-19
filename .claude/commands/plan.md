Enter Navigator role. Read `.claude/skills/trello-aware-planning/SKILL.md` and `.claude/agents/planner.md` for context.

Read the backlog file: `.paircoder/context/$ARGUMENTS`

Then:
1. Analyze and prioritize items (P0-P3)
2. Determine appropriate plan slug, type (feature|bugfix|maintenance|refactor), and title based on backlog contents
3. Create plan: `bpsai-pair plan new <slug> --type <type> --title "<title>"`
4. Generate task files in `.paircoder/tasks/` with acceptance criteria
5. Sync to Trello: `bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"`
6. Update `.paircoder/context/state.md` with new plan
7. Report summary: tasks created, complexity points, Trello sync status
