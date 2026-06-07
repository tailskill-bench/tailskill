FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip libreoffice iptables iproute2 && rm -rf /var/lib/apt/lists/*
WORKDIR /root
COPY input.pptx /root/input.pptx
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED
RUN pip3 install --no-cache-dir --timeout 300 python-pptx==1.0.2 pillow==11.1.0 defusedxml==0.7.1 openpyxl==3.1.5 pandas==2.2.3 pytest==8.4.1 pytest-json-ctrf==0.3.5
RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
