#!/usr/bin/env python3
"""Strip BOM from CSV/text files."""
import os, sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root/data"

if os.path.isfile(target):
    files = [target]
else:
    files = [os.path.join(target, f) for f in os.listdir(target)
             if f.endswith(('.csv', '.txt', '.json'))]

for fp in files:
    with open(fp, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(fp, 'wb') as f:
            f.write(data[3:])
        print(f"BOM stripped from {fp}")
