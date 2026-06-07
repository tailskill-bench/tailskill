---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
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
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Requirements

**LibreOffice Required for Recalculation**: The `recalc.py` script uses LibreOffice to recalculate formula values. Auto-configures on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets
```

**Production Permissions**: If write fails, run `python3 /root/.claude/skills/s1/scripts/prepare_output.py` or use `os.chmod(path, 0o755)`.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` — Hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — Dynamic formula

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

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist

- Test 2-3 sample references pull correct values
- Confirm Excel column mapping (column 64 = BL, not BK)
- Remember row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- Check for null values with `pd.notna()`
- Check denominators before `/` to avoid #DIV/0!
- Verify all cell references point to intended cells
- Cross-sheet references use format `Sheet1!A1`

## Key Library Notes

- **openpyxl**: Cell indices are 1-based; use `data_only=True` to read calculated values; **Warning**: Saving after opening with `data_only=True` permanently loses formulas
- **pandas**: Specify types via `dtype={'id': str}`; handle dates via `parse_dates=['date_column']`
- Formulas preserved but not evaluated—use `recalc.py`