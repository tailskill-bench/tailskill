FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /root
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED
RUN pip3 install --timeout 300 numpy==1.26.4 scipy==1.11.4 cvxpy==1.4.2 pytest==8.4.1 pytest-json-ctrf==0.3.5
COPY network.json /root/network.json
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skills
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
# TailSkills Variant: E1_missing_dep
RUN pip3 uninstall -y cvxpy
