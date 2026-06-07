#!/usr/bin/env python3
"""Clean extreme values (0, negative, -999) from CSV numeric columns by filtering invalid rows."""
import csv
import sys


def is_extreme(val_str):
    try:
        v = float(val_str)
        return v <= 0
    except (ValueError, TypeError):
        return False


def clean_extremes_csv(filepath, col_idx):
    col_idx = int(col_idx)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    n_removed = 0
    clean_rows = [header]
    for row in rows[1:]:
        if col_idx < len(row) and is_extreme(row[col_idx]):
            n_removed += 1
        else:
            clean_rows.append(row)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(clean_rows)

    print(f"Removed {n_removed} rows with extreme values in column {col_idx} (kept {len(clean_rows)-1} rows)")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        clean_extremes_csv(sys.argv[1], sys.argv[2])
    else:
        print("Usage: clean_data.py <filepath> <col_idx>")
