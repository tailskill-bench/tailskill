FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for PDF processing and OCR
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    poppler-utils \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

# Copy input files to /root/input/ directory
COPY input/input.pdf /root/input/input.pdf
COPY input/input.txt /root/input/input.txt

# Copy skills to ALL agent paths for different agent frameworks
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills

# Install Python dependencies for PDF processing and OCR
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 install --break-system-packages --no-cache-dir --timeout 300 \
    PyMuPDF==1.24.10 \
    pypdf==5.1.0 \
    reportlab==4.2.5 \
    Pillow==10.4.0 \
    pytest==8.4.1 pytest-json-ctrf==0.3.5

# ============================================
# TailSkills Variant: B1_readonly_output
# Set the output directory to read-only (chmod 555). Tests whether skill uses os.makedirs + os.chmod defense.
# ============================================
RUN mkdir -p /root/output && chmod 555 /root/output && chmod 555 /root
