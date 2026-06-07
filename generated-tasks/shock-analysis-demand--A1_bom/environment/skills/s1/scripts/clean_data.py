#!/usr/bin/env python3
"""Strip UTF-8 BOM from CSV sidecar files in the working directory."""
import os, glob

target_dir = sys.argv[1] if len(sys.argv) > 1 else "/root"

count = 0
for csv_path in glob.glob(os.path.join(target_dir, "*.csv")):
    with open(csv_path, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        with open(csv_path, "wb") as f:
            f.write(raw[3:])
        count += 1
        print(f"  Stripped BOM from {csv_path}")

print(f"Cleaned BOM from {count} CSV files in {target_dir}")
