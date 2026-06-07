---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Templates
- Match existing format, style, conventions when modifying

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
- **Currency**: Use `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: Default `0.0%` (one decimal)
- **Multiples**: Format as `0.0x` (e.g., EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples) in separate cells
- Use cell references, not hardcoded values: `=B5*(1+$B$6)` not `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` to recalculate formula values. The script auto-configures LibreOffice on first run.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

Applies to ALL calculations — totals, percentages, ratios, differences.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: If `status` is `errors_found`, check `error_summary` for error types and locations

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
- [ ] Column mapping confirmed (column 64 = BL, not BK)
- [ ] Row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] NaN handling: Check nulls with `pd.notna()`
- [ ] Division by zero: Check denominators before `/` in formulas
- [ ] Cross-sheet references use correct format (`Sheet1!A1`)

## Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving permanently loses formulas
- Formulas preserved but not evaluated — use `recalc.py` to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
- Convert string numerics: `pd.to_numeric(errors='coerce')` or run `python3 /root/.claude/skills/s1/scripts/clean_data.py`