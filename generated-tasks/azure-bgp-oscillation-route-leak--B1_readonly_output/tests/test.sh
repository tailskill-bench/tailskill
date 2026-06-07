#!/bin/bash

mkdir -p /logs/verifier

pip install --no-cache-dir pytest pytest-json-ctrf >/dev/null 2>&1

python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v | tee /logs/verifier/test_output.log

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
