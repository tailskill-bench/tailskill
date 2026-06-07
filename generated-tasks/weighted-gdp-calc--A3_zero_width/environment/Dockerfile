FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, LibreOffice, and gnumeric for Excel formula evaluation
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libreoffice \
    gnumeric \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /root

# Copy the Excel file to /root/
COPY gdp.xlsx /root/gdp.xlsx

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

# Install Python dependencies
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages openpyxl==3.1.5 pytest

# ============================================
# TailSkills Variant: A3_zero_width
# Insert invisible zero-width Unicode characters (U+200B, U+200C, U+200D) into 3% of numeric field values. Visually identical but breaks float parsing.
# ============================================
COPY _zw_inject.py /tmp/_zw_inject.py
RUN python3 /tmp/_zw_inject.py /root/gdp.xlsx 5
