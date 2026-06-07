#!/usr/bin/env python3
"""Inject UTF-8 BOM into downtime.csv."""
import os

DATA_DIR = "/app/data"
TARGET = os.path.join(DATA_DIR, "downtime.csv")

with open(TARGET, "rb") as f:
    content = f.read()

if not content.startswith(b"\xef\xbb\xbf"):
    with open(TARGET, "wb") as f:
        f.write(b"\xef\xbb\xbf" + content)
    print(f"[bom_inject] Added UTF-8 BOM to {TARGET}")
else:
    print(f"[bom_inject] BOM already present in {TARGET}")
