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

## Repo Analytics Commands

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

## Output Directory Permissions

If output directory is read-only, fix before writing:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/report.json