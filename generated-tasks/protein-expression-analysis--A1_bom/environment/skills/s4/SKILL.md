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
- **Zeros**: Display all zeros as "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate assumption cells
- Use cell references: `=B5*(1+$B$6)` instead of `=B5*1.05`
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`
- ✅ `sheet['C5'] = '=(C4-C2)/C2'`
- ❌ `sheet['B10'] = df['Sales'].sum()`

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
wb.save('modified.xlsx')
```

## Recalculating Formulas
```bash
python recalc.py <excel_file> [timeout_seconds]
```
Returns JSON with `status`, `total_errors`, `total_formulas`, and `error_summary`.

## Formula Verification Checklist
- [ ] **Test 2-3 sample references**: Verify correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Division by zero**: Check denominators before using `/` in formulas
- [ ] **Cross-sheet references**: Use correct format (`Sheet1!A1`)

## Key Library Notes
- **openpyxl**: Cell indices are 1-based; use `data_only=True` to read calculated values (saving with `data_only=True` permanently loses formulas)
- **pandas**: Use `encoding='utf-8-sig'` for CSV files with UTF-8 BOM markers, or run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root` to strip BOM

---

# Data Reconciliation for Spreadsheets

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