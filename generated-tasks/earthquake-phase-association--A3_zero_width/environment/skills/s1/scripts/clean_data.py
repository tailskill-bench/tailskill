#!/usr/bin/env python3
"""Remove zero-width characters from stations.csv"""
import unicodedata
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root/data/stations.csv"
with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

cleaned = ''.join(
    ch for ch in content
    if unicodedata.category(ch) not in ('Cf', 'Cc') or ch in ('\n', '\r', '\t')
)
with open(target, 'w', encoding='utf-8') as f:
    f.write(cleaned)
print(f"Cleaned zero-width chars from {target}")
