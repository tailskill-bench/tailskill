FROM python:3.10-slim

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

ENV DEBIAN_FRONTEND=noninteractive
ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    git \
    unzip \
    iptables \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb bookworm main" | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends trivy && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Download Trivy DB directly from HF mirror (bypass git-lfs)
RUN mkdir -p /root/.cache/trivy && \
    wget -q "https://hf-mirror.com/datasets/zodi1121/skillbench-software-db/resolve/main/db.zip" -O /tmp/db.zip && \
    unzip /tmp/db.zip -d /root/.cache/trivy && \
    ln -s /root/.cache/trivy /root/trivy-cache && \
    rm /tmp/db.zip

# Copy test data files
COPY package-lock.json /root/

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# Pre-install test dependencies (before D1 iptables rules take effect)
RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

# ============================================
# TailSkills Variant: D1_dns_jitter
# Apply 50% random DNS packet drop to test network retry robustness.
# ============================================
RUN echo '#!/bin/bash\niptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' > /usr/local/bin/dns_jitter.sh && \
    chmod +x /usr/local/bin/dns_jitter.sh
RUN echo '#!/bin/bash\n/usr/local/bin/dns_jitter.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
    chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
