#!/usr/bin/env python3
"""Restore corrupted output file from backup before processing."""
import shutil, sys

output = sys.argv[1] if len(sys.argv) > 1 else "/root/gdp.xlsx"
backup = output.replace('.xlsx', '_backup.xlsx')

try:
    with open(output, 'rb') as f:
        header = f.read(4)
    if not header.startswith(b'PK'):
        print(f"Corrupted file detected, restoring from {backup}")
        shutil.copy2(backup, output)
except FileNotFoundError:
    shutil.copy2(backup, output)

print(f"Output file ready: {output}")
