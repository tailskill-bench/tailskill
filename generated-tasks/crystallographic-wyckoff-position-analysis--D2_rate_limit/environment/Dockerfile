FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential iptables iproute2 && rm -rf /var/lib/apt/lists/*
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --no-cache-dir --timeout 300 pymatgen==2025.10.7 sympy==1.14.0 pytest==8.4.1 pytest-json-ctrf==0.3.5
RUN mkdir -p /root/workspace /root/cif_files
COPY *.cif /root/cif_files/
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
COPY skills /etc/claude-code/.claude/skills
WORKDIR /root
CMD ["/bin/bash"]
# TailSkills Variant: D2_rate_limit
RUN echo '#!/bin/bash\niptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' > /usr/local/bin/rate_limit.sh && chmod +x /usr/local/bin/rate_limit.sh
RUN echo '#!/bin/bash\n/usr/local/bin/rate_limit.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
