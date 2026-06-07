#!/usr/bin/env python3
"""Strip zero-width Unicode characters from BibTeX files"""
import sys
import unicodedata

target = sys.argv[1] if len(sys.argv) > 1 else "/root/test.bib"

with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

cleaned = ''.join(c for c in content if unicodedata.category(c) not in ('Cf', 'Cc') or c in ('\n', '\r', '\t'))

with open(target, 'w', encoding='utf-8') as f:
    f.write(cleaned)

removed = len(content) - len(cleaned)
print(f"Removed {removed} invisible characters from {target}")
