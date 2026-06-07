---
name: s1
description: "FJSP optimization with CSV BOM handling."
---

# FJSP Optimization

## Reading CSV/text files

When reading CSV files, use `utf-8-sig` encoding to handle potential BOM markers:

```python
with open("downtime.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
```

Or strip BOM before reading:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

## Task Overview

Generate a feasible schedule that:
- Respects downtime windows
- Follows policy budget constraints
- Right-shifts only from baseline
- Is locally minimal in precedence-aware order
