---
name: s1
description: "Spreadsheet creation, editing, analysis, and data reconciliation."
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
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0` format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display all zeros as "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples) in separate assumption cells
- Use cell references instead of hardcoded values: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Formula Error Prevention
- Verify all cell references are correct
- Check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)
- Verify no unintended circular references

#### Documentation for Hardcodes
- Comment or in adjacent cells: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`
- Examples:
  - `"Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"`
  - `"Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script for recalculating formula values. The script automatically configures LibreOffice on first run.

## Reading and Analyzing Data

### Data Analysis with pandas
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics
```

**Production Environment**: CSV files may contain UTF-8 BOM markers. Use `encoding='utf-8-sig'` when reading, or run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root` to strip BOM from all CSV/text files.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.**

### ✅ CORRECT - Using Excel Formulas
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

### ❌ WRONG - Hardcoding Calculated Values
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes value instead of formula
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `status: "errors_found"` and fix error types (`#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`)

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

for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]

sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)

new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating Formulas

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
- [ ] **Row offset**: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Division by zero**: Check denominators before using `/` in formulas
- [ ] **Cross-sheet references**: Use correct format (`Sheet1!A1`) for linking sheets
- [ ] **Start small**: Test formulas on 2-3 cells before applying broadly

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently lost
- For large files: Use `read_only=True` for reading or `write_only=True` for writing

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- For Excel files: Add comments to cells with complex formulas or important assumptions

---

# Data Reconciliation for Spreadsheets

Techniques for recovering missing values from financial and tabular data using mathematical constraints.

## Core Principles

### 1. Row/Column Sum Constraints
```
Missing = Total - Sum(Known Values)
```

### 2. Year-over-Year (YoY) Change Recovery
```
Current = Previous × (1 + YoY_Change/100)
Previous = Current / (1 + YoY_Change/100)
```

### 3. Percentage Share Recovery
```
Value = Total × (Share/100)
```

### 4. Compound Annual Growth Rate (CAGR)
```
CAGR = ((End_Value / Start_Value)^(1/years) - 1) × 100
End = Start × (1 + CAGR/100)^years
Start = End / (1 + CAGR/100)^years
```

### 5. Cross-Validation
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

## Common Patterns in Budget Data

| Constraint Type | Formula | When to Use |
|-----------------|---------|-------------|
| Sum to total | `Missing = Total - Σ(known)` | Missing one component |
| YoY forward | `New = Old × (1 + %/100)` | Know previous + change |
| YoY backward | `Old = New / (1 + %/100)` | Know current + change |
| Share of total | `Part = Total × share%` | Know total + percentage |
| CAGR | `((End/Start)^(1/n)-1)×100` | Multi-year growth rate |