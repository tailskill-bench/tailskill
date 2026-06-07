---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format/style/conventions; existing conventions override these guidelines

## Financial Models

### Color Coding (unless overridden)
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: Formulas and calculations
- **Green (0,128,0)**: Links to other worksheets in same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-": `$#,##0;($#,##0);-`
- **Percentages**: `0.0%` (one decimal)
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Construction
- **Assumptions in separate cells**: Use cell references, not hardcoded values: `=B5*(1+$B$6)` not `=B5*1.05`
- **Hardcode documentation**: Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required for Recalculation**: Use `recalc.py` for recalculating formula values. Auto-configures on first run.

## Reading/Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Production Data**: Extreme values (0, -1, -999) may distort statistics. Run: `python3 /root/.claude/skills/s1/scripts/clean_data.py`

## CRITICAL: Use Formulas, Not Hardcoded Values

- ❌ WRONG: `sheet['B10'] = total` (hardcodes value)
- ✅ CORRECT: `sheet['B10'] = '=SUM(B2:B9)'`

Applies to ALL calculations: totals, percentages, ratios, differences.

## Workflow
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

Files created/modified by openpyxl contain formula strings but not calculated values. Use:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist
- [ ] **Test 2-3 sample references**: Verify correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (column 64 = BL, not BK)
- [ ] **Row offset**: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Check null values with `pd.notna()`
- [ ] **Division by zero**: Check denominators before `/` in formulas (#DIV/0!)
- [ ] **Wrong references**: Verify cell references point to intended cells (#REF!)
- [ ] **Cross-sheet references**: Use correct format (`Sheet1!A1`)

## Library Notes
- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving after opening with `data_only=True` permanently loses formulas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`