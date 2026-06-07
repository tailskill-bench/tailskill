---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless otherwise stated by the user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use $#,##0 format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
- Use cell references instead of hardcoded values in formulas
- Example: Use =B5*(1+$B$6) instead of =B5*1.05

#### Documentation for Hardcodes
- Comment or in adjacent cells. Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script for recalculating formula values. The script automatically configures LibreOffice on first run.

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.**

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` (uses formula)

This applies to ALL calculations - totals, percentages, ratios, differences, etc.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix any errors**: If `status` is `errors_found`, check `error_summary` for specific error types and locations; fix and recalculate

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

Returns JSON with `status`, `total_errors`, `total_formulas`, and `error_summary` mapping error types to counts and locations.

## Data Analysis with pandas

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Production Environment**: Run `python3 /root/.claude/skills/s1/scripts/clean_data.py <filepath>` to detect and convert string-typed numeric cells back to proper numeric types.

## Formula Verification Checklist

- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets
- [ ] **Verify dependencies**: Check all cells referenced in formulas exist

## Key Library Notes

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently replaced with values
- Formulas are preserved but not evaluated — use recalc.py to update values

### pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`