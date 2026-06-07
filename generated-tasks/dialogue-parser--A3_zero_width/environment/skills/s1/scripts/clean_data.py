#!/usr/bin/env python3
"""Strip zero-width Unicode characters from text files in-place."""
import sys

ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff", "\u00ad", "\u2060", "\u2061", "\u2062", "\u2063", "\u2064"}


def strip_zero_width(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    cleaned = "".join(c for c in content if c not in ZW_CHARS)

    if cleaned != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Stripped zero-width chars from {filepath}")
    else:
        print(f"No zero-width chars found in {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [<file2> ...]", file=sys.stderr)
        sys.exit(1)
    for path in sys.argv[1:]:
        strip_zero_width(path)
