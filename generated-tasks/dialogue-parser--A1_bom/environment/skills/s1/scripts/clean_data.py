#!/usr/bin/env python3
"""Strip UTF-8 BOM from text files in-place."""
import sys


def strip_bom(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"Stripped BOM from {filepath}")
    else:
        print(f"No BOM found in {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [<file2> ...]", file=sys.stderr)
        sys.exit(1)
    for path in sys.argv[1:]:
        strip_bom(path)
