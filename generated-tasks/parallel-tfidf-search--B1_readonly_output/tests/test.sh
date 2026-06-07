#!/bin/bash

# Ensure logs directory exists
mkdir -p /logs/verifier
mkdir -p /root/logs

# Install test dependencies
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip install pytest==8.4.1 pytest-json-ctrf==0.3.5 >/dev/null 2>&1

# Run pytest
python -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py \
    -rA -v | tee /logs/verifier/test_output.log

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
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
