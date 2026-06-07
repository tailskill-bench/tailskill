FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV http_proxy=http://host.docker.internal:7897
ENV https_proxy=http://host.docker.internal:7897

RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv libreoffice \
    iptables iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY test-supply.xlsx /root/test-supply.xlsx

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip3 install --break-system-packages openpyxl==3.1.5 pytest uv

# ============================================
# TailSkills Variant: D1_dns_jitter
# Apply 50% random DNS packet drop to test network retry robustness.
# ============================================
RUN echo '#!/bin/bash\niptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' > /usr/local/bin/dns_jitter.sh && \
    chmod +x /usr/local/bin/dns_jitter.sh
RUN echo '#!/bin/bash\n/usr/local/bin/dns_jitter.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
    chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
