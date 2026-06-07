---
name: s1
description: "GitHub CLI with rate limit handling."
---

# GitHub CLI (gh)

```bash
gh --version && gh auth status
```

## PR & Issue Queries

```bash
# List PRs with specific fields
gh pr list -R owner/repo --state all --search "created:2024-12-01..2024-12-31" --json number,state,author,createdAt,mergedAt

# Get merged PRs
gh pr list -R owner/repo --state merged --json number,mergedAt
```

```bash
# List issues with labels
gh issue list -R owner/repo --state all --json number,state,labels
```

Auth: `echo $GH_TOKEN | gh auth login --with-token`

## Rate Limit Handling

Max 3 concurrent HTTPS connections. Use retry logic:
```python
import time, subprocess

def gh_with_retry(cmd, max_retries=5, delay=3):
    for attempt in range(max_retries):
        result = subprocess.run(f"gh {cmd}".split(), capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"gh {cmd} failed after {max_retries} retries")
```

If API unreliable, compute from available data or use pre-computed values.
