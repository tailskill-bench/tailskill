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

Prints total number of holdings, AUM, total number of stock holdings, etc.

### Holdings change between two quarters

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <accession number assigned in q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <accession number assigned in q2>
```

Prints dynamic changes from 2025-q2 to 2025-q3: newly purchased stocks ranked by notional value, newly sold stocks ranked by notional value.

### Top fund holders of a stock

```bash
python3 scripts/holding_analysis.py \
    --cusip <stock cusip> \
    --quarter 2025-q3 \
    --topk 10
```

Prints top 10 hedge funds holding a particular stock by highest notional value.

## Search Fund or Stock Metadata

Fuzzy search engine for fund or stock meta information by name. Uses built-in Levenshtein-based fuzzy matching.

### Fuzzy search a fund by name

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Returns top-10 funds with name most similar to the search term. Each result includes:

- `ACCESSION_NUMBER`
- `REPORTCALENDARORQUARTER`
- `FILINGMANAGER_NAME`
- `FILINGMANAGER_STREET`
- `FILINGMANAGER_CITY`
- `FILINGMANAGER_STATEORCOUNTRY`
- `FORM13FFILENUMBER`

### Exact search a fund by accession number

```bash
python3 scripts/search_fund.py \
    --accession_number 0001172661-25-003151 \
    --quarter 2025-q2
```

Returns exactly one match if found (score = 100.000).

### Fuzzy search a stock CUSIP by name

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

Returns top-10 stock matches with `Name` and `CUSIP` fields.

## Network Retry Guidance

DNS resolution may be intermittently unreliable. When making network requests (e.g., downloading SEC data, API calls), use retry logic:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
def fetch_with_retry(url):
    import urllib.request
    return urllib.request.urlopen(url, timeout=30)
```

Prefer working with local data files already available in `/root/2025-q2` and `/root/2025-q3` to avoid network dependencies.