---
name: s1
description: "Codebook normalization with CSV BOM."
---

BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py`

```python
with open("file.csv","r",encoding="utf-8-sig") as f: reader=csv.DictReader(f)
```

Pipeline: load logs+codebooks → split → fuzzy match → calibrate → output solution.json
