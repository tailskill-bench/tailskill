#!/usr/bin/env python3
"""Strip zero-width Unicode chars (Cf category) from CSV files in /app/data."""
import csv, unicodedata, os, glob

TARGETS = ["/app/data", "/app/output"]

removed = 0
for directory in TARGETS:
    for fp in glob.glob(os.path.join(directory, "*.csv")):
        with open(fp, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        changed = False
        for row in rows:
            for k in row:
                val = row[k]
                if val:
                    cleaned = "".join(c for c in val if unicodedata.category(c) != 'Cf')
                    if cleaned != val:
                        row[k] = cleaned
                        changed = True
                        removed += 1

        if changed:
            with open(fp, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            print(f"[clean] Stripped zero-width chars from {fp}")

if removed:
    print(f"[clean] Cleaned {removed} cells")
else:
    print("[clean] No zero-width chars found")
