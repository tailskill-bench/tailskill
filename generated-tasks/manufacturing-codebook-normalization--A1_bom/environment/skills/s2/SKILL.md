---
name: s1
description: "Manufacturing codebook normalization with CSV BOM handling."
---

# Codebook Normalization

**CSV BOM**: Use `encoding='utf-8-sig'` or run `python3 /root/.claude/skills/s1/scripts/clean_data.py`.

```python
with open("file.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
```

## Pipeline
1. Load test_center_logs.csv and product codebooks
2. Split raw_reason_text into segments
3. Match against codebook (token overlap + fuzzy matching)
4. Calibrate confidence with UNKNOWN handling
5. Output solution.json
