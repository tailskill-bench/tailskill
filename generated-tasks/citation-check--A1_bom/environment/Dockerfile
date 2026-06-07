FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and essential tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /root

# Install Python dependencies for citation verification
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages \
    requests==2.32.3 \
    bibtexparser==1.4.2 \
    uv==0.9.7

# Copy the test.bib file to /root
COPY test.bib /root/test.bib

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

# ============================================
# TailSkills Variant: A1_bom
# Inject UTF-8 BOM (byte order mark) at the start of CSV/text input files. Tests whether skill uses encoding='utf-8-sig' parameter.
# ============================================
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py bom /root/test.bib
