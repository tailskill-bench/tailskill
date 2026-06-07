FROM python:3.11-slim

# Create directories
# Data source: https://github.com/Azure/azure-quickstart-templates/tree/master/quickstarts/microsoft.network/virtual-wan-with-all-gateways
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

# ============================================
# TailSkills Variant: B1_readonly_output
# ============================================
RUN pip install --no-cache-dir pytest pytest-json-ctrf
RUN mkdir -p /logs/verifier
RUN chmod 555 /app/output
