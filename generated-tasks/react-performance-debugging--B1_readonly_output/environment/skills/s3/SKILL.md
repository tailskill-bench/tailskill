---
name: s1
description: Guide for handling read-only output directories in Next.js performance tasks.
---

# Read-Only Output Directory

## Diagnosis

Check permissions:
```bash
ls -la /app/output
```

If permissions show `dr-xr-xr-x` (555), the directory is read-only.

## Fix

Run the prepare_output script to restore write permissions:
```bash
python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output
```

This restores `chmod 755` on `/app/output`, enabling normal file writes.