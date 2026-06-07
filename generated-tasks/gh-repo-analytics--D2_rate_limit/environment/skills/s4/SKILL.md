---
name: s1
description: "GitHub CLI with rate limit handling."
---

PRs: `gh pr list -R owner/repo --state all --json number,state,author`
Issues: `gh issue list -R owner/repo --state all --json number,state,labels`
Auth: `echo $GH_TOKEN | gh auth login --with-token`

Rate limit (3 concurrent):
```python
import time, subprocess
def gh_retry(cmd, retries=5, delay=3):
    for i in range(retries):
        r = subprocess.run(f"gh {cmd}".split(), capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        time.sleep(delay * (i + 1))
```
