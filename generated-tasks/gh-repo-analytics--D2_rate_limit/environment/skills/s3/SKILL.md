---
name: s1
description: "GitHub CLI with rate limit handling."
---

# gh CLI

```bash
gh pr list -R owner/repo --state all --json number,state,author
gh issue list -R owner/repo --state all --json number,state,labels
```
Auth: `echo $GH_TOKEN | gh auth login --with-token`

## Rate Limit
Max 3 concurrent connections. Retry:
```python
import time, subprocess

def gh_retry(cmd, retries=5, delay=3):
    for i in range(retries):
        r = subprocess.run(f"gh {cmd}".split(), capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        time.sleep(delay * (i + 1))
    raise RuntimeError(f"gh {cmd} failed")
```
If unreliable, use available data or pre-computed values.
