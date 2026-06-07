---
name: s1
description: Clinical laboratory data harmonization with unit conversion, format standardization, and robust data quality handling.
---

# Lab Unit Harmonization

## When to Use

- Converting between US conventional and SI units (e.g., mg/dL to µmol/L)
- Merging EHR data with different default unit conventions
- Standardizing inconsistent numeric formats (scientific notation, decimals)
- Cleaning whitespace, thousand separators, or European decimal formats

## Core Workflow

### Step 0: Restore Corrupted Cells (Preprocessing)

If a backup file exists, restore corrupted cells (extreme values like 0, -1, -999) before processing:

```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/environment/data/ckd_lab_data.csv 1
```

### Step 1: Filter Incomplete Records

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

### Step 2: Parse Numeric Formats

Parse raw values to clean floats, handling scientific notation (`1.5e3` → `1500.0`), European decimals (`12,34` → `12.34`), and whitespace (`"  45.2  "` → `45.2`):

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

### Step 3: Unit Conversion (Range-Based Detection)

If a value falls outside the expected range (Min/Max) defined in `reference/ckd_lab_features.md`, try each conversion factor until one brings the value into range.

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
    return value  # No conversion worked — return original (NO CLAMPING)

for col in numeric_cols:
    df[col] = df[col].apply(lambda x: convert_unit_if_needed(x, col, reference_ranges, conversion_factors))
```

**Example**: Serum Creatinine — expected range 0.2–20.0 mg/dL. Value 673.4 is outside range → try factor 0.0113: 673.4 × 0.0113 = 7.61 mg/dL ✓

### Step 4: Format Output (2 Decimal Places)

```python
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '')
```

## Features with Multiple Alternative Units

| Feature | Unit 1 | Unit 2 | Unit 3 |
|---------|--------|--------|--------|
| Magnesium | mg/dL | mmol/L | mEq/L |
| Serum_Calcium | mg/dL | mmol/L | mEq/L |
| Hemoglobin | g/dL | g/L | mmol/L |
| Ferritin | ng/mL | µg/L | pmol/L |
| Prealbumin | mg/dL | mg/L | g/L |
| Urine_Creatinine | mg/dL | µmol/L | mmol/L |
| Troponin_I | ng/mL | µg/L | ng/L |
| Troponin_T | ng/mL | µg/L | ng/L |

## Key Constraints

- **Parse formats before unit conversion**: Clean scientific notation and European decimals first
- **Try all conversion factors**: Some features have multiple alternative units — try each until one brings the value into range
- **No clamping**: If no conversion factor brings a value into range, return the original value unchanged
- **5% tolerance**: Allow clamping for floating-point edge cases within 5% of range boundaries
- **Round to 2 decimal places**: Standard precision for clinical lab results
- **Validate results**: After harmonization, confirm values fall within expected physiological ranges

## Additional Resources

- `reference/ckd_lab_features.md`: Complete feature dictionary with all conversion factors