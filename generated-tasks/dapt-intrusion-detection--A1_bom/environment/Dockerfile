FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for network analysis
RUN pip3 install --break-system-packages \
    scapy==2.5.0 \
    pandas==2.2.2 \
    numpy==1.26.4

WORKDIR /root

# Copy data files
# Data source note: packets.pcap is an anonymized enterprise traffic capture
# provided by the task author; provenance is not publicly documented.
COPY packets.pcap /root/packets.pcap
COPY network_stats_template.csv /root/network_stats.csv

# Copy skills
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
COPY skills /root/skills

# ============================================
# TailSkills Variant: A1_bom
# Inject UTF-8 BOM (byte order mark) at the start of CSV/text input files. Tests whether skill uses encoding='utf-8-sig' parameter.
# ============================================
COPY _tail_inject.py /tmp/_tail_inject.py
RUN python3 /tmp/_tail_inject.py bom /root/network_stats.csv
