#!/usr/bin/env python3
"""Ensure per-station elevation consistency by replacing with station median"""
import sys
import pandas as pd
import numpy as np

target = sys.argv[1] if len(sys.argv) > 1 else "/root/data/stations.csv"
col_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 6
key_col_idx = int(sys.argv[3]) if len(sys.argv) > 3 else 1

df = pd.read_csv(target)
col_name = df.columns[col_idx]
key_col = df.columns[key_col_idx]
df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
df[col_name] = df[col_name].replace([np.inf, -np.inf], np.nan)

global_median = df[col_name].median()
df[col_name] = df.groupby(key_col)[col_name].transform(
    lambda x: x.median() if pd.notna(x.median()) else global_median
)
df.to_csv(target, index=False)
print(f"Cleaned {col_name} using per-station median consensus")
