---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Output Requirements

- Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Match existing format/style/conventions when modifying files; template conventions override these guidelines

## Financial Model Standards

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs/scenario-changeable
- **Black (0,0,0)**: Formulas/calculations
- **Green (0,128,0)**: Cross-sheet links (same workbook)
- **Red (255,0,0)**: External file links
- **Yellow background (255,255,0)**: Key assumptions

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Rules
- Assumptions in separate cells; use references not hardcoded values (`=B5*(1+$B$6)` not `=B5*1.05`)
- Document hardcodes: adjacent cell with `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required**: Use `recalc.py` to recalculate formulas (auto-configures on first run).

**CRITICAL: Use formulas, not hardcoded values**
- ❌ `sheet['B10'] = total`
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

### Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load** → **Modify** → **Save**
3. **Recalculate (MANDATORY)**: `python recalc.py output.xlsx`
4. **Verify**: Check JSON; if `status` is `errors_found`, review `error_summary`

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

### Recalculating Formulas
```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist
- Test 2-3 sample references pull correct values
- Confirm column mapping (column 64 = BL, not BK)
- Row offset: Excel rows 1-indexed (DataFrame row 5 = Excel row 6)
- Check null values with `pd.notna()`
- Check denominators before `/` to avoid #DIV/0!
- Verify cell references point to intended cells
- Cross-sheet references: `Sheet1!A1`

## Library Notes
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features
- openpyxl indices 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving loses formulas permanently
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
- Filter invisible Unicode: `python3 /root/.claude/skills/s1/scripts/clean_data.py`

## Code Style
- Minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements