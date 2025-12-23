---
id: RFE-001
title: Remote orchestration API
plan: backlog
type: feature
priority: P3
complexity: 60
status: backlog
sprint: future
tags:
  - api
  - remote
  - orchestration
  - integration
---

# Objective

Expose PairCoder tools via HTTP API for remote orchestration.

This enables:
- Claude.ai to trigger workflows on your machine
- CI/CD pipelines to manage tasks
- External dashboards to interact with PairCoder
- Multi-machine orchestration

# Vision

```
Claude.ai (or any client)
        ↓
   HTTP/WebSocket
        ↓
PairCoder API Server (your machine)
        ↓
   MCP Tools / CLI
        ↓
   .paircoder/ + Trello
```

# Implementation Plan

1. Create HTTP server wrapper around MCP tools
   ```python
   from fastapi import FastAPI
   
   app = FastAPI()
   
   @app.post("/tools/{tool_name}")
   async def invoke_tool(tool_name: str, params: dict, api_key: str):
       verify_api_key(api_key)
       return await mcp_server.call_tool(tool_name, params)
   ```

2. Add authentication
   - API key authentication
   - Optional OAuth for web clients
   - Rate limiting

3. Create CLI command
   ```bash
   bpsai-pair api serve --port 8080 --auth-token $SECRET
   ```

4. Add WebSocket for streaming
   - Real-time task updates
   - Log streaming
   - Progress notifications

5. Create client library
   ```python
   from paircoder_client import PairCoderClient
   
   client = PairCoderClient("https://your-server:8080", api_key="...")
   tasks = client.task_list(status="pending")
   client.task_start("TASK-081")
   ```

# Security Considerations

- [ ] API key rotation
- [ ] IP allowlisting option
- [ ] Audit logging
- [ ] Command sandboxing (no arbitrary execution)
- [ ] HTTPS required in production

# Acceptance Criteria

- [ ] API server starts with `bpsai-pair api serve`
- [ ] All MCP tools accessible via HTTP
- [ ] Authentication working
- [ ] Can trigger workflow from remote client
- [ ] Claude.ai can call API (with web_fetch)

# Why This Is Badass

Once this exists:
1. You tell me (claude.ai) "Start Sprint 14"
2. I call your API to create the plan
3. I call your API to sync to Trello
4. I call your API to kick off Claude Code
5. Work happens on your machine while you sleep
6. I can check progress via API

True remote orchestration. 🚀

# Files to Create

- `tools/cli/bpsai_pair/api/` (new package)
- `tools/cli/bpsai_pair/api/server.py`
- `tools/cli/bpsai_pair/api/auth.py`
- `tools/cli/bpsai_pair/api/routes.py`
- `tools/cli/bpsai_pair/api/websocket.py`
