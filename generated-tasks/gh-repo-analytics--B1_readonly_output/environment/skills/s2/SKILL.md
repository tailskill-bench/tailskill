---
name: s1
description: GitHub CLI (gh) usage guide with output permission handling for repository analytics.
---

# GitHub CLI (gh) Guide

## Installation Verification
```bash
gh --version
gh auth status
```

## Common Commands for Repo Analytics

### PR Analysis
```bash
gh pr list -R owner/repo --state all --search "created:2024-12-01..2024-12-31" --json number,state,author,createdAt,mergedAt
gh pr list -R owner/repo --state merged --json number,mergedAt
```

### Issue Analysis
```bash
gh issue list -R owner/repo --state all --search "created:2024-12-01..2024-12-31" --json number,state,labels
gh issue list -R owner/repo --label bug --state all --json number
```

### Authentication
If `GH_TOKEN` is set, `gh` authenticates automatically:
```bash
echo $GH_TOKEN | gh auth login --with-token
```

## Handling Output Directory Permissions

If the output directory is read-only (`chmod 555`), fix before writing:
```python
import os, stat
output_dir = '/app'
if os.path.exists(output_dir) and not os.access(output_dir, os.W_OK):
    mode = os.stat(output_dir).st_mode
    os.chmod(output_dir, mode | stat.S_IWUSR | stat.S_IXUSR)
```

Or run the helper script:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/report.json