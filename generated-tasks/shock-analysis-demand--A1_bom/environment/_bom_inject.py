#!/usr/bin/env python3
"""Inject UTF-8 BOM into CSV sidecar file to test encoding robustness."""
import csv, os, sys

filepath = sys.argv[1] if len(sys.argv) > 1 else "/root"
# Create a CSV sidecar with BOM that looks like WEO data export
csv_path = os.path.join(filepath, "weo_data_export.csv")

rows = [
    ["Year", "Real_GDP_growth", "GDP_deflator"],
    ["2019", "4.8", "4.5"],
    ["2020", "-6.3", "2.1"],
    ["2021", "10.5", "8.9"],
    ["2022", "11.8", "10.2"],
    ["2023", "7.5", "3.5"],
    ["2024", "5.2", "3.0"],
    ["2025", "4.8", "2.8"],
]

with open(csv_path, "wb") as f:
    f.write(b"\xef\xbb\xbf")  # UTF-8 BOM

with open(csv_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"[TailSkills] BOM: Created CSV sidecar with BOM at {csv_path}")
