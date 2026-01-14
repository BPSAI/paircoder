# Subagent Invocation Guide

> How to use and create specialized AI agents in PairCoder

## Overview

Subagents are specialized AI role definitions that guide Claude Code's behavior for specific types of tasks. They're defined in `.claude/agents/` and automatically loaded by Claude Code when using the Task tool.

Each subagent has:
- A specific role and expertise area
- A restricted set of tools
- Behavioral guidelines and constraints
- Read-only mode (cannot modify files)

## Available Subagents

| Agent | File | Purpose |
|-------|------|---------|
| **Planner** | `.claude/agents/planner.md` | Strategic planning, architecture decisions, task breakdown |
| **Reviewer** | `.claude/agents/reviewer.md` | Code review, quality checks, best practices |
| **Security** | `.claude/agents/security.md` | Pre-execution security gating, SOC2 compliance |
| **Security Auditor** | `.claude/agents/security-auditor.md` | Security scanning and reporting |

## How Subagents Work

```
1. Claude Code reads agent definitions from .claude/agents/
2. User invokes Task tool with subagent_type parameter
3. Agent definition is injected into the subagent's system prompt
4. Subagent executes with restricted tools and follows its guidelines
5. Results return to the parent conversation
```

### Agent Tool Restrictions

Subagents operate in **read-only mode** by default:

| Agent | Tools Available |
|-------|-----------------|
| Planner | Read, Grep, Glob, Bash |
| Reviewer | Read, Grep, Glob, Bash |
| Security | Read, Grep, Glob, Bash |

None of these agents can use Write, Edit, or NotebookEdit tools.

## Invoking Subagents

### From Claude Code (Task Tool)

Claude Code uses the Task tool with `subagent_type` to invoke agents:

```json
{
  "subagent_type": "reviewer",
  "prompt": "Review the changes in src/auth.py for security issues",
  "description": "Security review"
}
```

### When to Use Each Agent

| Situation | Agent | Why |
|-----------|-------|-----|
| Planning a new feature | `planner` | Designs solutions with trade-offs |
| After writing code | `reviewer` | Catches bugs and style issues |
| Before git commit | `security` | Blocks credentials and dangerous patterns |
| Security audit needed | `security-auditor` | Comprehensive security scan |

### Example: Proactive Review After Changes

Claude Code should automatically invoke the reviewer after significant code changes:

```
User: "Add authentication to the API"
Claude: [writes authentication code]
Claude: "Let me review these changes for quality..."
Claude: [invokes reviewer agent]
Reviewer: [returns feedback]
Claude: [addresses any issues found]
```

## Agent File Structure

Each agent definition file follows this structure:

```markdown
---
name: agent-name
description: Brief description shown in agent listings
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
skills: optional-skill-reference
---

# Agent Name

## Your Role
What the agent does and its expertise area.

## What You Do NOT Do
Explicit constraints on agent behavior.

## Process
Step-by-step workflow the agent follows.

## Output Format
How the agent structures its responses.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Agent identifier (used in `subagent_type`) |
| `description` | Yes | Brief description for listings |
| `tools` | Yes | Comma-separated list of available tools |
| `model` | No | Preferred model (sonnet, opus, haiku) |
| `permissionMode` | No | Permission level (plan = read-only) |
| `skills` | No | Associated skills reference |

## Creating Custom Subagents

### 1. Create the Agent File

Create a new file in `.claude/agents/`:

```bash
touch .claude/agents/my-agent.md
```

### 2. Add Frontmatter

```yaml
---
name: my-agent
description: Describe what this agent specializes in
tools: Read, Grep, Glob
model: sonnet
permissionMode: plan
---
```

### 3. Write Agent Instructions

```markdown
# My Agent

## Your Role
You are a specialist in [domain]. You help with:
- Task 1
- Task 2
- Task 3

## What You Do NOT Do
- Do not modify files
- Do not execute destructive commands
- Do not [other constraints]

## Process
1. First step
2. Second step
3. Third step

## Output Format
Structure your response as:
- Summary
- Findings
- Recommendations
```

### Example: Testing Agent

```markdown
---
name: tester
description: Test execution and analysis specialist
tools: Read, Bash, Grep
model: haiku
permissionMode: plan
---

