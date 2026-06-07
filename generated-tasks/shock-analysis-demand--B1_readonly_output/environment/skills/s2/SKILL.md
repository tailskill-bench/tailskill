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

### Color Coding (unless overridden by user or template)
- **Blue (0,0,255)**: Hardcoded inputs / scenario-changeable numbers
- **Black (0,0,0)**: ALL formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024", not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: 0.0% (one decimal)
- **Multiples**: 0.0x (e.g., EV/EBITDA, P/E)
- **Negatives**: Parentheses (123) not minus -123

### Formula Construction
- Place ALL assumptions in separate cells; reference them, never hardcode into formulas
- Use `=B5*(1+$B$6)` not `=B5*1.05`
- Verify cell references, check off-by-one errors, ensure consistency across periods
- Test edge cases (zero, negative values); verify no unintended circular references
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL]"

# XLSX Creation, Editing, and Analysis

## Requirements

**LibreOffice Required for Recalculation**: `recalc.py` uses LibreOffice (auto-configured on first run).

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # all sheets dict

df.head()      # preview
df.info()      # column info
df.describe()  # statistics

df.to_excel('output.xlsx', index=False)
```

**Production**: Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py` to fix directory permissions before saving, or check with `os.access('/root', os.W_OK)`.

## Excel File Workflows

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = df['Sales'].sum()` — hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — dynamic formula

Applies to ALL calculations (totals, percentages, ratios, differences).

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: Check returned JSON; if `status` is `errors_found`, inspect `error_summary`

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
- Confirm column mapping (column 64 = BL, not BK)
- Remember row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- Check null values with `pd.notna()`
- Guard division by zero (#DIV/0!)
- Verify all cell references (#REF!)
- Cross-sheet references use format `Sheet1!A1`

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving permanently loses formulas
- Formulas preserved but not evaluated — use `recalc.py`

### Working with pandas
- Specify dtypes: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Write minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements