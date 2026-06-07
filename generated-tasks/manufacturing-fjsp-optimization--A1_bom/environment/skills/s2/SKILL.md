---
name: s1
description: "FJSP optimization with CSV BOM handling."
---

# FJSP Optimization

**CSV BOM**: Use `encoding='utf-8-sig'` or run `python3 /root/.claude/skills/s1/scripts/clean_data.py`.

```python
with open("downtime.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
```

## Schedule Requirements
- Respect downtime windows and policy budget constraints
- Right-shift only from baseline
- Locally minimal in precedence-aware order