# Testing Agent

## Your Role
You execute test suites and analyze results:
- Run appropriate test commands
- Analyze failures
- Provide actionable summaries

## What You Do NOT Do
- Modify test files
- Skip failing tests
- Run tests with --force flags

## Process
1. Identify test framework (pytest, jest, etc.)
2. Run tests with verbose output
3. Analyze any failures
4. Report summary with recommendations

## Output Format
## Test Results

**Status**: PASS / FAIL
**Total**: X tests
**Passed**: Y
**Failed**: Z

### Failures (if any)
- test_name: reason for failure

### Recommendations
- How to fix failures
```

## Containment Mode Considerations

In **contained autonomy mode**, agent definition files are protected:

### Protected Paths
```
.claude/agents/     → READ-ONLY (Tier 2)
.claude/commands/   → READ-ONLY (Tier 2)
.claude/skills/     → READ-ONLY (Tier 2)
```

### Why Agents Are Protected

Without containment protection, Claude could:
1. Read the security agent definition
2. Edit it to remove constraints
3. Invoke the modified agent to bypass security

With containment protection, step 2 fails:
```
ContainmentViolationError: Cannot write to .claude/agents/security.md
  Path is protected (read-only in containment mode)
```

### Modifying Agents in Containment Mode

To modify agent definitions while in containment mode:

1. **Exit containment mode** - Run `bpsai-pair contained-auto` without the `-y` flag and decline
2. **Make your changes** - Edit the agent files normally
3. **Re-enter containment mode** - Run `bpsai-pair contained-auto` again

## Agent Invocation Patterns

### Sequential Agent Workflow

```
1. Planner designs the approach
2. User/Claude implements
3. Reviewer checks the code
4. Security validates before commit
```

### Parallel Agent Workflow

Multiple agents can be invoked simultaneously:

```json
[
  {"subagent_type": "reviewer", "prompt": "Review auth.py", "description": "Auth review"},
  {"subagent_type": "security", "prompt": "Check auth.py for vulnerabilities", "description": "Security check"}
]
```

### Conditional Agent Invocation

Agents should be invoked proactively based on context:

| Context | Invoke |
|---------|--------|
| New feature request | Planner |
| After code changes | Reviewer |
| Before `git commit` | Security |
| Complex architecture question | Planner |
| PR review requested | Reviewer |

## Troubleshooting

### Agent Not Found

```
Error: Agent 'my-agent' not found
```

**Solution**: Ensure the file exists at `.claude/agents/my-agent.md` with correct frontmatter.

### Agent Tools Limited

If an agent can't perform an action, check the `tools` field in frontmatter:

```yaml
# Limited
tools: Read, Grep

# More capable
tools: Read, Grep, Glob, Bash
```

### Can't Modify Agent in Containment

```
ContainmentViolationError: Cannot write to .claude/agents/
```

**By design**. Exit containment mode to modify agents:
```bash
# Check current mode
bpsai-pair containment status

# Exit and re-enter without containment
# (or edit agents outside of containment session)
```

### Agent Ignoring Instructions

Ensure agent instructions are clear and specific:
- Use "Do NOT" for prohibitions
- Use numbered steps for processes
- Provide output format examples

## Best Practices

### Writing Agent Instructions

1. **Be specific** - Vague instructions lead to inconsistent behavior
2. **Show examples** - Include output format examples
3. **List constraints explicitly** - "What You Do NOT Do" section
4. **Keep focused** - One area of expertise per agent

### Using Agents Effectively

1. **Use the right agent** - Planner for planning, Reviewer for reviews
2. **Provide context** - Include relevant file paths and background
3. **Review agent output** - Agents advise, humans decide
4. **Iterate** - Ask follow-up questions if needed

### Security Considerations

1. **Don't give Write access** - Agents should advise, not modify
2. **Use containment mode** - Protects agent definitions from tampering
3. **Audit agent changes** - Review any modifications to `.claude/agents/`

## See Also

- [Contained Autonomy Mode](CONTAINED_AUTONOMY.md) - How containment protects agents
- [Claude Code Integration](CLAUDE_CODE_INTEGRATION.md) - How PairCoder integrates with Claude Code
