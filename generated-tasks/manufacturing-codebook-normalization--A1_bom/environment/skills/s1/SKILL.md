---
name: s1
description: "Manufacturing codebook normalization with CSV BOM handling."
---

# Manufacturing Codebook Normalization

## Reading CSV files

When reading CSV files, always use `utf-8-sig` encoding to handle potential BOM markers:

```python
import csv
with open("file.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
```

Or strip BOM before reading:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

## Normalization Pipeline

1. Load test_center_logs.csv and product codebooks
2. Split raw_reason_text into segments
3. Match each segment against codebook entries using token overlap + fuzzy matching
4. Calibrate confidence scores with UNKNOWN handling
5. Output solution.json with normalized records
