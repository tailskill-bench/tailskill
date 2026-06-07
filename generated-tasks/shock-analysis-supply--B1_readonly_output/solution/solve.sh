#!/bin/bash
# Oracle solution for shock-analysis-supply B1_readonly_output variant
python3 /root/.claude/skills/s1/scripts/prepare_output.py
cp "/solution/answer-supply.xlsx" "test-supply.xlsx"
