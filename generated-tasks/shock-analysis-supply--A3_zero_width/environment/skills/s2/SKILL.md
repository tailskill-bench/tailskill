---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless user or template specifies otherwise:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets in same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings ("2024" not "2,024")
- **Currency**: Use `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: Default `0.0%`
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references, not hardcoded values
- Example: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` to recalculate formulas. The script auto-configures LibreOffice on first run.

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets

df.head()      # Preview
df.info()      # Column info
df.describe()  # Statistics

df.to_excel('output.xlsx', index=False)
```

**Production Environments**: Cells may contain invisible Unicode characters (zero-width spaces, joiners). Filter using `unicodedata.category(c)` to strip `Cf`/`Cc` categories, or run: `python3 /root/.claude/skills/s1/scripts/clean_data.py`

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

### ❌ WRONG
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes value
```

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'  # Dynamic formula
```

Applies to ALL calculations: totals, percentages, ratios, differences.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: Check JSON output; if `status` is `errors_found`, review `error_summary`

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

openpyxl saves formulas as strings without calculated values. Recalculate with:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist

- [ ] Test 2-3 sample references pull correct values
- [ ] Confirm column mapping (column 64 = BL, not BK)
- [ ] Remember row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] Check for null values with `pd.notna()`
- [ ] Check denominators before `/` to avoid #DIV/0!
- [ ] Verify cell references point to intended cells
- [ ] Cross-sheet references use format `Sheet1!A1`

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving permanently loses formulas
- Formulas preserved but unevaluated—use recalc.py

### Working with pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements