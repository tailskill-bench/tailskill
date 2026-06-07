FROM python:3.11-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip install --no-cache-dir --timeout 300 \
    pandas==2.2.3 \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5 \
    uv==0.9.7

# Create standard folders
RUN mkdir -p /app/data /app/output

# Copy skills to ALL agent paths (keep your existing behavior)
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

#TRY THIS IF YOUR AGENT CAN NOT FIND THE SKILLS PATH
RUN mkdir -p /etc/claude-code/.claude/skills
COPY skills/ /etc/claude-code/.claude/skills/

# Copy case data into /app/data (Dockerfile will copy from your repo's environment/data)
# IMPORTANT: keep this folder in your build context
COPY data/ /app/data/

# Default command (kept similar to your original)
CMD ["/bin/bash"]

# ============================================
# TailSkills Variant: B1_readonly_output
# Set the output directory to read-only (chmod 555). Tests whether skill uses os.makedirs + os.chmod defense.
# ============================================
RUN mkdir -p /logs/verifier
RUN chmod 555 /app/output
