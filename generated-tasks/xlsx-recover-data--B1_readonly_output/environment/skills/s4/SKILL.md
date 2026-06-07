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
- **Green text (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0` format; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values
- Example: `=B5*(1+$B$6)` instead of `=B5*1.05`

#### Documentation for Hardcodes
- Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

- ✅ `sheet['B10'] = '=SUM(B2:B9)'`
- ❌ `sheet['B10'] = df['Sales'].sum()`

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `status: "errors_found"` and fix errors

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
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON with `status`, `total_errors`, `total_formulas`, and `error_summary`.

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Verify denominators before division to avoid `#DIV/0!`
- Use correct cross-sheet format: `Sheet1!A1`

## Key Library Notes

- **openpyxl**: Cell indices are 1-based; use `data_only=True` to read calculated values (warning: saving with this replaces formulas with values); formulas preserved but not evaluated — use `recalc.py`
- **pandas**: Specify data types via `dtype={'id': str}`; read specific columns via `usecols=['A', 'C', 'E']`; handle dates via `parse_dates=['date_column']`
- **PermissionError on save**: Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>`

---

# Data Reconciliation for Spreadsheets

Techniques for recovering missing values using mathematical constraints.

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
3. **Solve in order**: Some values depend on others (chain dependencies)
4. **Validate**: Check all constraints still hold

## Chain Dependencies

Some values must be solved in sequence — e.g., recover value A from Sheet 1, use A to calculate YoY in Sheet 2, then verify downstream values. Always map dependencies before starting.