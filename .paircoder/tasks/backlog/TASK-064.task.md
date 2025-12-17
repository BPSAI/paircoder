---
id: TASK-064
title: Create current task status bar widget
plan: plan-2025-12-sprint-13-autonomy
type: feature
priority: P3
complexity: 35
status: planned
sprint: sprint-13
tags:
- ide
- vscode
- status-bar
- ux
---

# Objective

Create a VS Code status bar widget that displays information about the currently active task, including task ID, title, status, and elapsed time. The widget provides quick access to task actions and serves as a constant reminder of the current focus.

# Background

This is part of the VS Code extension (TASK-063). The status bar is the thin bar at the bottom of VS Code that shows information like line number, language mode, etc. We want to add a PairCoder section that shows:
- Current task being worked on
- Time spent on task
- Quick actions (complete, block)

# Implementation Plan

## 1. Status Bar Item Structure

Create the status bar component:

```typescript
// src/views/statusBar.ts
import * as vscode from 'vscode';

export class TaskStatusBar {
  private statusBarItem: vscode.StatusBarItem;
  private currentTaskId: string | null = null;
  private startTime: Date | null = null;
  private updateInterval: NodeJS.Timer | null = null;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      100  // Priority - higher = more left
    );
    this.statusBarItem.command = 'paircoder.task.showCurrent';
  }

  setTask(taskId: string, taskTitle: string, status: string): void {
    this.currentTaskId = taskId;
    this.startTime = new Date();
    this.updateDisplay(taskTitle, status);
    this.startTimeUpdate();
  }

  clearTask(): void {
    this.currentTaskId = null;
    this.startTime = null;
    this.stopTimeUpdate();
    this.statusBarItem.hide();
  }

  private updateDisplay(title: string, status: string): void {
    const elapsed = this.getElapsedTime();
    const icon = this.getStatusIcon(status);

    // Format: $(icon) TASK-001: Title [1h 23m]
    this.statusBarItem.text = `${icon} ${this.currentTaskId}: ${this.truncate(title, 30)} [${elapsed}]`;
    this.statusBarItem.tooltip = new vscode.MarkdownString(
      `**Current Task**\n\n` +
      `**ID:** ${this.currentTaskId}\n\n` +
      `**Title:** ${title}\n\n` +
      `**Status:** ${status}\n\n` +
      `**Time:** ${elapsed}\n\n` +
      `_Click to show task details_`
    );
    this.statusBarItem.show();
  }

  private getStatusIcon(status: string): string {
    const icons: Record<string, string> = {
      'in_progress': '$(sync~spin)',
      'pending': '$(circle-outline)',
      'done': '$(check)',
      'blocked': '$(warning)',
      'review': '$(eye)',
    };
    return icons[status] || '$(tasklist)';
  }

  private getElapsedTime(): string {
    if (!this.startTime) return '0m';
    const elapsed = Date.now() - this.startTime.getTime();
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }

  private truncate(text: string, maxLength: number): string {
    return text.length > maxLength
      ? text.substring(0, maxLength - 3) + '...'
      : text;
  }

  private startTimeUpdate(): void {
    this.updateInterval = setInterval(() => {
      if (this.currentTaskId) {
        // Re-fetch task to update display
        this.statusBarItem.text = this.statusBarItem.text.replace(
          /\[.*\]$/,
          `[${this.getElapsedTime()}]`
        );
      }
    }, 60000); // Update every minute
  }

  private stopTimeUpdate(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  dispose(): void {
    this.stopTimeUpdate();
    this.statusBarItem.dispose();
  }
}
```

## 2. Status Bar States

Define visual states for different scenarios:

| State | Icon | Color | Text |
|-------|------|-------|------|
| No active task | $(tasklist) | default | "No active task" |
| Task in progress | $(sync~spin) | green | "TASK-001: Title [5m]" |
| Task blocked | $(warning) | yellow | "TASK-001: Title [BLOCKED]" |
| Task in review | $(eye) | blue | "TASK-001: Title [REVIEW]" |

## 3. Quick Actions Menu

Add a quick actions menu when clicking the status bar:

```typescript
// Register command for status bar click
vscode.commands.registerCommand('paircoder.task.showCurrent', async () => {
  if (!currentTaskId) {
    // Show task picker if no task selected
    await vscode.commands.executeCommand('paircoder.task.pick');
    return;
  }

  const action = await vscode.window.showQuickPick([
    { label: '$(eye) View Task', description: 'Show full task details', action: 'view' },
    { label: '$(check) Complete Task', description: 'Mark task as done', action: 'complete' },
    { label: '$(warning) Block Task', description: 'Mark task as blocked', action: 'block' },
    { label: '$(clock) Show Time', description: 'Show time tracking details', action: 'time' },
    { label: '$(x) Stop Task', description: 'Stop working on this task', action: 'stop' },
  ], {
    placeHolder: `Task: ${currentTaskId}`,
  });

  if (action) {
    // Execute the selected action
    await handleAction(action.action);
  }
});
```

## 4. Integration Points

Connect status bar to:
- Time tracking system (hooks.py timers)
- Task status updates
- MCP server events
- File watcher for task file changes

## 5. Configuration Options

```json
{
  "paircoder.statusBar.enabled": true,
  "paircoder.statusBar.showTimer": true,
  "paircoder.statusBar.position": "left",
  "paircoder.statusBar.maxTitleLength": 30
}
```

# Acceptance Criteria

- [ ] Status bar item appears when extension is active
- [ ] Shows "No active task" when no task is in progress
- [ ] Displays task ID and truncated title when task is active
- [ ] Shows elapsed time that updates every minute
- [ ] Click opens quick actions menu
- [ ] Can complete/block task from quick actions
- [ ] Status bar updates when task status changes
- [ ] Configurable via VS Code settings
- [ ] Correct icons for different statuses

# Dependencies

- TASK-063: VS Code extension wrapper for MCP (base extension)

# Verification

```bash
# Test status bar functionality
1. Open VS Code with PairCoder extension
2. Verify status bar shows "No active task"
3. Start a task using command palette
4. Verify status bar updates with task info
5. Wait 1+ minutes and verify timer updates
6. Click status bar and verify quick actions appear
7. Complete task and verify status bar resets
8. Toggle statusBar.enabled setting and verify visibility
```

# Notes

- Consider adding notification when task has been active for > 2 hours
- Status bar should persist across VS Code window reloads
- Timer should sync with server-side time tracking for accuracy
- Consider adding color background for blocked tasks
