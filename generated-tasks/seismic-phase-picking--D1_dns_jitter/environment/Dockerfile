# Dockerfile for running SeisBench inference
# Supports CPU and NVIDIA GPU execution

FROM python:3.11-slim-bookworm

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# Set working directory
WORKDIR /root

# Install runtime libraries required by ObsPy for XML parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    curl \
    iptables \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Pre-install uv and pytest to speed up test.sh
RUN curl -x http://host.docker.internal:7897 -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Pre-install seisbench + obspy (D1 dns_jitter: avoid runtime pip install under DNS drop)
RUN pip install --no-cache-dir --timeout 120 seisbench==0.10.2 obspy pandas numpy || \
    pip install --no-cache-dir --timeout 120 seisbench==0.10.2 obspy pandas numpy

# Copy data files
COPY data /root/data

# Copy skills to ALL agent paths (required)
COPY skills /root/.claude/skills
COPY skills /etc/claude-code/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills

RUN mkdir -p /root/output

# ============================================
# TailSkills Variant: D1_dns_jitter
# 50% DNS packet drop via iptables. Tests whether agent can handle intermittent DNS resolution failures.
# ============================================
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
