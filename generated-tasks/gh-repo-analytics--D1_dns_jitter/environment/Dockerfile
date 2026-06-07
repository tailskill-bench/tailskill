FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y \
    python3 python3-pip curl jq iptables iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# GH_TOKEN is passed via docker-compose.yaml environment variable

COPY skills /root/.claude/skills
COPY skills /etc/claude-code/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# ============================================
# TailSkills Variant: D1_dns_jitter
# Apply 50% random DNS packet drop to test network retry robustness.
# ============================================
RUN echo '#!/bin/bash\niptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' > /usr/local/bin/dns_jitter.sh && \
    chmod +x /usr/local/bin/dns_jitter.sh
RUN echo '#!/bin/bash\n/usr/local/bin/dns_jitter.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
    chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
