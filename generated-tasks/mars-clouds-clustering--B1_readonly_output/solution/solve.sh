#!/bin/bash
set -e

# The solution directory is mounted at /solution by Harbor
cd /root

# >>> TailSkills: 修复输出目录权限 <<<
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/pareto_frontier.csv

python3 /solution/solve.py
