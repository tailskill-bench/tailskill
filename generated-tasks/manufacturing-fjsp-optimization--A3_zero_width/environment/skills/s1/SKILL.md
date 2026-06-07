---
name: s1
description: "FJSP optimization with zero-width character handling."
---

# FJSP Optimization

## Cleaning invisible characters

Text files may contain invisible zero-width Unicode characters. Strip them before processing:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

Or filter inline:

```python
import unicodedata
def clean(text):
    return "".join(c for c in text if unicodedata.category(c) != 'Cf')
```

## Task Overview

Generate a feasible schedule that:
- Respects downtime windows
- Follows policy budget constraints
- Right-shifts only from baseline
- Is locally minimal in precedence-aware order
