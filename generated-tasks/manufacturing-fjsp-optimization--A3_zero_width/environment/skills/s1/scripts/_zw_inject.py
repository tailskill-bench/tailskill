#!/usr/bin/env python3
"""Inject zero-width Unicode chars into downtime.csv and instance.txt."""
import csv, random, os

random.seed(42)
ZW_CHARS = ['\u200b', '\u200c', '\u200d', '\ufeff']

DATA_DIR = "/app/data"

# Inject into downtime.csv text representation
dt_path = os.path.join(DATA_DIR, "downtime.csv")
with open(dt_path, "r", encoding="utf-8") as f:
    content = f.read()

# Insert zero-width chars at random positions in header and data lines
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    if line.strip():
        pos = random.randint(0, max(0, len(line) - 1))
        zw = random.choice(ZW_CHARS)
        new_lines.append(line[:pos] + zw + line[pos:])
    else:
        new_lines.append(line)

with open(dt_path, "w", encoding="utf-8", newline="") as f:
    f.write('\n'.join(new_lines))
print(f"[zw_inject] Injected zero-width chars into {dt_path}")

# Inject into instance.txt - add zero-width chars between tokens
inst_path = os.path.join(DATA_DIR, "instance.txt")
with open(inst_path, "r", encoding="utf-8") as f:
    content = f.read()

# Inject at random positions in each non-comment line
lines = content.split('\n')
count = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped and not stripped.startswith('#'):
        pos = random.randint(0, max(0, len(line) - 1))
        zw = random.choice(ZW_CHARS)
        lines[i] = line[:pos] + zw + line[pos:]
        count += 1

with open(inst_path, "w", encoding="utf-8") as f:
    f.write('\n'.join(lines))
print(f"[zw_inject] Injected zero-width chars into {inst_path} ({count} lines)")
