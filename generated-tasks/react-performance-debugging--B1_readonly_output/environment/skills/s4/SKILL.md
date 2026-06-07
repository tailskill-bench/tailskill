---
name: s1
description: Guide for handling read-only output directories in Next.js performance tasks.
---

# Read-Only Output Directory

## Diagnosis

```bash
ls -la /app/output
```

Permissions `dr-xr-xr-x` (555) confirm read-only.

## Fix

```bash
python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output
```

Restores `chmod 755` on `/app/output`.