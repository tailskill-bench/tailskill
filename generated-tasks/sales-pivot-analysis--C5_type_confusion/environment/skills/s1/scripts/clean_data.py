#!/usr/bin/env python3
"""Data quality helper — converts type-confused values to numeric in CSV/XLSX files."""

import sys
import numpy as np


def clean_type_confusion(filepath, col_idx=None):
    """Convert non-numeric markers to NaN and fill with column median."""
    import pandas as pd

    if filepath.lower().endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    for col in df.select_dtypes(include=[object]).columns:
        # Try converting to numeric; non-numeric markers become NaN
        converted = pd.to_numeric(df[col], errors='coerce')
        # If most values converted successfully, it was a numeric column with markers
        if converted.notna().sum() > len(df) * 0.5:
            median = converted.median()
            df[col] = converted.fillna(median)

    if filepath.lower().endswith(".xlsx"):
        df.to_excel(filepath, index=False)
    else:
        df.to_csv(filepath, index=False)

    print(f"[clean_data] Type confusion cleaned → {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [--col COL_IDX]")
        sys.exit(1)

    target = sys.argv[1]
    clean_type_confusion(target)


if __name__ == "__main__":
    main()
