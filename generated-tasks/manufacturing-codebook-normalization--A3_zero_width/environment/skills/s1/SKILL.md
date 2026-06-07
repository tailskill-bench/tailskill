---
name: s1
description: "Manufacturing codebook normalization with zero-width character handling."
---

# Manufacturing Codebook Normalization

## Cleaning invisible characters

When reading CSV files, text fields may contain invisible zero-width Unicode characters. Strip them before processing:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

Or filter inline:

```python
import unicodedata
def clean(text):
    return "".join(c for c in text if unicodedata.category(c) != 'Cf')
```

## Normalization Pipeline

1. Load test_center_logs.csv and product codebooks
2. Split raw_reason_text into segments
3. Match each segment against codebook entries using token overlap + fuzzy matching
4. Calibrate confidence scores with UNKNOWN handling
5. Output solution.json with normalized records
