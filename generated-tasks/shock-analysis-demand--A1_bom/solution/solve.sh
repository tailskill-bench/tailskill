#!/bin/bash

# TailSkills: Strip BOM from CSV sidecar files
python3 /root/.claude/skills/s1/scripts/clean_data.py /root

# Oracle solution for shock-analysis-demand task
cp "/solution/answer - demand.xlsx" "test - demand.xlsx"
