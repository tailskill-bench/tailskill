#!/usr/bin/env python3
"""Data quality helper — cleans NaN/Inf from numeric columns in CSV/XLSX files."""

import sys
from pathlib import Path

import numpy as np


def clean_nan_inf(filepath, key_col=None):
    """Remove or fill NaN/Inf values in numeric columns."""
    import pandas as pd

    if filepath.lower().endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    for col in df.select_dtypes(include=[np.number]).columns:
        # Replace Inf with NaN first
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        # Fill NaN with median of the column
        median = df[col].median()
        if pd.notna(median):
            df[col] = df[col].fillna(median)
        else:
            df[col] = df[col].fillna(0)

    if filepath.lower().endswith(".xlsx"):
        df.to_excel(filepath, index=False)
    else:
        df.to_csv(filepath, index=False)

    print(f"[clean_data] NaN/Inf cleaned in {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [--key KEY_COL]")
        sys.exit(1)

    target = sys.argv[1]
    key_col = None
    if '--key' in sys.argv:
        key_col = sys.argv[sys.argv.index('--key') + 1]

    clean_nan_inf(target, key_col)


if __name__ == "__main__":
    main()
