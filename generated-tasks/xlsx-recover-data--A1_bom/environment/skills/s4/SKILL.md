---
name: s1
description: "Spreadsheet creation, editing, analysis, and data reconciliation."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- **Zero Formula Errors**: Deliver with ZERO `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` errors.
- **Preserve Existing Templates**: EXACTLY match existing format, style, and conventions; template conventions ALWAYS override these guidelines.

## Financial Models

### Color Coding Standards
Unless overridden by user or template:
- **Blue (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (RGB: 0,0,0)**: ALL formulas and calculations
- **Green (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Text strings (`"2024"`, not `2,024`)
- **Currency**: `$#,##0`; specify units in headers (`"Revenue ($mm)"`)
- **Zeros**: Display as `"-"` via `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate cells; use cell references, not hardcoded values.
  - ✅ `=B5*(1+$B$6)` ❌ `=B5*1.05`
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`
- ❌ `sheet['B10'] = 5000` (hardcoded sum)

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
sheet = wb.active
sheet['A1'] = 'New Value'
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'
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
- Cross-sheet format: `Sheet1!A1`

## Key Library Notes
- **openpyxl**: 1-based indices; `data_only=True` reads calculated values (saving with this replaces formulas permanently)
- **pandas**: Use `dtype={'id': str}`, `usecols=['A','C']`, `parse_dates=['date_column']` as needed; `encoding='utf-8-sig'` for CSV with BOM markers

---

# Data Reconciliation for Spreadsheets

Recover missing values using mathematical constraints.

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
- Row totals match column totals?
- Percentage shares consistent?
- YoY changes recalculate correctly?

## Recovery Strategy
1. **Identify constraints**: What mathematical relationships exist?
2. **Find solvable cells**: Which missing values have enough information?
3. **Solve in order**: Some values depend on others (chain dependencies)
4. **Validate**: Check all constraints still hold