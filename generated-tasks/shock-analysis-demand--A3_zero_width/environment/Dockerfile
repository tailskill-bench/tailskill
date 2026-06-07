FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libreoffice \
    gnumeric \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY ["test - demand.xlsx", "/root/test - demand.xlsx"]

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip3 install --break-system-packages \
    openpyxl==3.1.5 \
    pytest uv

# ============================================
# TailSkills Variant: A3_zero_width
# Inject zero-width Unicode characters into XLSX numeric cells.
# ============================================
COPY _zw_inject.py /tmp/_zw_inject.py
RUN python3 /tmp/_zw_inject.py "/root/test - demand.xlsx"
