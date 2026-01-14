# PairCoder Containment Image

Docker image for running Claude Code in contained autonomy mode with filesystem and network restrictions.

## Quick Start

```bash
# The image is pulled automatically when needed
bpsai-pair contained-auto
```

## What This Image Provides

- **Claude Code CLI** pre-installed
- **iptables** for network allowlist enforcement  
- **Python 3.12** runtime
- **Non-root user** for safer execution

## Manual Pull

```bash
docker pull bpsai/paircoder-containment:latest

# Or specific version
docker pull bpsai/paircoder-containment:2.9.0
```

## Usage

This image is used automatically by `bpsai-pair contained-auto` when strict containment mode is enabled.

```yaml
# config.yaml
containment:
  enabled: true
  mode: strict
```

## Security Features

When running in this container:

1. **Read-only mounts** - Enforcement code cannot be modified (OS-enforced)
2. **Network allowlist** - Only configured domains are accessible
3. **Non-root execution** - Container runs as unprivileged user

## Building Locally

```bash
cd tools/cli/bpsai_pair/security
docker build -t paircoder/containment:latest -f Dockerfile.containment .
```

## Links

- [PairCoder GitHub](https://github.com/BPSAI/paircoder)
- [Containment Documentation](https://github.com/BPSAI/paircoder/blob/main/docs/CONTAINED_AUTONOMY.md)
