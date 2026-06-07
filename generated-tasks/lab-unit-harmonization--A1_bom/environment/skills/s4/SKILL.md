---
name: s1
description: Clinical laboratory data harmonization with unit conversion, format standardization, and data quality handling including encoding issues.
---

# Lab Unit Harmonization

## When to Use

- Harmonizing lab values across hospitals or health systems
- Converting between US conventional and SI units (e.g., mg/dL to µmol/L)
- Standardizing inconsistent numeric formats (scientific notation, European decimals)
- Preparing CKD lab panels for eGFR calculations or staging models

## Core Workflow

### Encoding Check (Pre-load)

Check for UTF-8 BOM markers before loading. Remove BOM bytes in-place:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/environment/data/ckd_lab_data.csv
```

### Step 0: Filter Incomplete Records

Exclude rows with any missing values before harmonization:

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

Convert raw values to clean floats, handling scientific notation, European decimals, and whitespace:

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

If a value falls outside the expected range defined in `reference/ckd_lab_features.md`, try each conversion factor until one brings it within range. Do NOT clamp values.

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
    return value

for col in numeric_cols:
    df[col] = df[col].apply(lambda x: convert_unit_if_needed(x, col, reference_ranges, conversion_factors))
```

**Floating-point precision**: Due to format conversions, some values may land slightly outside boundaries. Use a 5% tolerance and clamp edge cases.

### Step 3: Format Output (2 Decimal Places)

```python
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '')
```

## Key Rules

- **Parse formats first**: Clean scientific notation and European decimals before unit conversion
- **Use range-based detection**: Values outside expected ranges likely need unit conversion
- **Try all conversion factors**: Some features have multiple alternative units
- **Handle floating-point precision**: Use 5% tolerance for boundary checks; clamp edge cases
- **Round to 2 decimal places**: Standard precision for clinical lab results
- **Validate results**: Confirm values fall within expected physiological ranges

## Reference

- `reference/ckd_lab_features.md`: Complete feature dictionary with all conversion factors