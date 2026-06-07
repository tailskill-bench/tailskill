---
name: s1
description: Clinical laboratory data harmonization with unit conversion, format standardization, and robust data quality handling.
---

# Lab Unit Harmonization

## When to Use

- Converting between US conventional and SI units (e.g., mg/dL ↔ µmol/L)
- Standardizing inconsistent numeric formats (scientific notation, European decimals)
- Preparing CKD lab panels for eGFR calculations or staging models

## Data Quality Issues

| Issue Type | Example |
|------------|---------|
| Mixed Units | Creatinine: mg/dL vs µmol/L |
| Scientific Notation | `1.5e3` instead of `1500` |
| Thousand Separators | `1,234.5` vs `1234.5` |
| European Decimals | `12,5` instead of `12.5` |
| Whitespace Issues | `  45.2 ` vs `45.2` |
| Missing Values | `NaN`, `-999`, blank |

## Core Workflow

**Before filtering**: Numeric fields may contain text markers (N/A, -, TBD). If a backup file exists, restore corrupted cells:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/environment/data/ckd_lab_data.csv 1
```

Alternatively, use `pd.to_numeric(errors='coerce')`.

### Step 0: Filter Incomplete Records

Exclude rows with any missing values:

```python
def count_missing(row, numeric_cols):
    count = 0
    for col in numeric_cols:
        val = row[col]
        if pd.isna(val) or str(val).strip() in ['', 'NaN', 'None', 'nan', 'none']:
            count += 1
    return count

missing_counts = df.apply(lambda row: count_missing(row, numeric_cols), axis=1)
df = df[missing_counts == 0].reset_index(drop=True)
```

### Step 1: Parse Numeric Formats

Parse raw values to clean floats, handling scientific notation, European decimals, and whitespace:

```python
import pandas as pd
import numpy as np

def parse_value(value):
    if pd.isna(value):
        return np.nan
    s = str(value).strip()
    if s == '' or s.lower() == 'nan':
        return np.nan
    if 'e' in s.lower():
        try:
            return float(s)
        except ValueError:
            pass
    if ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return np.nan

for col in numeric_cols:
    df[col] = df[col].apply(parse_value)
```

### Step 2: Unit Conversion (Range-Based Detection)

If a value falls outside the expected range (Min/Max) defined in `reference/ckd_lab_features.md`, try each conversion factor until one brings the value into range. Do NOT clamp values.

```python
def convert_unit_if_needed(value, column, reference_ranges, conversion_factors):
    if pd.isna(value):
        return value
    if column not in reference_ranges:
        return value
    min_val, max_val = reference_ranges[column]
    if min_val <= value <= max_val:
        return value
    factors = conversion_factors.get(column, [])
    for factor in factors:
        converted = value * factor
        if min_val <= converted <= max_val:
            return converted
    return value  # No conversion worked - return original

for col in numeric_cols:
    df[col] = df[col].apply(lambda x: convert_unit_if_needed(x, col, reference_ranges, conversion_factors))
```

**Example**: Serum Creatinine — Expected range: 0.2–20.0 mg/dL. Value = 673.4 (outside range) → likely µmol/L. Try factor 0.0113: 673.4 × 0.0113 = 7.61 mg/dL ✓

**Floating point precision**: Use a 5% tolerance and clamp edge cases.

### Step 3: Format Output (2 Decimal Places)

```python
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '')
```

## Feature Reference

See `reference/ckd_lab_features.md` for the complete dictionary of 60 CKD-related lab features including feature key, description, Min/Max ranges, original unit, and bidirectional conversion formulas.

## Key Constraints

- Parse formats first, then convert units, then format output
- Try all conversion factors for features with multiple alternative units
- Round to 2 decimal places for clinical lab standard precision
- Validate results are within expected physiological ranges after harmonization