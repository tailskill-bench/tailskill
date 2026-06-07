#!/usr/bin/env python3
"""A1_bom variant: Strip UTF-8 BOM from CSV/text/JSON sidechain files."""

import os
import sys
import glob


def strip_bom(filepath):
    """Remove UTF-8 BOM from a file if present."""
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        with open(filepath, 'wb') as f:
            f.write(content[3:])
        print(f"Stripped BOM from {filepath}")
        return True
    return False


def clean_directory(directory):
    """Scan directory for CSV/TXT/JSON files and strip BOM."""
    count = 0
    for ext in ('*.csv', '*.txt', '*.json'):
        for f in glob.glob(os.path.join(directory, ext)):
            if strip_bom(f):
                count += 1
    print(f"Cleaned {count} files with BOM in {directory}")
    return count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file_or_directory>")
        sys.exit(1)
    target = sys.argv[1]
    if os.path.isdir(target):
        clean_directory(target)
    else:
        strip_bom(target)
