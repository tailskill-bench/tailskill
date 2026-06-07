---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format/style/conventions; template conventions override these guidelines

## Financial Models

### Color Coding (unless user/template specifies otherwise)
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: Formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within workbook
- **Red (255,0,0)**: External file links
- **Yellow background (255,255,0)**: Key assumptions

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting (`$#,##0;($#,##0);-`)
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Rules
- Place assumptions (growth rates, margins, multiples) in separate cells; use references: `=B5*(1+$B$6)` not `=B5*1.05`
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

**Production Data Cleaning**: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/test-rar.xlsx` strips invisible Unicode characters. Handles all sheets in-place.

## CRITICAL: Use Formulas, Not Hardcoded Values

- ❌ `sheet['B10'] = total` — Hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — Dynamic formula

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load** → **Modify** → **Save**
3. **Recalculate** (MANDATORY with formulas): `python recalc.py output.xlsx`
4. **Verify**: Check JSON for `status: "errors_found"`

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
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON: `{"status": "success", "total_errors": 0, "total_formulas": 42, "error_summary": {}}`

## Verification Checklist
- Test 2-3 sample references before full model
- Column mapping: column 64 = BL, not BK
- Row offset: Excel rows 1-indexed (DataFrame row 5 = Excel row 6)
- NaN handling: `pd.notna()`
- Division by zero: Check denominators
- Cross-sheet references: `Sheet1!A1`

## Best Practices

**Library Selection**: pandas for data/bulk ops; openpyxl for formatting/formulas/Excel features

**openpyxl**: 1-based indices; `data_only=True` reads calculated values (warning: saving replaces formulas with values)

**pandas**: Specify dtypes (`dtype={'id': str}`), columns (`usecols=['A','C','E']`), dates (`parse_dates=['date_column']`)

## Code Style
- Minimal, concise Python; no unnecessary comments
- Excel: Comment complex formulas/assumptions; document hardcoded data sources