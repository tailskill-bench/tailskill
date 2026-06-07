---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- **Zero Formula Errors**: Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).
- **Preserve Existing Templates**: Study and EXACTLY match existing format, style, and conventions. Existing template conventions ALWAYS override these guidelines.

## Financial Models

### Color Coding Standards
Unless overridden by user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Text strings (e.g., "2024" not "2,024")
- **Currency**: `$#,##0`; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: 0.0% (one decimal)
- **Multiples**: 0.0x (e.g., EV/EBITDA, P/E)
- **Negative numbers**: Parentheses (123) not minus -123

### Formula Construction Rules
- Place ALL assumptions in separate cells; use cell references (e.g., `=B5*(1+$B$6)` not `=B5*1.05`).
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` for recalculating formula values. Auto-configures LibreOffice on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Strip invisible Unicode**: `python3 /root/.claude/skills/s1/scripts/clean_data.py "/root/test - demand.xlsx"` — removes zero-width spaces, soft hyphens, etc. Handles all sheets in-place.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding.

```python
# WRONG
sheet['B10'] = df['Sales'].sum()  # Hardcodes value

# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output `error_summary` for error types and locations if `status` is `errors_found`

### Creating New Excel Files
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

### Editing Existing Excel Files
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

- Test 2-3 sample references to verify correct values before building full model
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Check denominators before using `/` in formulas (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Use correct format for cross-sheet references (Sheet1!A1)

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently lost
- Formulas preserved but not evaluated — use recalc.py to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements