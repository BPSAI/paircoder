---
id: HF-001
title: Auto-update context on file save
plan: hotfix
type: feature
priority: P3
complexity: 30
status: planned
sprint: hotfix
tags:
- ide
- context
- file-watcher
---

# Objective

Automatically update PairCoder context files when relevant project files are saved. This ensures context files stay in sync with the codebase without requiring manual updates, improving the accuracy of AI-assisted development.

# Background

PairCoder uses context files in `.paircoder/context/` to provide project information to AI agents:
- `project.md` - Project overview, tech stack, architecture
- `state.md` - Current focus, active tasks, recent changes
- `workflow.md` - Development workflow and conventions

When code files change, these context files may become outdated. This feature will:
1. Watch for file saves in the project
2. Determine which context files need updating
3. Automatically update relevant sections

# Implementation Plan

## 1. File Watcher Setup

Create file watcher in VS Code extension:

```typescript
// src/watchers/contextWatcher.ts
import * as vscode from 'vscode';
import * as path from 'path';

export class ContextFileWatcher {
  private watcher: vscode.FileSystemWatcher | null = null;
  private debounceTimer: NodeJS.Timeout | null = null;
  private pendingUpdates: Set<string> = new Set();

  constructor(private mcpClient: MCPClient) {}

  start(): void {
    // Watch for all file changes in workspace
    this.watcher = vscode.workspace.createFileSystemWatcher(
      '**/*',
      false,  // create
      false,  // change
      false   // delete
    );

    this.watcher.onDidChange(uri => this.handleFileChange(uri, 'change'));
    this.watcher.onDidCreate(uri => this.handleFileChange(uri, 'create'));
    this.watcher.onDidDelete(uri => this.handleFileChange(uri, 'delete'));
  }

  private handleFileChange(uri: vscode.Uri, action: string): void {
    // Ignore .paircoder directory itself
    if (uri.fsPath.includes('.paircoder')) return;

    // Ignore common non-source files
    const ignoredPatterns = [
      /node_modules/,
      /\.git/,
      /\.venv/,
      /__pycache__/,
      /\.pyc$/,
      /\.log$/,
      /\.tmp$/,
    ];
    if (ignoredPatterns.some(p => p.test(uri.fsPath))) return;

    // Add to pending updates
    this.pendingUpdates.add(uri.fsPath);

    // Debounce updates (wait 2 seconds after last change)
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(() => this.processPendingUpdates(), 2000);
  }

  private async processPendingUpdates(): Promise<void> {
    if (this.pendingUpdates.size === 0) return;

    const files = Array.from(this.pendingUpdates);
    this.pendingUpdates.clear();

    // Determine which context files need updating
    const updates = this.determineContextUpdates(files);

    for (const update of updates) {
      await this.updateContextFile(update.file, update.section, update.data);
    }
  }

  private determineContextUpdates(files: string[]): ContextUpdate[] {
    const updates: ContextUpdate[] = [];

    // Check file types and determine context updates
    const hasSourceChanges = files.some(f =>
      /\.(ts|js|py|tsx|jsx|go|rs|java)$/.test(f)
    );
    const hasConfigChanges = files.some(f =>
      /(package\.json|pyproject\.toml|Cargo\.toml|go\.mod)/.test(f)
    );
    const hasReadmeChanges = files.some(f =>
      /README\.md$/i.test(f)
    );

    if (hasSourceChanges) {
      updates.push({
        file: 'state.md',
        section: 'recent_changes',
        data: { files, timestamp: new Date().toISOString() },
      });
    }

    if (hasConfigChanges) {
      updates.push({
        file: 'project.md',
        section: 'dependencies',
        data: { files },
      });
    }

    return updates;
  }

  private async updateContextFile(
    file: string,
    section: string,
    data: any
  ): Promise<void> {
    try {
      // Call MCP tool to update context
      await this.mcpClient.callTool('update_context', {
        file,
        section,
        data,
      });
    } catch (error) {
      console.error(`Failed to update context ${file}:`, error);
    }
  }

  stop(): void {
    if (this.watcher) {
      this.watcher.dispose();
      this.watcher = null;
    }
  }
}
```

