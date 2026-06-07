FROM python:3.11-slim

# Create directories
# Data source: https://github.com/Azure/azure-quickstart-templates/tree/master/quickstarts/microsoft.network/virtual-wan-with-all-gateways
RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y iptables iproute2 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/data /app/output /app/environment/data

# Copy Azure deployment files
COPY data /app/environment/data

# Copy and run data generation script
COPY generate_data.py /tmp/generate_data.py
RUN python3 /tmp/generate_data.py

WORKDIR /app

COPY skills /root/.claude/skills
COPY skills /etc/claude-code/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
# Gemini
COPY skills /root/.gemini/skills

RUN pip install --no-cache-dir pytest pytest-json-ctrf
RUN mkdir -p /logs/verifier

# ============================================
# TailSkills Variant: D2_rate_limit
# Limit concurrent HTTPS connections to 3 via iptables.
# ============================================
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
