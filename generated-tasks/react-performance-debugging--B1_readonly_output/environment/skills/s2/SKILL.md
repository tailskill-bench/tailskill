---
name: s1
description: Guide for handling read-only output directories in Next.js performance tasks.
---

# Read-Only Output Directory

## Problem

The `/app/output` directory has been set to read-only permissions (`chmod 555`). Attempting to write files to this directory will fail with a "Permission denied" error.

## Diagnosis

Check directory permissions:
```bash
ls -la /app/output
```

If permissions show `dr-xr-xr-x` (555), the directory is read-only.

## Fix

Use the prepare_output script to restore write permissions:
```bash
python3 /app/.claude/skills/s1/scripts/prepare_output.py /app/output
```

This restores `chmod 755` on the output directory so you can write files normally.