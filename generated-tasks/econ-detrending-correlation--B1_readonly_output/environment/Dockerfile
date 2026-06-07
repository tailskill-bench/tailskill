FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Configure pip mirror for faster downloads
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# Install python packages with pinned versions
RUN pip install --no-cache-dir \
    pandas==2.2.3 \
    numpy==1.26.4 \
    openpyxl==3.1.5 \
    xlrd==2.0.1 \
    scipy==1.14.1 \
    statsmodels==0.14.4 \
    uv==0.9.7 \
    pytest==8.4.1

WORKDIR /root

# Copy data files
COPY CPI.xlsx /root/
COPY ERP-2025-table10.xls /root/
COPY ERP-2025-table12.xls /root/

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
# Goose/Amp (portable agents format)
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills

# ============================================
# TailSkills Variant: B1_readonly_output
# Set the output directory to read-only (chmod 555). Tests whether skill uses os.makedirs + os.chmod defense.
# ============================================
RUN mkdir -p /root/output && chmod 555 /root/output && chmod 555 /root
