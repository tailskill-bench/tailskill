#!/bin/bash

# Ensure logs directory exists
mkdir -p /logs/verifier

# Export results.pptx to verifier folder for debugging
if [ -f "/root/results.pptx" ]; then
    echo "Exporting results.pptx to verifier folder..."
    cp /root/results.pptx /logs/verifier/results.pptx 2>/dev/null || true
fi

# Install test dependencies
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 >/dev/null 2>&1

# Run tests
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# ═══ TailSkills: run variant-specific tests ═══
if [ -f /tests/test_tail.py ]; then
    echo "=== TailSkills variant tests ==="
    pytest /tests/test_tail.py -rA -v --tb=short 2>&1 | tee -a /logs/verifier/tail_results.txt
fi
exit 0
