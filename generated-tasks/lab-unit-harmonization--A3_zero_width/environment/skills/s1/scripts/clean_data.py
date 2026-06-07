#!/usr/bin/env python3
"""Strip zero-width Unicode characters from CSV files."""
import sys
import unicodedata

for path in sys.argv[1:]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = ''.join(
        c for c in content
        if unicodedata.category(c) not in ('Cf', 'Cc') or c in ('\n', '\r', '\t')
    )
    if cleaned != content:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(cleaned)
        print(f"Cleaned zero-width chars from {path}")
    else:
        print(f"No zero-width chars found in {path}")
