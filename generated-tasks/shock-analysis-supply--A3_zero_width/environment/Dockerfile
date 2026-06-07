FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY test-supply.xlsx /root/test-supply.xlsx

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && pip3 install --break-system-packages openpyxl==3.1.5 pytest uv

# TailSkills Variant: A3_zero_width — inject zero-width Unicode chars
COPY _zw_inject.py /tmp/_zw_inject.py
RUN python3 /tmp/_zw_inject.py

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
