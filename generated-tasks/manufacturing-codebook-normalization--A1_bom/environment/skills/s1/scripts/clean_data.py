#!/usr/bin/env python3
"""Strip UTF-8 BOM from CSV/TXT/JSON files in /app/data."""
import os, glob

TARGETS = ["/app/data", "/app/output"]

removed = 0
for directory in TARGETS:
    for ext in ("*.csv", "*.txt", "*.json"):
        for fp in glob.glob(os.path.join(directory, "**", ext), recursive=True):
            with open(fp, "rb") as f:
                raw = f.read()
            if raw.startswith(b"\xef\xbb\xbf"):
                with open(fp, "wb") as f:
                    f.write(raw[3:])
                removed += 1
                print(f"[clean] Stripped BOM from {fp}")

if removed:
    print(f"[clean] Removed BOM from {removed} file(s)")
else:
    print("[clean] No BOM found")
