FROM python:3.12.8-slim

# Install Python dependencies
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip install --no-cache-dir --timeout 300 \
    graphviz==0.20.3 \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

# Install Graphviz system binary for visualization
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Copy skills for various agent runtimes
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# Copy input files to working directory
COPY script.txt /app/script.txt

# Set working directory
WORKDIR /app

# Set PYTHONPATH so agents can import skill modules
ENV PYTHONPATH="/root/.codex/skills/s1/scripts:/root/.claude/skills/s1/scripts:/root/.agents/skills/s1/scripts:/root/.opencode/skill/s1/scripts"

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]

# ============================================
# TailSkills Variant: A3_zero_width
# Insert invisible zero-width Unicode characters (U+200B, U+200C, U+200D) into dialogue text lines. Visually identical but breaks pattern matching.
# ============================================
COPY _zw_inject.py /tmp/_zw_inject.py
RUN python3 /tmp/_zw_inject.py /app/script.txt
