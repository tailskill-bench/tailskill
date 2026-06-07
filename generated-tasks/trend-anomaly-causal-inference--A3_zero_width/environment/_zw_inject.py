#!/usr/bin/env python3
"""Inject zero-width Unicode characters into CSV text fields."""
import csv
import random
import sys

ZW_CHARS = ["\u200b", "\u200c", "\u200d"]


def inject_zero_width_csv(filepath, ratio=0.03):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    random.seed(42)
    n_modified = 0
    for i in range(1, len(rows)):  # skip header
        row = rows[i]
        for j, cell in enumerate(row):
            if cell and random.random() < ratio:
                pos = random.randint(0, max(0, len(cell) - 1))
                row[j] = cell[:pos] + random.choice(ZW_CHARS) + cell[pos:]
                n_modified += 1

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"[TailSkills] Zero-width: {n_modified} cells modified in {filepath}")


if __name__ == "__main__":
    inject_zero_width_csv(sys.argv[1])
