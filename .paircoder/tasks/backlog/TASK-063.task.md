---
id: TASK-063
title: VS Code extension wrapper for MCP
plan: plan-2025-12-sprint-13-autonomy
type: feature
priority: P3
complexity: 45
status: planned
sprint: sprint-13
tags:
- ide
- vscode
- mcp
- integration
---

# Objective

Create a VS Code extension that wraps the PairCoder MCP server, providing a native IDE experience for interacting with tasks, plans, and workflow features.

# Background

The MCP (Model Context Protocol) server already exists in `bpsai_pair/mcp/`. This extension will:
1. Connect to the MCP server running locally
2. Provide VS Code UI components for task management
3. Enable Claude Code-like features within VS Code

# Implementation Plan

## 1. Project Setup

Create VS Code extension project structure:
```
tools/vscode-extension/
├── package.json           # Extension manifest
├── tsconfig.json         # TypeScript config
├── src/
│   ├── extension.ts      # Entry point
│   ├── mcpClient.ts      # MCP server connection
│   ├── providers/
│   │   ├── taskProvider.ts    # Task tree view
│   │   ├── planProvider.ts    # Plan tree view
│   │   └── flowProvider.ts    # Flow commands
│   ├── views/
│   │   ├── statusBar.ts       # Status bar items
│   │   ├── taskPanel.ts       # Task webview panel
│   │   └── contextPanel.ts    # Context viewer
│   └── commands/
│       ├── taskCommands.ts    # Task operations
│       ├── flowCommands.ts    # Flow operations
│       └── contextCommands.ts # Context sync
├── media/                # Icons and styles
└── README.md
```

## 2. MCP Client Implementation

Create client to connect to PairCoder MCP server:

```typescript
// mcpClient.ts
import { spawn, ChildProcess } from 'child_process';

class MCPClient {
  private process: ChildProcess | null = null;

  async connect(): Promise<void> {
    // Start MCP server as subprocess
    this.process = spawn('bpsai-pair', ['mcp', 'serve']);
  }

  async callTool(name: string, args: any): Promise<any> {
    // Send JSON-RPC request to MCP server
  }

  // Tool wrappers
  async listTasks(planId?: string): Promise<Task[]>;
  async getTask(taskId: string): Promise<Task>;
  async updateTask(taskId: string, updates: any): Promise<void>;
  async listPlans(): Promise<Plan[]>;
  async runFlow(flowName: string, taskId: string): Promise<void>;
}
```

## 3. Tree View Providers

### Task Tree View
- Shows tasks grouped by plan and status
- Icons for task type (feature, bug, etc.)
- Color coding for priority (P0=red, P1=orange, P2=yellow)
- Context menu for start, complete, block actions

### Plan Tree View
- Shows all plans with progress indicators
- Expandable to show tasks under each plan
- Quick filters for sprint, status

## 4. Commands

Register VS Code commands:
- `paircoder.task.start` - Start working on a task
- `paircoder.task.complete` - Mark task complete
- `paircoder.task.block` - Block a task
- `paircoder.task.show` - Show task details
- `paircoder.flow.run` - Run a flow
- `paircoder.context.sync` - Sync context files
- `paircoder.pack` - Create agent pack

## 5. Webview Panels

### Task Detail Panel
- Shows full task content in markdown
- Edit button to modify task file
- Quick actions toolbar

### Context Viewer
- Display current context files
- Edit in place
- Auto-refresh on file changes

## 6. Configuration

Add VS Code settings:
```json
{
  "paircoder.mcpServerPath": "bpsai-pair",
  "paircoder.autoConnect": true,
  "paircoder.statusBar.enabled": true,
  "paircoder.taskView.groupBy": "plan"
}
```

# Acceptance Criteria

- [ ] Extension activates when .paircoder directory is present
- [ ] Can connect to MCP server and list tasks
- [ ] Task tree view shows all tasks with correct status
- [ ] Can start/complete/block tasks from tree view
- [ ] Status bar shows current task info
- [ ] Flow commands execute correctly
- [ ] Context sync works via command palette
- [ ] Extension works offline with direct file access

# Dependencies

- MCP server implementation (already exists)
- Node.js and npm for extension development
- VS Code Extension API knowledge

# Verification

```bash
# Build extension
cd tools/vscode-extension
npm install
npm run compile

# Package extension
npx vsce package

# Test in VS Code
code --extensionDevelopmentPath=./

# Verify features
1. Open a project with .paircoder directory
2. Check that PairCoder tree view appears
3. Verify tasks are listed correctly
4. Try start/complete actions
5. Check status bar updates
```

# Notes

- Consider using VS Code's built-in webview for rich task display
- MCP server should be started automatically when extension loads
- Fall back to direct file access if MCP server unavailable
- Consider supporting Cursor IDE as well (same API)
