FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl wget poppler-utils && rm -rf /var/lib/apt/lists/*
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED
RUN pip3 install --no-cache-dir --timeout 300 pymupdf==1.24.0 pdfplumber==0.11.0 pypdf==4.0.0 pytest==8.4.1 pytest-json-ctrf==0.3.5
COPY paper1.pdf paper2.pdf paper3.pdf /root/
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
WORKDIR /root
# TailSkills Variant: E1_missing_dep
RUN pip3 uninstall -y pymupdf pdfplumber pypdf
