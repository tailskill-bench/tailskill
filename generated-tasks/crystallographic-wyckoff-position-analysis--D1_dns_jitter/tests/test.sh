#!/bin/bash
mkdir -p /logs/verifier
python3 /tests/test_outputs.py
if [ -f /tests/test_tail.py ]; then
    echo "=== TailSkills variant tests ==="
    python3 /tests/test_tail.py 2>&1 | tee -a /logs/verifier/tail_results.txt
fi
exit 0
