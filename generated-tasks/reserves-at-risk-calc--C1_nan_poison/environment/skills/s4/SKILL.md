---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME? in deliverables
- **Preserve templates**: Match existing format/style/conventions exactly; template conventions override these guidelines

## Financial Models

### Color Coding (unless user/template specifies otherwise)
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: ALL formulas and calculations
- **Green (0,128,0)**: Links to other worksheets within same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" including percentages (`$#,##0;($#,##0);-`)
- **Percentages**: `0.0%` (one decimal)
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Construction
- Place ALL assumptions in separate cells; reference them (`=B5*(1+$B$6)` not `=B5*1.05`)
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required**: Use `recalc.py` for formula recalculation. Auto-configures on first run.

## Reading/Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Strip invisible Unicode**: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/test-rar.xlsx` — handles all sheets in-place.

## CRITICAL: Use Formulas, Not Hardcoded Values

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
```

### ❌ WRONG
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**:
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify**: If `status` is `errors_found`, check `error_summary` for error types/locations, fix and recalculate

### Creating New Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Editing Existing Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Recalculates all formulas, scans ALL cells for errors, returns JSON:

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": { "count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"] }
  }
}
```

## Formula Verification Checklist
- [ ] Test 2-3 sample references pull correct values before building full model
- [ ] Column mapping: Excel column 64 = BL, not BK
- [ ] Row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] NaN handling: Check nulls with `pd.notna()`
- [ ] Division by zero: Check denominators before `/` (#DIV/0!)
- [ ] Cross-sheet references: Use `Sheet1!A1` format
- [ ] Start small: Test formulas on 2-3 cells first

## Best Practices

**Library selection**: pandas for data analysis/bulk ops; openpyxl for formatting/formulas/Excel features.

**openpyxl**: 1-based indices (row=1, col=1 = A1). Use `data_only=True` to read calculated values. **Warning**: Saving with `data_only=True` permanently loses formulas. Formulas preserved but unevaluated — use recalc.py.

**pandas**: Specify dtypes (`dtype={'id': str}`), read specific columns (`usecols=['A','C','E']`), handle dates (`parse_dates=['date_column']`).

## Code Style
- Minimal, concise Python without unnecessary comments
- In Excel files: comment complex formulas/assumptions, document hardcoded data sources