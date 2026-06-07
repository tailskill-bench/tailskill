---
name: s1
description: "13F SEC financial report analysis with fuzzy name matching for hedge fund AUM and holdings comparison."
---

## Fund Analysis

Analyze a single fund's holdings for one quarter:

```bash
python3 scripts/one_fund_analysis.py \
    --accession_number <ACCESSION_NUMBER> \
    --quarter 2025-q2
```

Analyze holdings change between two quarters (newly purchased/sold stocks ranked by notional value):

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <ACCESSION_NUMBER_Q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <ACCESSION_NUMBER_Q2>
```

Analyze which funds hold a stock the most:

```bash
python3 scripts/holding_analysis.py \
    --cusip <STOCK_CUSIP> \
    --quarter 2025-q3 \
    --topk 10
```

## Fuzzy Search

Fuzzy search uses Levenshtein-based string matching. Exact names are not required.

### Search funds

Fuzzy search by name (returns top-10 matches with `ACCESSION_NUMBER`, `REPORTCALENDARORQUARTER`, `FILINGMANAGER_NAME`, `FILINGMANAGER_STREET`, `FILINGMANAGER_CITY`, `FILINGMANAGER_STATEORCOUNTRY`, `FORM13FFILENUMBER`):

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Exact search by accession number (returns one match, score = 100.000):

```bash
python3 scripts/search_fund.py \
    --accession_number 0001172661-25-003151 \
    --quarter 2025-q2
```

### Search stocks

Fuzzy search by name (returns top-10 matches with `Name`, `CUSIP`):

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

## Output Permissions

Before writing to output files (e.g., `/root/answers.json`), fix directory permissions:

```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root