---
name: s1
description: "13F SEC financial report analysis with fuzzy name matching for hedge fund AUM and holdings comparison."
---

## Fund Analysis

### Analyze a single fund's holdings for one quarter

```bash
python3 scripts/one_fund_analysis.py \
    --accession_number <ACCESSION_NUMBER> \
    --quarter 2025-q2
```

Prints total holdings, AUM, number of stock holdings, and other summary data for the specified fund.

### Analyze holdings change between two quarters

```bash
python3 scripts/one_fund_analysis.py \
    --quarter 2025-q3 \
    --accession_number <ACCESSION_NUMBER_Q3> \
    --baseline_quarter 2025-q2 \
    --baseline_accession_number <ACCESSION_NUMBER_Q2>
```

Prints dynamic changes from baseline quarter to target quarter: newly purchased stocks ranked by notional value, newly sold stocks ranked by notional value.

### Analyze which funds hold a stock the most

```bash
python3 scripts/holding_analysis.py \
    --cusip <STOCK_CUSIP> \
    --quarter 2025-q3 \
    --topk 10
```

Prints top 10 hedge funds holding the specified stock by highest notional value.

## Fuzzy Search

Fuzzy search for fund or stock metadata using Levenshtein-based string matching. Exact names are not required.

### Fuzzy search a fund by name

```bash
python3 scripts/search_fund.py --keywords "bridgewater" --quarter 2025-q2 --topk 10
```

Returns top-10 funds with names most similar to the keywords. Each result includes:

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

Returns exactly one match (score = 100.000) if found, with the same fields as fuzzy search.

### Fuzzy search a stock by name

```bash
python3 scripts/search_stock_cusip.py \
    --keywords palantir \
    --topk 10
```

Returns top-10 stock matches. Each result includes:

- `Name` — company name
- `CUSIP` — stock CUSIP identifier

## Output Permissions

Before writing results to output files (e.g., `/root/answers.json`), ensure the output directory has proper write permissions. In containerized environments, directories may have restricted permissions. Run:

```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root
```

This fixes directory permissions for output writing.