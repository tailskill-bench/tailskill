FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; \
    sed -i 's|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null; true

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential vim unzip wget \
    openjdk-17-jdk-headless \
    maven \
    python3 python3-pip \
    iptables iproute2 \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages pytest uv==0.9.7

# Java / Flink environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV FLINK_HOME=/opt/flink
ENV PATH="${JAVA_HOME}/bin:${FLINK_HOME}/bin:${PATH}"

COPY workspace /app/workspace
WORKDIR /app/workspace

# Copy skills to agent-specific locations
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN wget -4 https://mirrors.tuna.tsinghua.edu.cn/apache/flink/flink-1.20.3/flink-1.20.3-bin-scala_2.12.tgz || wget -4 https://dlcdn.apache.org/flink/flink-1.20.3/flink-1.20.3-bin-scala_2.12.tgz
RUN tar -xzf flink-1.20.3-bin-scala_2.12.tgz
RUN mv flink-1.20.3 ${FLINK_HOME}
RUN rm flink-1.20.3-bin-scala_2.12.tgz

RUN java -version && flink --version

# ============================================
# TailSkills Variant: D1_dns_jitter
# 50% DNS packet drop via iptables.
# ============================================
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p udp --dport 53 -m statistic --mode random --probability 0.5 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
