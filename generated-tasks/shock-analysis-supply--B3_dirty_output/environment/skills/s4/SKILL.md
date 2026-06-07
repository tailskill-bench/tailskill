---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format/style/conventions exactly; template conventions override these guidelines

## Financial Models

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: Formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within workbook
- **Red (255,0,0)**: External file links
- **Yellow background (255,255,0)**: Key assumptions

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" including percentages (`$#,##0;($#,##0);-`)
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Rules
- Place assumptions in separate cells; reference them (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Document hardcodes: "Source: [System/Document], [Date], [Reference], [URL]"

# XLSX Creation, Editing, and Analysis

**LibreOffice Required**: Use `recalc.py` for formula recalculation (auto-configures on first run).

## CRITICAL: Use Formulas, Not Hardcoded Values
- ❌ `sheet['B10'] = total`
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

## Workflow
1. Choose tool (pandas for data, openpyxl for formulas/formatting)
2. Create/load workbook
3. Modify data, formulas, formatting
4. Save to file
5. **Recalculate (MANDATORY with formulas)**: `python recalc.py output.xlsx`
6. Verify: Check JSON output; if `status` is `errors_found`, review `error_summary`

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

## Recalculate Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist
- [ ] Test 2-3 sample references pull correct values
- [ ] Column mapping: column 64 = BL, not BK
- [ ] Row offset: Excel rows 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] NaN handling: Check with `pd.notna()`
- [ ] Division by zero: Check denominators (#DIV/0!)
- [ ] Wrong references: Verify cell references (#REF!)
- [ ] Cross-sheet references: Use `Sheet1!A1` format

## Library Notes

### openpyxl
- 1-based indices (row=1, column=1 = A1)
- `data_only=True` reads calculated values
- **Warning**: Saving with `data_only=True` permanently loses formulas
- Formulas preserved but unevaluated; use recalc.py

### pandas
- Specify dtypes: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Minimal, concise Python; no unnecessary comments
- Avoid verbose variable names and print statements