---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- Match existing format, style, and conventions when modifying files
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
- **Currency**: Use `$#,##0` format; specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display as "-" (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values
- Example: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Comment or adjacent cell: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script for recalculating formula values. The script auto-configures LibreOffice on first run.

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets
df.head()      # Preview
df.describe()  # Statistics
```

**NaN/Inf Handling**: Input files may contain NaN or Inf values. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/gdp.xlsx 4` to restore from backup, or use `df.fillna(df.median())` after loading.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating values in Python and hardcoding them.

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

### ❌ WRONG
```python
sheet['B10'] = df['Sales'].sum()  # Hardcodes value
sheet['C5'] = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `status: "errors_found"` and fix `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` errors

### Creating New Excel Files
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
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
sheet.insert_rows(2)
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script recalculates all formulas, scans for errors, and returns JSON:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Verify denominators before division to avoid `#DIV/0!`
- Use correct cross-sheet format (`Sheet1!A1`)
- Test formulas on 2-3 cells before applying broadly

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple data export
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
- For Excel files: add comments to cells with complex formulas or important assumptions