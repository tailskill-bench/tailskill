---
name: s1
description: "FJSP optimization with zero-width character handling."
---

# FJSP Optimization

## Cleaning invisible characters

Strip zero-width Unicode characters before processing:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

## Task Overview

Generate a feasible schedule that:
- Respects downtime windows
- Follows policy budget constraints
- Right-shifts only from baseline
- Is locally minimal in precedence-aware order