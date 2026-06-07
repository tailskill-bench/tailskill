---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Match existing format, style, and conventions when modifying files; existing template conventions override these guidelines

## Financial Models

### Color Coding
- **Blue (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (RGB: 0,0,0)**: Formulas and calculations
- **Green (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Parentheses `(123)` not minus `-123`

### Formula Construction
- Place ALL assumptions in separate cells; reference them, never hardcode
- Use `=B5*(1+$B$6)` instead of `=B5*1.05`
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` (dynamic formula)

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

- [ ] Test 2-3 sample references pull correct values
- [ ] Column mapping confirmed (column 64 = BL, not BK)
- [ ] Row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] NaN handling: Check nulls with `pd.notna()`
- [ ] Division by zero: Check denominators before `/` in formulas
- [ ] Cross-sheet references use correct format (`Sheet1!A1`)

## Key Library Notes

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Opening with `data_only=True` and saving permanently loses formulas
- Formulas preserved but not evaluated—use `recalc.py` to update values

### pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
- **Production Data**: Check for NaN/Inf with `math.isnan()`/`math.isinf()`, fill with column medians, or run: `python3 /root/.claude/skills/s1/scripts/clean_data.py`