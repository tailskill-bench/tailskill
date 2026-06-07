# Dockerfile for Wyckoff Position Analysis Task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip3 install --no-cache-dir --timeout 300 \
    pymatgen==2025.10.7 \
    sympy==1.14.0 \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

# Create directories
RUN mkdir -p /root/workspace /root/cif_files

# Copy CIF files to /root/cif_files/
COPY *.cif /root/cif_files/

# Copy skills to agent-specific locations
# Claude Code
COPY skills /root/.claude/skills
# Codex
COPY skills /root/.codex/skills
# OpenCode
COPY skills /root/.opencode/skill
# Goose
COPY skills /root/.goose/skills
# Factory
COPY skills /root/.factory/skills
# Portable agents format (Goose, Amp)
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills
# Required for Harbor
COPY skills /etc/claude-code/.claude/skills

# Set working directory
WORKDIR /root

# Default command
CMD ["/bin/bash"]

# ============================================
# TailSkills Variant: B1_readonly_output
# Set the output directory to read-only (chmod 555). Tests whether skill uses os.makedirs + os.chmod defense.
# ============================================
RUN mkdir -p /logs/verifier
RUN chmod 555 /root/workspace
