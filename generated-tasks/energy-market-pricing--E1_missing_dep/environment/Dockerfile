FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Configure pip mirror
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# Pre-install packages (solve.sh also installs but this speeds up)
RUN pip3 install --break-system-packages --timeout 300 \
    numpy==1.26.4 \
    scipy==1.11.4 \
    cvxpy==1.4.2 \
    uv==0.9.7 \
    pytest==8.4.1

# Copy data files
COPY network.json /root/network.json

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# ============================================
# TailSkills Variant: E1_missing_dep
# Uninstall cvxpy to test whether agent can recover from missing dependency.
# ============================================
RUN pip3 uninstall -y --break-system-packages cvxpy
