#!/usr/bin/env python3
"""Clean NaN/Inf values from CSV numeric columns using median fillna."""
import csv
import math
import sys


def parse_float(s):
    try:
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except (ValueError, TypeError):
        return None


def clean_nan_csv(filepath, col_idx):
    col_idx = int(col_idx)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Compute median of valid values
    valid = []
    for row in rows[1:]:
        if col_idx < len(row):
            v = parse_float(row[col_idx])
            if v is not None:
                valid.append(v)

    if not valid:
        print(f"No valid values in column {col_idx}, skipping")
        return

    valid.sort()
    median = valid[len(valid) // 2]

    # Replace NaN/Inf with median
    n_fixed = 0
    for row in rows[1:]:
        if col_idx < len(row):
            v = parse_float(row[col_idx])
            if v is None and row[col_idx].strip():
                row[col_idx] = str(median)
                n_fixed += 1

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Fixed {n_fixed} NaN/Inf values in column {col_idx} with median={median}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        clean_nan_csv(sys.argv[1], sys.argv[2])
    else:
        print("Usage: clean_data.py <filepath> <col_idx>")
