#!/bin/bash
pip3 install -q pytest
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -rA -v > /logs/verifier/test-stdout.txt 2>&1
if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
# ═══ TailSkills: run variant-specific tests ═══
if [ -f /tests/test_tail.py ]; then
    echo "=== TailSkills variant tests ==="
    pytest /tests/test_tail.py -rA -v --tb=short 2>&1 | tee -a /logs/verifier/tail_results.txt
fi
exit 0