## 2. Context Update Rules

Define rules for what triggers context updates:

| File Pattern | Context File | Section | Update Type |
|--------------|--------------|---------|-------------|
| `*.ts`, `*.py`, etc. | state.md | Recent Changes | Append |
| `package.json` | project.md | Dependencies | Refresh |
| `README.md` | project.md | Overview | Refresh |
| Task files | state.md | Current Focus | Refresh |
| New files in `/src` | project.md | Structure | Append |

## 3. State.md Auto-Update

Update the "Recent Changes" section:

```markdown
## Recent Changes

- 2024-01-15 14:30: Modified src/auth/login.ts
- 2024-01-15 14:28: Created src/auth/signup.ts
- 2024-01-15 14:25: Modified tests/auth.test.ts
```

## 4. Project.md Auto-Update

Update dependency and structure sections:

```typescript
async function updateProjectDependencies(packageJson: any): Promise<void> {
  const deps = Object.keys(packageJson.dependencies || {});
  const devDeps = Object.keys(packageJson.devDependencies || {});

  // Update project.md dependencies section
  const content = `
## Dependencies

### Runtime
${deps.map(d => `- ${d}`).join('\n')}

### Development
${devDeps.map(d => `- ${d}`).join('\n')}
`;
}
```

## 5. MCP Tool Integration

Add MCP tool for context updates:

```python
# bpsai_pair/mcp/tools/context.py
@tool("update_context")
async def update_context(file: str, section: str, data: dict) -> dict:
    """Update a section in a context file."""
    context_dir = Path(".paircoder/context")
    context_file = context_dir / file

    if not context_file.exists():
        return {"error": f"Context file not found: {file}"}

    content = context_file.read_text()
    updated = update_section(content, section, data)
    context_file.write_text(updated)

    return {"updated": True, "file": file, "section": section}
```

## 6. Configuration

Add settings for auto-update behavior:

```json
{
  "paircoder.contextAutoUpdate.enabled": true,
  "paircoder.contextAutoUpdate.debounceMs": 2000,
  "paircoder.contextAutoUpdate.ignoredPatterns": [
    "**/node_modules/**",
    "**/.git/**"
  ],
  "paircoder.contextAutoUpdate.updateOnSave": true,
  "paircoder.contextAutoUpdate.updateOnCreate": true,
  "paircoder.contextAutoUpdate.updateOnDelete": false
}
```

# Acceptance Criteria

- [ ] File watcher starts when extension activates
- [ ] Source file changes trigger state.md update
- [ ] Package.json changes trigger project.md update
- [ ] Updates are debounced (no spam on rapid saves)
- [ ] .paircoder directory is ignored
- [ ] node_modules and similar are ignored
- [ ] Configuration allows disabling auto-update
- [ ] Update failures don't crash the extension
- [ ] Recent changes section shows last 10 changes

# Dependencies

- TASK-063: VS Code extension wrapper for MCP (base extension)

# Verification

```bash
# Test auto-update functionality
1. Open VS Code with PairCoder extension
2. Enable contextAutoUpdate in settings
3. Edit and save a source file
4. Check .paircoder/context/state.md for "Recent Changes" update
5. Edit package.json
6. Check .paircoder/context/project.md for dependency update
7. Make multiple rapid saves
8. Verify only one update occurs (debouncing works)
9. Disable auto-update in settings
10. Verify saves no longer trigger updates
```

# Notes

- Consider rate limiting to prevent excessive file writes
- Large projects may need smarter filtering
- Could integrate with git to show only uncommitted changes
- Future: Use AI to generate better context summaries
- Consider adding undo capability for context updates
