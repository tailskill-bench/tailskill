FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || sed -i "s|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g" /etc/apt/sources.list 2>/dev/null || true

RUN apt-get update && apt-get install -y \
    curl git vim iptables iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pandas==2.2.3 numpy==1.26.4 geopandas==1.0.1 shapely==2.0.6 pyproj==3.7.0

RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /root

COPY earthquakes_2024.json /root/earthquakes_2024.json
COPY PB2002_plates.json /root/PB2002_plates.json
COPY PB2002_boundaries.json /root/PB2002_boundaries.json

COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# TailSkills Variant: D2_rate_limit
RUN echo '#!/bin/bash\niptables -A OUTPUT -p tcp --dport 443 -m connlimit --connlimit-above 3 -j DROP 2>/dev/null || true' > /usr/local/bin/rate_limit.sh && \
    chmod +x /usr/local/bin/rate_limit.sh
RUN echo '#!/bin/bash\n/usr/local/bin/rate_limit.sh\nexec "$@"' > /usr/local/bin/entrypoint_wrapper.sh && \
    chmod +x /usr/local/bin/entrypoint_wrapper.sh
ENTRYPOINT ["/usr/local/bin/entrypoint_wrapper.sh"]
