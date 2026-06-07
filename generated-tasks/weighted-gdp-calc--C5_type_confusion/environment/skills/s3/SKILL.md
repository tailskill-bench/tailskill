---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- **Zero Formula Errors**: Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- **Preserve Existing Templates**: Match existing format, style, and conventions exactly when modifying files. Template conventions ALWAYS override these guidelines.

## Financial Models

### Color Coding Standards
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., `"2024"` not `"2,024"`)
- **Currency**: Use `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Use formatting to display zeros as `"-"` (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default `0.0%`
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate assumption cells
- Use cell references, not hardcoded values (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Verify cell references; check for off-by-one errors
- Ensure consistent formulas across projection periods
- Test edge cases (zero, negative); verify no circular references

#### Documentation for Hardcodes
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` for recalculating formula values. The script auto-configures LibreOffice on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Non-numeric markers** (e.g. 'N/A', '-', '#REF!') in numeric columns cause type errors. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/gdp.xlsx 4` to restore numeric values, or use `pd.to_numeric(df[col], errors='coerce')` after loading.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` (dynamic formula)

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output `error_summary` for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`

### Creating New Excel Files

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

### Editing Existing Excel Files

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

Returns JSON:
```json
{"status": "success", "total_errors": 0, "total_formulas": 42, "error_summary": {}}
```

If `status` is `errors_found`, check `error_summary` for error types and locations, fix, and recalculate.

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Column mapping: Confirm Excel columns match (column 64 = BL, not BK)
- Row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- NaN handling: Check with `pd.notna()`
- Far-right columns: FY data often in columns 50+
- Division by zero: Check denominators before `/` in formulas
- Cross-sheet references: Use `Sheet1!A1` format
- Verify all referenced cells exist

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: Saving with `data_only=True` permanently replaces formulas with values
- For large files: Use `read_only=True` or `write_only=True`

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- For Excel files: Add comments to cells with complex formulas; document data sources for hardcoded values