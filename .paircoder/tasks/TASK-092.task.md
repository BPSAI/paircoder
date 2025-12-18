---
id: TASK-092
title: Docker sandbox runner
plan: plan-2025-12-sprint-15-security-sandboxing
type: feature
priority: P1
complexity: 50
status: done
sprint: sprint-15
tags:
- security
- docker
- sandbox
- isolation
depends_on:
- TASK-090
---

# Objective

Execute agent work in isolated Docker containers to prevent system-wide damage from malicious or buggy commands.

# Implementation Plan

1. Create sandbox Docker image:
   ```dockerfile
   FROM python:3.12-slim

   # Install common dev tools
   RUN apt-get update && apt-get install -y git nodejs npm

   # Create non-root user
   RUN useradd -m sandbox
   USER sandbox

   # Copy project (read-only mount)
   WORKDIR /workspace
   ```

2. Create SandboxRunner class:
   ```python
   class SandboxRunner:
       def __init__(self, workspace: Path, config: SandboxConfig):
           self.workspace = workspace
           self.config = config

       def run_command(self, command: str) -> SandboxResult:
           """Run command in isolated container."""
           container = self.create_container()
           try:
               result = container.exec_run(command)
               return SandboxResult(
                   exit_code=result.exit_code,
                   stdout=result.output,
                   changes=self.detect_changes()
               )
           finally:
               container.remove()
   ```

3. Implement change detection:
   - Mount workspace as volume
   - Track file changes during execution
   - Allow/deny changes based on policy

4. Create sandbox config:
   ```yaml
   sandbox:
     enabled: true
     image: paircoder/sandbox:latest
     memory_limit: 2g
     cpu_limit: 2
     network: none  # No network by default
     mounts:
       - source: .
         target: /workspace
         readonly: false
     env_passthrough:
       - GITHUB_TOKEN
       - TRELLO_API_KEY
   ```

# Acceptance Criteria

- [ ] Docker sandbox image builds successfully
- [ ] Commands run in isolated container
- [ ] File changes captured and reviewable
- [ ] Network isolation works (no external calls by default)
- [ ] Resource limits enforced (memory, CPU)
- [ ] Can enable network for specific commands
- [ ] Changes can be applied or discarded

# Files to Create/Modify

- `tools/cli/bpsai_pair/security/sandbox.py` (new)
- `tools/cli/bpsai_pair/security/Dockerfile` (new)
- `.paircoder/security/sandbox.yaml` (new)
- `tests/test_security_sandbox.py` (new)