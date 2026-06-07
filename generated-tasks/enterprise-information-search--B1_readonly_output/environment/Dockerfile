FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Configure pip mirror
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# Pre-install packages
RUN pip3 install --break-system-packages --timeout 300 \
    uv==0.9.7 \
    pytest==8.4.1

# Copy data files
COPY DATA /root/DATA
COPY question.txt /root/question.txt

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills
COPY skills /root/.factory/skills

# ============================================
# TailSkills Variant: B1_readonly_output
# Set the output directory to read-only (chmod 555). Tests whether skill uses os.makedirs + os.chmod defense.
# ============================================
RUN mkdir -p /root/output && chmod 555 /root/output && chmod 555 /root
