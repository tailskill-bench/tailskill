#!/usr/bin/env python3
"""Strip zero-width Unicode chars (Cf category) from files in /app/data and /app/output."""
import unicodedata, os, glob

TARGETS = ["/app/data", "/app/output"]
EXTS = ("*.csv", "*.txt", "*.json")

removed = 0
for directory in TARGETS:
    for ext in EXTS:
        for fp in glob.glob(os.path.join(directory, ext)):
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = "".join(c for c in content if unicodedata.category(c) != 'Cf')
            if cleaned != content:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                removed += 1
                print(f"[clean] Stripped zero-width chars from {fp}")

if removed:
    print(f"[clean] Cleaned {removed} file(s)")
else:
    print("[clean] No zero-width chars found")
