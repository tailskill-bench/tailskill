#!/usr/bin/env python3
"""Inject zero-width Unicode chars into test_center_logs.csv text fields."""
import csv, random, os

random.seed(42)
ZW_CHARS = ['\u200b', '\u200c', '\u200d', '\ufeff']
TARGET_FIELDS = ["raw_reason_text", "station", "fail_code", "test_item"]
INJECT_RATE = 0.30

DATA_DIR = "/app/data"
TARGET = os.path.join(DATA_DIR, "test_center_logs.csv")

with open(TARGET, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

fieldnames = list(rows[0].keys())
injected = 0

for row in rows:
    for field in TARGET_FIELDS:
        val = row.get(field, "")
        if val and random.random() < INJECT_RATE:
            pos = random.randint(1, max(1, len(val) - 1))
            zw = random.choice(ZW_CHARS)
            row[field] = val[:pos] + zw + val[pos:]
            injected += 1

with open(TARGET, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print(f"[zw_inject] Injected {injected} zero-width chars into {TARGET}")
