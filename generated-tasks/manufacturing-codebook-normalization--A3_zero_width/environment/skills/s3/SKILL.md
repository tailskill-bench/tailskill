---
name: s1
description: "Normalize manufacturing codebooks with zero-width character handling."
---

# Codebook Normalization

Strip zero-width Unicode characters:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

## Pipeline

1. Load `test_center_logs.csv` and product codebooks
2. Split `raw_reason_text` into segments
3. Match segments via token overlap + fuzzy matching
4. Calibrate confidence with `UNKNOWN` handling
5. Output `solution.json`