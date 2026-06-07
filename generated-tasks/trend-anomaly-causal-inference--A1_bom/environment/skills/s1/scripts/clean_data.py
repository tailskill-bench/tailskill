#!/usr/bin/env python3
"""Strip BOM from CSV/text files."""
import sys


def strip_bom(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(filepath, 'wb') as f:
            f.write(data[3:])
        print(f"Stripped BOM from {filepath}")
    else:
        print(f"No BOM found in {filepath}")


if __name__ == "__main__":
    for path in sys.argv[1:]:
        strip_bom(path)
