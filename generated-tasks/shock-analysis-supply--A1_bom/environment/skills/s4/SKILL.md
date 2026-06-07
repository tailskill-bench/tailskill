---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every model MUST have ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless overridden by user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets in same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: `0.0%` (one decimal)
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references, not hardcoded values
- Use `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` to recalculate formulas. The script auto-configures LibreOffice on first run.

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**CSV BOM Handling**: Use `encoding='utf-8-sig'` when reading CSVs, or run `python3 /root/.claude/skills/s1/scripts/clean_data.py` to strip BOM.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` — Hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — Dynamic formula

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: Check JSON output; if `status` is `errors_found`, inspect `error_summary`

### Creating New Files
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

### Editing Existing Files
```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist

- [ ] Test 2-3 sample references pull correct values
- [ ] Confirm column mapping (column 64 = BL, not BK)
- [ ] Remember row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- [ ] Check null values with `pd.notna()`
- [ ] Guard division by zero before using `/` in formulas
- [ ] Verify all cell references point to intended cells
- [ ] Use correct cross-sheet format: `Sheet1!A1`

## Key Library Notes

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving permanently loses formulas
- Formulas preserved but not evaluated—use `recalc.py`

### pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`