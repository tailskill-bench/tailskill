#!/bin/bash

# TailSkills: Strip zero-width characters from XLSX
python3 /root/.claude/skills/s1/scripts/clean_data.py "/root/test - demand.xlsx"

# Oracle solution for shock-analysis-demand task
cp "/solution/answer - demand.xlsx" "test - demand.xlsx"
