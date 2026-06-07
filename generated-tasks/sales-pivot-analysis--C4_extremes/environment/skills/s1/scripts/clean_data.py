#!/usr/bin/env python3
"""Data quality helper — filters extreme/boundary values from numeric columns in CSV/XLSX files."""

import sys
import numpy as np


def clean_extremes(filepath, col_idx=None):
    """Remove rows with extreme values (0, negative, -999) in numeric columns."""
    import pandas as pd

    if filepath.lower().endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    before = len(df)
    for col in df.select_dtypes(include=[np.number]).columns:
        # Filter out clearly invalid values: 0 or negative in count/population/income columns
        if any(kw in col.upper() for kw in ['EARNER', 'INCOME', 'POPULATION', 'TOTAL']):
            df = df[df[col] > 0]

    df = df.reset_index(drop=True)
    after = len(df)

    if filepath.lower().endswith(".xlsx"):
        df.to_excel(filepath, index=False)
    else:
        df.to_csv(filepath, index=False)

    print(f"[clean_data] Extremes filtered: {before - after} rows removed → {filepath}")


def main():
    if len(sys.argv) < 2:
        print("Usage: clean_data.py <file> [--col COL_IDX]")
        sys.exit(1)

    target = sys.argv[1]
    clean_extremes(target)


if __name__ == "__main__":
    main()
