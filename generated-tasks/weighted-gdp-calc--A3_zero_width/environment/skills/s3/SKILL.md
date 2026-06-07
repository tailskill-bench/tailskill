---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless otherwise stated by the user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0`; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display as "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values
- Example: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script (auto-configures LibreOffice on first run).

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets dict
```

**Production Note**: Input files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that break float parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/gdp.xlsx 4` to strip them, or filter `Cf`/`Cc` categories via `unicodedata.category(c)`.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

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

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output; fix `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` errors and recalculate

### Creating New Excel Files
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

### Editing Existing Excel Files
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

Returns JSON with `status`, `total_errors`, `total_formulas`, `error_summary`. If `status` is `errors_found`, fix errors and recalculate.

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Verify denominators before division to avoid `#DIV/0!`
- Use correct cross-sheet format: `Sheet1!A1`

## Key Library Notes

- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values; **Warning**: saving with `data_only=True` permanently replaces formulas with values
- For large files: `read_only=True` for reading, `write_only=True` for writing