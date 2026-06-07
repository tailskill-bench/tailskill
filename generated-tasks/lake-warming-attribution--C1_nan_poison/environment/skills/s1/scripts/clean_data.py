#!/usr/bin/env python3
"""Replace NaN/Inf values with column median — proper error handling."""
import csv, sys, math

filepath = sys.argv[1] if len(sys.argv) > 1 else "/root/data/water_temperature.csv"
col_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 1

def parse(s):
    s = str(s).strip()
    if s in ('', 'NaN', 'nan', 'None', 'none', 'Inf', 'inf', '-Inf', '-inf'):
        return None
    try:
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except:
        return None

with open(filepath, 'r') as f:
    rows = list(csv.reader(f))

valid = [parse(r[col_idx]) for r in rows[1:] if col_idx < len(r)]
valid = [v for v in valid if v is not None]
median = sorted(valid)[len(valid)//2]

count = 0
for r in rows[1:]:
    if col_idx < len(r) and parse(r[col_idx]) is None:
        r[col_idx] = str(median)
        count += 1

with open(filepath, 'w', newline='') as f:
    csv.writer(f).writerows(rows)
print(f"Replaced {count} NaN/Inf values with median {median:.4f}")
