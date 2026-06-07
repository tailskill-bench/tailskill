#!/usr/bin/env python3
"""Strip BOM from stations.csv"""
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root/data/stations.csv"
with open(target, 'rb') as f:
    raw = f.read()
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]
with open(target, 'wb') as f:
    f.write(raw)
print(f"Cleaned BOM from {target}")
