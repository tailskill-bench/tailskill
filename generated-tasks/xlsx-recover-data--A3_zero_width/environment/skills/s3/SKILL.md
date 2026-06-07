---
name: s1
description: "Comprehensive spreadsheet creation, editing, analysis, and data reconciliation."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards
Unless otherwise stated by the user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or update

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0` format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display all zeros as "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
- Use cell references instead of hardcoded values in formulas
- Example: Use `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation Requirements for Hardcodes
- Comment or in adjacent cells. Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script for recalculating formula values. The script automatically configures LibreOffice on first run.

## Reading and Analyzing Data

### Data Analysis with pandas
For data analysis, visualization, and basic operations:

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Production Note**: Input files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) in numeric values that break float parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py <input_file> <sheet_index>` to strip these characters before processing.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.**

### ❌ WRONG — Hardcoding Calculated Values
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

### ✅ CORRECT — Using Excel Formulas
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the recalc.py script
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify and fix any errors**:
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix the identified errors and recalculate again

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
sheet.insert_rows(2)
sheet.delete_cols(3)

new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating Formulas

Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts

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

- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Cross-sheet references**: Use correct format (`Sheet1!A1`) for linking sheets

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
- Formulas are preserved but not evaluated — use recalc.py to update values

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
When generating Python code for Excel operations:
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

---

# Data Reconciliation for Spreadsheets

Techniques for recovering missing values from financial and tabular data using mathematical constraints.

## Core Principles

### 1. Row/Column Sum Constraints
When totals are provided, missing values can be recovered:

```
Missing = Total - Sum(Known Values)
```

### 2. Year-over-Year (YoY) Change Recovery
When you have percentage changes between periods:

```
Current = Previous × (1 + YoY_Change/100)
Previous = Current / (1 + YoY_Change/100)
```

### 3. Percentage Share Recovery
When you know a value's share of the total:

```
Value = Total × (Share/100)
```

### 4. Compound Annual Growth Rate (CAGR)
For multi-year growth analysis:

```
CAGR = ((End_Value / Start_Value)^(1/years) - 1) × 100
End = Start × (1 + CAGR/100)^years
Start = End / (1 + CAGR/100)^years
```

### 5. Cross-Validation
Always verify recovered values:
- Do row totals match column totals?
- Are percentage shares consistent?
- Do YoY changes recalculate correctly?

## Recovery Strategy

1. **Identify constraints**: What mathematical relationships exist?
2. **Find solvable cells**: Which missing values have enough information?
3. **Solve in order**: Some values may depend on others (chain dependencies)
4. **Validate**: Check all constraints still hold

## Chain Dependencies

Sometimes you must solve values in a specific order:
- Recover budget value A from Sheet 1
- Use A to calculate YoY percentage in Sheet 2
- Use that percentage to verify or calculate another value

Always map out dependencies before starting.