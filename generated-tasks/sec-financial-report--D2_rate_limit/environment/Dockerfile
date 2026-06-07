FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Use Chinese mirror for faster downloads
RUN sed -i 's|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; \
    sed -i 's|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; true

# Install Python, pip, wget, unzip, iptables for rate limiting
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    unzip \
    iptables \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /root

COPY 13f-2025-q2.zip /root/13f-2025-q2.zip
COPY 13f-2025-q3.zip /root/13f-2025-q3.zip
RUN mkdir /root/2025-q2
RUN mkdir /root/2025-q3

RUN unzip /root/13f-2025-q2.zip -d /root
RUN mv /root/01JUN2025-31AUG2025_form13f/* /root/2025-q2

RUN unzip /root/13f-2025-q3.zip -d /root/2025-q3

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /etc/claude-code/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip3 install --break-system-packages --timeout 300 pandas==2.3.3 rapidfuzz==3.14.3 pytest==8.4.1

RUN mkdir -p /logs/verifier /root/logs

# ============================================
# TailSkills Variant: D2_rate_limit
# Limit concurrent HTTPS connections to 3 to test API rate limit handling.
# ============================================
RUN echo '#!/bin/bash\niptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' > /usr/local/bin/rate_limit.sh && \
    chmod +x /usr/local/bin/rate_limit.sh
RUN echo '#!/bin/bash\n/usr/local/bin/rate_limit.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
    chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
