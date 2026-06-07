#!/usr/bin/env python3
"""Strip zero-width Unicode characters from CSV cells."""
import unicodedata, csv, sys

filepath = sys.argv[1] if len(sys.argv) > 1 else "/root/data/water_temperature.csv"
col_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 1

rows = []
count = 0
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)
    for row in reader:
        if col_idx < len(row):
            val = row[col_idx]
            cleaned = ''.join(c for c in val if unicodedata.category(c) not in ('Cf', 'Cc'))
            if cleaned != val:
                try:
                    row[col_idx] = str(float(cleaned))
                    count += 1
                except:
                    pass
        rows.append(row)

with open(filepath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
print(f"Cleaned {count} cells with zero-width characters")
