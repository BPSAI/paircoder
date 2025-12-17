# PairCoder Sandbox Image
# Provides isolated environment for running untrusted commands
#
# Build: docker build -t paircoder/sandbox:latest -f Dockerfile .
# Usage: Used by SandboxRunner for isolated command execution

FROM python:3.12-slim

LABEL maintainer="PairCoder"
LABEL description="Isolated sandbox environment for PairCoder command execution"

# Install common development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    nodejs \
    npm \
    jq \
    tree \
    less \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/*

# Create non-root sandbox user
RUN useradd -m -s /bin/bash sandbox \
    && mkdir -p /workspace \
    && chown sandbox:sandbox /workspace

# Install common Python packages
RUN pip install --no-cache-dir \
    pytest \
    ruff \
    black \
    mypy \
    requests \
    pyyaml

# Switch to non-root user
USER sandbox

# Set working directory
WORKDIR /workspace

# Default command - keep container running
CMD ["sleep", "infinity"]
