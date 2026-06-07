#!/bin/bash
set -e

# >>> TailSkills: 安装缺失依赖 <<<
pip install --no-cache-dir scikit-learn==1.2.2 2>/dev/null

cd /root
python3 /solution/solve.py
