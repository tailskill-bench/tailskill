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
# TailSkills Variant: A3_zero_width
# Insert invisible zero-width Unicode characters (U+200B, U+200C, U+200D) into 3% of numeric field values. Visually identical but breaks float parsing.
# ============================================
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py zero_width /root/CPI.xlsx 1
