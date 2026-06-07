#!/bin/bash

# Install test dependencies and run the tests.
# Copied to /tests/test.sh and run from the working directory.

# Ensure logs directory exists
mkdir -p /logs/verifier

# Copy PDFs to verifier folder for manual inspection
if [ -f /root/sc100-filled.pdf ]; then
    cp /root/sc100-filled.pdf /logs/verifier/sc100-filled.pdf
    echo "Copied filled PDF to /logs/verifier/sc100-filled.pdf"
fi

if [ -f /root/sc100-blank.pdf ]; then
    cp /root/sc100-blank.pdf /logs/verifier/sc100-blank.pdf
    echo "Copied blank PDF to /logs/verifier/sc100-blank.pdf"
fi

# Install test-only dependencies (PDF libraries already in Dockerfile)
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install --break-system-packages \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

# Run tests with CTRF report
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v

PYTEST_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
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
