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

Prints total number of holdings, AUM, total number of stock holdings, etc.

### Holdings change between two quarters

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <accession number assigned in q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <accession number assigned in q2>
```

Prints dynamic changes from baseline to current quarter: newly purchased stocks ranked by notional value, newly sold stocks ranked by notional value.

### Top funds holding a stock

```bash
python3 scripts/holding_analysis.py \
    --cusip <stock cusip> \
    --quarter 2025-q3 \
    --topk 10
```

Prints top 10 hedge funds holding a particular stock by highest notional value.

## Search Funds and Stocks

Fuzzy search engine for fund or stock meta information by name. Uses built-in fuzzy string matching (Levenshtein-based); exact names are not required.

### Fuzzy search a fund by name

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Returns top-10 funds with names most similar to the keyword. Each result includes:

- `ACCESSION_NUMBER`
- `REPORTCALENDARORQUARTER`
- `FILINGMANAGER_NAME`
- `FILINGMANAGER_STREET`
- `FILINGMANAGER_CITY`
- `FILINGMANAGER_STATEORCOUNTRY`
- `FORM13FFILENUMBER`

Example output fields for rank 1 (score = 81.818):

```
ACCESSION_NUMBER: 0001172661-25-003151
REPORTCALENDARORQUARTER: 30-JUN-2025
FILINGMANAGER_NAME: Bridgewater Associates, LP
FILINGMANAGER_STREET: One Nyala Farms Road
FILINGMANAGER_CITY: Westport
FILINGMANAGER_STATEORCOUNTRY: CT
FORM13FFILENUMBER: 028-11794
```

### Exact search a fund by accession number

```bash
python3 scripts/search_fund.py \
    --accession_number 0001172661-25-003151 \
    --quarter 2025-q2
```

Returns exactly one match if found (score = 100.000), with the same fields as above.

### Fuzzy search a stock CUSIP by name

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

Returns top-10 stock matches. Each result includes:

- `Name` — company name
- `CUSIP` — stock CUSIP identifier

Example output for rank 1 (score = 90.000):

```
Name: palantir technologies inc
CUSIP: 69608A108
```

## Rate Limit Handling

HTTPS API calls may be rate-limited (concurrent connections restricted). Use retry logic with exponential backoff:

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=30))
def fetch_with_retry(url):
    import urllib.request
    return urllib.request.urlopen(url, timeout=30)
```

Prefer local data files already available in `/root/2025-q2` and `/root/2025-q3` to avoid network dependencies.