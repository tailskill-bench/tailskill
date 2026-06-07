---
name: s1
description: "FJSP with CSV BOM."
---

BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py`

```python
with open("downtime.csv","r",encoding="utf-8-sig") as f: reader=csv.DictReader(f)
```

Schedule: respect downtime/budgets, right-shift baseline, minimize precedence.
