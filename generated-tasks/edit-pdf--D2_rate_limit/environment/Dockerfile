FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    poppler-utils \
    curl \
    tesseract-ocr \
    iptables \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY input/input.pdf /root/input/input.pdf
COPY input/input.txt /root/input/input.txt

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages --no-cache-dir --timeout 300 \
    PyMuPDF==1.24.10 \
    pypdf==5.1.0 \
    reportlab==4.2.5 \
    Pillow==10.4.0 \
    pytest==8.4.1 pytest-json-ctrf==0.3.5

RUN echo '#!/bin/bash' > /usr/local/bin/network_fault.sh && echo 'iptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' >> /usr/local/bin/network_fault.sh && chmod +x /usr/local/bin/network_fault.sh
RUN echo '#!/bin/bash' > /usr/local/bin/entrypoint_wrapper.sh && echo '/usr/local/bin/network_fault.sh' >> /usr/local/bin/entrypoint_wrapper.sh && echo 'exec "$@"' >> /usr/local/bin/entrypoint_wrapper.sh && chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
CMD ["/bin/bash"]
