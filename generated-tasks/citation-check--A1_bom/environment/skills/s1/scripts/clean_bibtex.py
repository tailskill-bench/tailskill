#!/usr/bin/env python3
"""Strip BOM from BibTeX files"""
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root/test.bib"

with open(target, 'rb') as f:
    data = f.read()

if data.startswith(b'\xef\xbb\xbf'):
    data = data[3:]
    with open(target, 'wb') as f:
        f.write(data)
    print(f"Stripped BOM from {target}")
else:
    print(f"No BOM found in {target}")
