#!/usr/bin/env python3
"""Strip BOM from CSV/text/JSON files."""
import sys
import os


def strip_bom(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        with open(filepath, 'wb') as f:
            f.write(content)
        print(f"BOM stripped from {filepath}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file_or_dir>")
        sys.exit(1)
    target = sys.argv[1]
    if os.path.isdir(target):
        for fn in os.listdir(target):
            if fn.endswith(('.csv', '.txt', '.json')):
                strip_bom(os.path.join(target, fn))
    else:
        strip_bom(target)
