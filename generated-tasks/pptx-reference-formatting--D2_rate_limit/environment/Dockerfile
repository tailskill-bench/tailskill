FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y     python3     python3-pip     python3-venv     iptables     iproute2     && rm -rf /var/lib/apt/lists/*

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip3 install --break-system-packages --no-cache-dir --timeout 300 \
    lxml==5.3.0 \
    defusedxml==0.7.1 \
    six==1.17.0 \
    rapidfuzz==3.14.3 \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

WORKDIR /root
COPY Awesome-Agent-Papers.pptx /root/

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
