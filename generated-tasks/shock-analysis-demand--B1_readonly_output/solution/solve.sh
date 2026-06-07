#!/bin/bash

# TailSkills: Fix output directory permissions
python3 /root/.claude/skills/s1/scripts/prepare_output.py

# Oracle solution for shock-analysis-demand task
cp "/solution/answer - demand.xlsx" "test - demand.xlsx"
