---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero Formula Errors**: No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` in deliverables
- **Preserve Existing Templates**: Match existing format/style/conventions; template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless overridden by user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., `"2024"` not `"2,024"`)
- **Currency**: Use `$#,##0` format; ALWAYS specify units in headers (`"Revenue ($mm)"`)
- **Zeros**: Use number formatting to display as `"-"`, including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format (one decimal)
- **Multiples**: Format as `0.0x` for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions (growth rates, margins, multiples) in separate assumption cells
- Use cell references instead of hardcoded values: `=B5*(1+$B$6)` instead of `=B5*1.05`
- Document hardcodes with comment/note: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required for Formula Recalculation**: Use `recalc.py` for recalculating formula values. Auto-configures LibreOffice on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Production Environment**: CSV files may contain UTF-8 BOM markers. Use `encoding='utf-8-sig'` when reading, or run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root` to strip BOM from all CSV/text files.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating values in Python and hardcoding them.

### ❌ WRONG
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'  # Dynamic formula
```

This applies to ALL calculations — totals, percentages, ratios, differences. The spreadsheet must recalculate when source data changes.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `status: "errors_found"` and fix error types

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
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating Formulas

Excel files created/modified by openpyxl contain formula strings but not calculated values. Use `recalc.py`:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script auto-sets up LibreOffice macro on first run, recalculates all formulas in all sheets, scans ALL cells for Excel errors, and returns JSON with error locations and counts.

### Interpreting recalc.py Output
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## Formula Verification Checklist
- **Test 2-3 sample references**: Verify correct values before building full model
- **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- **Row offset**: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- **NaN handling**: Check for null values with `pd.notna()`
- **Division by zero**: Check denominators before using `/` in formulas
- **Cross-sheet references**: Use correct format (`Sheet1!A1`) for linking sheets

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: Saving with `data_only=True` permanently replaces formulas with values
- Formulas are preserved but not evaluated — use `recalc.py` to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- **Python code**: Write minimal, concise code without unnecessary comments; avoid verbose variable names and redundant operations
- **Excel files**: Add comments to cells with complex formulas or important assumptions; document data sources for hardcoded values