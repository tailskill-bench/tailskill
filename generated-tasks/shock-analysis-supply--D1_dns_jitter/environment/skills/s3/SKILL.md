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
Unless otherwise stated by the user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings ("2024" not "2,024")
- **Currency**: Use `$#,##0`; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: Default to `0.0%`
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values
- Example: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` to recalculate formula values. The script auto-configures LibreOffice on first run.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

❌ **WRONG**: `sheet['B10'] = df['Sales'].sum()`
✅ **CORRECT**: `sheet['B10'] = '=SUM(B2:B9)'`

This applies to ALL calculations—totals, percentages, ratios, differences.

## Common Workflow

1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or existing file
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

- Test 2-3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Check denominators before division to avoid #DIV/0!
- Verify all cell references point to intended cells
- Use correct cross-sheet format: `Sheet1!A1`

## Library Selection

- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving after opening with `data_only=True` permanently loses formulas
- Formulas preserved but not evaluated—use `recalc.py` to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`