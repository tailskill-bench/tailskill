#!/bin/bash

mkdir -p /logs/verifier

echo "=========================================="
echo "Installing dependencies..."
echo "=========================================="

# Install pytest for testing
pip3 install --break-system-packages pytest==8.3.4 pytest-json-report==1.5.0 --quiet || true

echo ""
echo "=========================================="
echo "Agent's solution.py:"
echo "=========================================="
cat /root/workspace/solution.py

echo ""
echo "=========================================="
echo "Running tests..."
echo "=========================================="

# Run pytest with verbose output
python3 /tests/test_outputs.py

# Check if reward.txt was created
if [ -f "/logs/verifier/reward.txt" ]; then
    echo ""
    echo "=========================================="
    echo "Test completed. Score:"
    cat /logs/verifier/reward.txt
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "WARNING: No reward.txt generated"
    echo "Writing default score: 0.0"
    echo "=========================================="
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
fi

# ═══ TailSkills: run variant-specific tests ═══
if [ -f /tests/test_tail.py ]; then
    echo "=== TailSkills variant tests ==="
    pytest /tests/test_tail.py -rA -v --tb=short 2>&1 | tee -a /logs/verifier/tail_results.txt
fi
exit 0
