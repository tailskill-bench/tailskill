---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero Formula Errors**: No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`
- **Preserve Existing Templates**: Match existing format/style; template conventions override these guidelines

## Financial Models

### Color Coding (unless overridden)
- **Blue (0,0,255)**: Hardcoded inputs/scenario-changeable
- **Black (0,0,0)**: Formulas/calculations
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
- **Assumptions in separate cells**: `=B5*(1+$B$6)` not `=B5*1.05`
- **Hardcode documentation**: Comment or adjacent cell: `"Source: [System/Document], [Date], [Reference], [URL]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required**: Use `recalc.py` (auto-configures on first run).

## Reading/Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets dict
```

**Invisible Unicode Fix**: Files may contain zero-width chars (U+200B/C/D) breaking float parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/gdp.xlsx 4` or filter `Cf`/`Cc` via `unicodedata.category(c)`.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

### ❌ WRONG
```python
sheet['B10'] = df['Sales'].sum()  # Hardcodes value
```

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY with formulas)**: `python recalc.py output.xlsx`
6. **Verify**: Check JSON output; fix errors and recalculate

### Creating New Files
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Editing Existing Files
```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON: `status`, `total_errors`, `total_formulas`, `error_summary`. If `status` is `errors_found`, fix and recalculate.

## Verification Checklist
- Test 2-3 sample references before full model
- Confirm column mapping (column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Verify denominators to avoid `#DIV/0!`
- Cross-sheet format: `Sheet1!A1`

## Library Notes
- **pandas**: Data analysis, bulk ops, simple export
- **openpyxl**: Formatting, formulas, Excel features
- Cell indices 1-based (row=1, col=1 = A1)
- `data_only=True` reads calculated values; **Warning**: saving with it permanently replaces formulas
- Large files: `read_only=True` / `write_only=True`