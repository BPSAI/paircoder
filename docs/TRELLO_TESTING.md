# Trello Integration Testing Guide

> Manual verification steps for Trello integration (no credentials available in CI)

## Status

**Testing Status**: Needs Manual Verification

The Trello integration has been implemented and unit tested, but end-to-end testing requires Trello API credentials which are not available in the automated test environment.

## Unit Test Coverage (Automated)

The following are covered by automated tests in `tests/test_trello_*.py` (21 tests):

- TrelloClient initialization and mock API calls
- Board listing and selection logic
- Card state transitions
- Comment adding logic
- List mapping configuration
- Error handling for API failures
- CLI command parsing and argument validation

## Manual E2E Test Script

If you have Trello credentials, run these tests:

### Prerequisites

1. Get API key from https://trello.com/app-key
2. Generate token from the API key page
3. Create or identify a test board in Trello

### Test Sequence

```bash
# 1. Connect to Trello
bpsai-pair trello connect
# Enter API key and token when prompted
# Expected: "Successfully connected to Trello"

# 2. Verify connection
bpsai-pair trello status
# Expected: Shows "Connected" with username and member ID

# 3. List boards
bpsai-pair trello boards
# Expected: Table showing board IDs and names

# 4. Select a test board
bpsai-pair trello use-board <board-id>
# Expected: "Using board: <board-name>"

# 5. View board lists
bpsai-pair trello lists
# Expected: Table showing list names and IDs

# 6. Preview plan sync (dry-run)
bpsai-pair plan sync-trello plan-2025-01-paircoder-v2.4-mcp --dry-run
# Expected: Lists tasks that would be created as cards

# 7. Actually sync (if dry-run looks good)
# WARNING: This creates real cards in Trello
bpsai-pair plan sync-trello plan-2025-01-paircoder-v2.4-mcp
# Expected: Cards created for each task

# 8. Verify in Trello UI
# - Check board has lists for sprints (or default lists)
# - Check cards exist with correct titles
# - Check card descriptions have task details

# 9. Test task operations
bpsai-pair ttask list
# Expected: Lists cards from the board

bpsai-pair ttask show <card-id>
# Expected: Shows card details including description, labels, comments

bpsai-pair ttask start <card-id>
# Expected: Card moved to "In Progress" list

# Verify in Trello UI that card moved

bpsai-pair ttask comment <card-id> --message "Testing comment"
# Expected: Comment added to card

bpsai-pair ttask done <card-id> --summary "Integration test complete"
# Expected: Card moved to "Done" list

# 10. Disconnect
bpsai-pair trello disconnect
# Expected: Credentials removed

bpsai-pair trello status
# Expected: "Not connected"
```

### Expected Results

| Step | Command | Expected Outcome |
|------|---------|------------------|
| 1 | `trello connect` | Credentials stored in `.paircoder/trello.json` |
| 2 | `trello status` | Shows "Connected" with user info |
| 3 | `trello boards` | Lists available boards |
| 4 | `trello use-board` | Board ID saved to config |
| 5 | `trello lists` | Shows board lists |
| 6 | `plan sync-trello --dry-run` | Shows tasks without creating cards |
| 7 | `plan sync-trello` | Creates cards in Trello |
| 8 | UI verification | Cards visible in Trello web |
| 9a | `ttask list` | Shows cards from board |
| 9b | `ttask start` | Card moves to In Progress |
| 9c | `ttask comment` | Comment appears on card |
| 9d | `ttask done` | Card moves to Done |
| 10 | `trello disconnect` | Credentials removed |

### Cleanup

After testing:

1. In Trello web UI, delete test cards created during sync
2. Or archive the entire test board
3. Run `bpsai-pair trello disconnect` to remove credentials

## Hooks Integration

The hooks system integrates with Trello when `sync_trello` hook is enabled:

```yaml
# .paircoder/config.yaml
hooks:
  enabled: true
  on_task_start:
    - sync_trello    # Updates card when task starts
  on_task_complete:
    - sync_trello    # Updates card when task completes
  on_task_block:
    - sync_trello    # Updates card when task is blocked
```

To test hooks with Trello:

1. Connect to Trello with `bpsai-pair trello connect`
2. Sync a plan: `bpsai-pair plan sync-trello <plan-id>`
3. Start a task: `bpsai-pair task update TASK-XXX --status in_progress`
4. Verify card moved in Trello UI
5. Complete task: `bpsai-pair task update TASK-XXX --status done`
6. Verify card moved to Done in Trello UI

## MCP Tools Testing

Test the MCP Trello tools:

```bash
# Preview sync via MCP
bpsai-pair mcp test paircoder_trello_sync_plan --plan_id plan-2025-01-feature --dry_run true

# Update card via MCP (requires active Trello connection)
bpsai-pair mcp test paircoder_trello_update_card --task_id TASK-001 --action start
```

## Known Limitations

1. **Rate Limits**: Trello API has rate limits; bulk operations may be throttled
2. **Webhook Support**: Trello webhooks are not implemented (one-way sync only)
3. **Label Mapping**: Labels are not automatically synced from task tags
4. **Due Dates**: Task due dates are not synced to Trello cards

## Reporting Issues

If you encounter issues during manual testing:

1. Run with verbose output: `bpsai-pair --verbose trello <command>`
2. Check `.paircoder/trello.json` for stored credentials
3. Verify API key permissions at https://trello.com/app-key
4. Report issues at: https://github.com/anthropics/paircoder/issues

Include:
- Command that failed
- Error message
- Trello board ID (not credentials)
- PairCoder version (`bpsai-pair --version`)
