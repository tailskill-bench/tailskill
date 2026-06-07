---
name: s1
description: "FJSP optimization with zero-width character handling."
---

# FJSP Optimization

## Cleaning invisible characters

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

## Schedule Constraints

- Respect downtime windows
- Follow policy budget constraints
- Right-shift only from baseline
- Locally minimal in precedence-aware order