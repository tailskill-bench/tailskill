#!/usr/bin/env python3
"""Data quality helper — removes duplicate rows based on key column in CSV/XLSX files."""

import sys


def clean_duplicates(filepath, key_col):
    """Remove duplicate rows based on key column, keeping first occurrence."""
    import pandas as pd

    if filepath.lower().endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    before = len(df)
    df = df.drop_duplicates(subset=[key_col], keep='first')
    after = len(df)

    if filepath.lower().endswith(".xlsx"):
        df.to_excel(filepath, index=False)
    else:
        df.to_csv(filepath, index=False)

    print(f"[clean_data] Duplicates removed: {before - after} rows dropped (key={key_col}) → {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> --key KEY_COL")
        sys.exit(1)

    target = sys.argv[1]
    key_col = None
    if '--key' in sys.argv:
        key_col = sys.argv[sys.argv.index('--key') + 1]

    if not key_col:
        print("Error: --key is required for duplicate removal", file=sys.stderr)
        sys.exit(1)

    clean_duplicates(target, key_col)


if __name__ == "__main__":
    main()
