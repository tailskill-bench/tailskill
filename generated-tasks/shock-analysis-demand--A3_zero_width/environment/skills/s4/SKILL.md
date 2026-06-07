---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero Formula Errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve Templates**: Match existing format/style. Template conventions override these guidelines.

## Financial Models

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs
- **Black (0,0,0)**: Formulas/calculations
- **Green (0,128,0)**: Cross-sheet links (same workbook)
- **Red (255,0,0)**: External file links
- **Yellow bg (255,255,0)**: Key assumptions

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via `$#,##0;($#,##0);-`
- **Percentages**: 0.0%
- **Multiples**: 0.0x (EV/EBITDA, P/E)
- **Negatives**: Parentheses (123) not -123

### Formula Rules
- Assumptions in separate cells; use references (`=B5*(1+$B$6)` not `=B5*1.05`)
- Document hardcodes: "Source: [System/Document], [Date], [Reference], [URL]"

# XLSX Operations

**LibreOffice Required**: Use `recalc.py` for formula recalculation. Auto-configures on first run.

## Reading Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Strip invisible Unicode**: `python3 /root/.claude/skills/s1/scripts/clean_data.py "/root/test - demand.xlsx"` — removes zero-width spaces, soft hyphens, etc. Handles all sheets in-place.

## Use Formulas, Not Hardcoded Values

```python
# WRONG
sheet['B10'] = df['Sales'].sum()  # Hardcodes value

# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
```

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY with formulas)**: `python recalc.py output.xlsx`
6. **Verify**: Check JSON `error_summary` if `status` is `errors_found`

### Creating Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

### Editing Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculating

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Verification Checklist
- Test 2-3 sample references before building full model
- Confirm column mapping (column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check nulls with `pd.notna()`
- Check denominators before `/` (#DIV/0!)
- Verify cell references (#REF!)
- Cross-sheet format: Sheet1!A1

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel features

### openpyxl Notes
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving with `data_only=True` permanently loses formulas
- Formulas preserved but not evaluated — use recalc.py

### pandas Notes
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements