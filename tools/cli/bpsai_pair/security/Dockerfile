# PairCoder Containment Image
# Minimal environment for running Claude Code in contained autonomy mode

FROM python:3.12-slim-bookworm

LABEL maintainer="BPS AI Software"
LABEL org.opencontainers.image.source="https://github.com/BPSAI/paircoder"
LABEL org.opencontainers.image.description="Contained autonomy environment with Claude Code"

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    git \
    iptables \
    dnsutils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user for safer execution
RUN useradd -m -s /bin/bash sandbox \
    && mkdir -p /workspace \
    && chown sandbox:sandbox /workspace

# Switch to non-root user
USER sandbox
WORKDIR /workspace

# Skip update checks inside container
ENV CLAUDE_CODE_SKIP_UPDATE_CHECK=1

CMD ["bash"]
