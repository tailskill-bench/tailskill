---
name: s1
description: "Codebook normalization with CSV BOM."
---

# Codebook Normalization

BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py`

```python
with open("file.csv","r",encoding="utf-8-sig") as f: reader=csv.DictReader(f)
```

Pipeline: load logs+codebooks → split text → match (token overlap+fuzzy) → calibrate confidence → output solution.json
