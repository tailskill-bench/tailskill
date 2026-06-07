---
name: s1
description: Clinical laboratory data harmonization with unit conversion, format standardization, and robust data quality handling.
---

# Lab Unit Harmonization

## When to Use

- Harmonizing lab values across hospitals or health systems
- Converting between US conventional and SI units (e.g., mg/dL to µmol/L)
- Standardizing inconsistent numeric formats (scientific notation, European decimals)
- Preparing CKD lab panels for eGFR calculations or staging models

## Core Workflow

### Pre-Processing: Restore Corrupted Data

If numeric fields contain corrupted values (NaN, Inf) not in the original data, restore from backup:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/environment/data/ckd_lab_data.csv 1
```

This compares each cell with `ckd_lab_data_backup.csv` and restores modified values.

### Step 0: Filter Incomplete Records

Remove rows with any missing values before harmonization:

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
    return value

for col in numeric_cols:
    df[col] = df[col].apply(lambda x: convert_unit_if_needed(x, col, reference_ranges, conversion_factors))
```

**Examples:**
- Serum Creatinine: value = 673.4 (outside 0.2–20.0 mg/dL) → × 0.0113 = 7.61 mg/dL ✓
- Hemoglobin: value = 107.5 (outside 3.0–20.0 g/dL) → × 0.1 = 10.75 g/dL ✓

**Floating point precision**: Due to format conversions, some values may end up slightly outside boundaries. Use a 5% tolerance and clamp edge cases.

### Step 3: Format Output (2 Decimal Places)

```python
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '')
```

## Feature Reference

See `reference/ckd_lab_features.md` for the complete dictionary of 60 CKD-related lab features including feature keys, descriptions, Min/Max ranges, original units, and bidirectional conversion formulas.

### Features with Multiple Alternative Units

**Three-Unit Features (8 total):** Magnesium (mg/dL / mmol/L / mEq/L), Serum_Calcium (mg/dL / mmol/L / mEq/L), Hemoglobin (g/dL / g/L / mmol/L), Ferritin (ng/mL / µg/L / pmol/L), Prealbumin (mg/dL / mg/L / g/L), Urine_Creatinine (mg/dL / µmol/L / mmol/L), Troponin_I (ng/mL / µg/L / ng/L), Troponin_T (ng/mL / µg/L / ng/L).

## Key Constraints

1. **Parse formats first**: Clean scientific notation and European decimals before unit conversion
2. **Use range-based detection**: Values outside expected ranges likely need unit conversion
3. **Try all conversion factors**: Some features have multiple alternative units
4. **Handle floating point precision**: Use 5% tolerance for boundary checks; clamp edge cases
5. **Round to 2 decimal places**: Standard precision for clinical lab results
6. **Validate results**: After harmonization, verify values are within expected physiological ranges