---
name: s1
description: "13F SEC financial report analysis with network retry guidance for DNS jitter environments."
---

## Analyze Fund Holdings

### Single quarter holdings summary

```bash
python3 scripts/one_fund_analysis.py \
    --accession_number ... \
    --quarter 2025-q2
```

### Holdings change between two quarters

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <accession number assigned in q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <accession number assigned in q2>
```

### Top fund holders of a stock

```bash
python3 scripts/holding_analysis.py \
    --cusip <stock cusip> \
    --quarter 2025-q3 \
    --topk 10
```

## Search Fund or Stock Metadata

### Fuzzy search a fund by name

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Returns fields: `ACCESSION_NUMBER`, `REPORTCALENDARORQUARTER`, `FILINGMANAGER_NAME`, `FILINGMANAGER_STREET`, `FILINGMANAGER_CITY`, `FILINGMANAGER_STATEORCOUNTRY`, `FORM13FFILENUMBER`.

### Exact search a fund by accession number

```bash
python3 scripts/search_fund.py \
    --accession_number 0001172661-25-003151 \
    --quarter 2025-q2
```

### Fuzzy search a stock CUSIP by name

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

Returns `Name` and `CUSIP` fields.

## Network Retry Guidance

For DNS jitter, use retry logic:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
def fetch_with_retry(url):
    import urllib.request
    return urllib.request.urlopen(url, timeout=30)
```

Prefer local data in `/root/2025-q2` and `/root/2025-q3` to avoid network dependencies.