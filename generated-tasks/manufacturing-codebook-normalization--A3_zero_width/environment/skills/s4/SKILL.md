---
name: s1
description: "Normalize manufacturing codebooks with zero-width character handling."
---

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

Pipeline: Load `test_center_logs.csv` and product codebooks → split `raw_reason_text` into segments → match via token overlap + fuzzy matching → calibrate confidence with `UNKNOWN` handling → output `solution.json`