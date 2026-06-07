---
name: s1
description: GitHub CLI usage with output permission handling for repo analytics.
---

## Setup & Auth
```bash
gh --version
gh auth status
echo $GH_TOKEN | gh auth login --with-token
```

## Repo Analytics

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

## Output Permissions
Fix read-only output dirs before writing:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /app/report.json