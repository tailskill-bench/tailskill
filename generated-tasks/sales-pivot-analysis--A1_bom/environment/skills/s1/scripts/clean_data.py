#!/usr/bin/env python3
"""Data quality helper — strips BOM and normalizes encoding for CSV/text files."""

import sys
from pathlib import Path


def strip_bom(filepath: str) -> None:
    """Remove UTF-8 BOM from a text/CSV file if present."""
    p = Path(filepath)
    if not p.exists():
        return
    raw = p.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        p.write_bytes(raw[3:])
        print(f"[clean_data] BOM stripped from {filepath}")
    else:
        print(f"[clean_data] No BOM found in {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [--key KEY_COL]")
        sys.exit(1)

    target = sys.argv[1]
    strip_bom(target)


if __name__ == "__main__":
    main()
