#!/usr/bin/env python3
"""Strip zero-width Unicode characters from CSV/text files."""
import csv
import sys
import unicodedata

ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}


def strip_zero_width(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    cleaned = "".join(c for c in content if c not in ZW_CHARS and unicodedata.category(c) != "Cf")

    if cleaned != content:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(cleaned)
        print(f"Stripped zero-width chars from {filepath}")
    else:
        print(f"No zero-width chars found in {filepath}")


if __name__ == "__main__":
    for path in sys.argv[1:]:
        strip_zero_width(path)
