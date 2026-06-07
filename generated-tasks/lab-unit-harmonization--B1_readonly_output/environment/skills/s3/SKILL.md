---
name: s1
description: Clinical laboratory data harmonization with unit conversion, format standardization, and robust output handling.
---

# Lab Unit Harmonization

## When to Use

- Harmonizing lab values from multiple hospitals or health systems
- Converting between US conventional and SI units (e.g., mg/dL to µmol/L)
- Standardizing inconsistent numeric formats (scientific notation, European decimals)
- Preparing CKD lab panels for eGFR calculations or staging models

## Core Workflow

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

If a value falls outside the expected range (Min/Max) defined in `reference/ckd_lab_features.md`, try each conversion factor until one produces an in-range result.

- If value is within expected range → keep as-is
- If outside range, try each conversion factor from the reference
- Return the first converted value that falls within range
- If no conversion works, return original (do NOT clamp)

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

**Example**: Serum Creatinine — Expected range 0.2–20.0 mg/dL. Value 673.4 is outside range → likely µmol/L. Factor 0.0113: 673.4 × 0.0113 = 7.61 mg/dL ✓

**Floating-point precision**: Use a 5% tolerance and clamp values slightly outside the boundary due to format conversion artifacts.

### Step 3: Format Output (2 Decimal Places)

```python
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '')
```

Before writing output, ensure write permissions:

```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/ckd_lab_data_harmonized.csv
```

## Feature Reference

See `reference/ckd_lab_features.md` for the complete dictionary of 60 CKD-related lab features including feature keys, descriptions, Min/Max ranges, original units, and conversion factors.

### Features with Multiple Alternative Units

**Three-Unit Features (8 total):**

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

### Feature Categories

| Category | Count | Examples |
|----------|-------|----------|
| Kidney Function | 5 | Serum_Creatinine, BUN, eGFR, Cystatin_C |
| Electrolytes | 6 | Sodium, Potassium, Chloride, Bicarbonate |
| Mineral & Bone | 7 | Serum_Calcium, Phosphorus, Intact_PTH, Vitamin_D |
| Hematology/CBC | 5 | Hemoglobin, Hematocrit, RBC_Count, WBC_Count |
| Iron Studies | 5 | Serum_Iron, TIBC, Ferritin, Transferrin_Saturation |
| Liver Function | 2 | Total_Bilirubin, Direct_Bilirubin |
| Proteins/Nutrition | 4 | Albumin_Serum, Total_Protein, Prealbumin, CRP |
| Lipid Panel | 5 | Total_Cholesterol, LDL, HDL, Triglycerides |
| Glucose Metabolism | 3 | Glucose, HbA1c, Fructosamine |
| Uric Acid | 1 | Uric_Acid |
| Urinalysis | 7 | Urine_Albumin, UACR, UPCR, Urine_pH |
| Cardiac Markers | 4 | BNP, NT_proBNP, Troponin_I, Troponin_T |
| Thyroid Function | 2 | Free_T4, Free_T3 |
| Blood Gases | 4 | pH_Arterial, pCO2, pO2, Lactate |
| Dialysis-Specific | 2 | Beta2_Microglobulin, Aluminum |

## Key Constraints

- Parse formats first, then convert units
- Try all conversion factors for features with multiple alternative units
- Round to exactly 2 decimal places for clinical lab standard
- Validate results fall within expected physiological ranges after harmonization