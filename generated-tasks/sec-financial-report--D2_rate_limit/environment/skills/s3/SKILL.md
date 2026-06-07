---
name: s1
description: "13F SEC financial report analysis with rate limit handling guidance."
---

## Analyze Fund Holdings

### Single-quarter fund summary

```bash
python3 scripts/one_fund_analysis.py \
    --accession_number ... \
    --quarter 2025-q2
```

Prints total holdings, AUM, and total stock holdings.

### Holdings change between two quarters

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <accession number assigned in q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <accession number assigned in q2>
```

Prints newly purchased and newly sold stocks ranked by notional value.

### Top funds holding a stock

```bash
python3 scripts/holding_analysis.py \
    --cusip <stock cusip> \
    --quarter 2025-q3 \
    --topk 10
```

Prints top 10 funds holding the stock by highest notional value.

## Search Funds and Stocks

Fuzzy search (Levenshtein-based) for fund or stock metadata; exact names not required.

### Fuzzy search a fund by name

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Returns top-10 matching funds with fields: `ACCESSION_NUMBER`, `REPORTCALENDARORQUARTER`, `FILINGMANAGER_NAME`, `FILINGMANAGER_STREET`, `FILINGMANAGER_CITY`, `FILINGMANAGER_STATEORCOUNTRY`, `FORM13FFILENUMBER`.

### Exact search a fund by accession number

```bash
python3 scripts/search_fund.py \
    --accession_number 0001172661-25-003151 \
    --quarter 2025-q2
```

Returns one match (score = 100.000) with the same fields.

### Fuzzy search a stock CUSIP by name

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

Returns top-10 stock matches with `Name` and `CUSIP` fields.

## Rate Limit Handling

API calls may be rate-limited. Use retry with exponential backoff:

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=30))
def fetch_with_retry(url):
    import urllib.request
    return urllib.request.urlopen(url, timeout=30)
```

Prefer local data in `/root/2025-q2` and `/root/2025-q3` to avoid network dependencies.