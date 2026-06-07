---
name: s1
description: GitHub CLI (gh) usage guide with network retry handling for DNS jitter environments.
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
```bash
echo $GH_TOKEN | gh auth login --with-token
```

## Handling DNS Jitter / Network Instability

Use retry logic with exponential backoff (default: 5 retries, base delay 2s). On persistent failure, compute from available data or use pre-computed values.