#!/usr/bin/env python3
"""Remove duplicate rows by key column from stations.csv"""
import sys
import pandas as pd

target = sys.argv[1] if len(sys.argv) > 1 else "/root/data/stations.csv"
key_col_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 1

df = pd.read_csv(target)
key_col = df.columns[key_col_idx]
before = len(df)
df = df.drop_duplicates(subset=[key_col], keep='first')
after = len(df)
df.to_csv(target, index=False)
print(f"Removed {before - after} duplicate rows by {key_col}")
