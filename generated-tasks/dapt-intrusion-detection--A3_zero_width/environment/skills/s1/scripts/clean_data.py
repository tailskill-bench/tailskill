#!/usr/bin/env python3
"""Strip zero-width Unicode characters from CSV/text files."""
import sys
import unicodedata


def strip_zero_width(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = ''.join(c for c in content if unicodedata.category(c) not in ('Cf', 'Cc') or c in ('\n', '\r', '\t'))
    if cleaned != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"Stripped zero-width chars from {filepath}")
    else:
        print(f"No zero-width chars found in {filepath}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file>")
        sys.exit(1)
    strip_zero_width(sys.argv[1])
