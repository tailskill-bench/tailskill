FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY protein_expression.xlsx /root/protein_expression.xlsx

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages openpyxl==3.1.5 pytest uv

# ============================================
# TailSkills Variant: C4_extremes
# Inject extreme values (0, -1, -999) into Data sheet numeric cells. Tests whether skill detects outliers.
# ============================================
COPY _extremes_inject.py /tmp/_extremes_inject.py
RUN python3 /tmp/_extremes_inject.py /root/protein_expression.xlsx 5
