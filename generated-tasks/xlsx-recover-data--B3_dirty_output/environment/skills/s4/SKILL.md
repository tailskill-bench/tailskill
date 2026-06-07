---
name: s1
description: "Spreadsheet creation, editing, analysis, and data reconciliation with formula verification."
license: Proprietary. LICENSE.txt has complete terms
---

# Output Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME? in delivered files
- **Preserve existing templates**: Match existing format, style, and conventions exactly; template conventions override these guidelines

## Financial Models

### Color Coding (unless overridden by user/template)
- **Blue (RGB: 0,0,255)**: Hardcoded inputs/scenario numbers
- **Black (RGB: 0,0,0)**: All formulas and calculations
- **Green (RGB: 0,128,0)**: Cross-sheet links within same workbook
- **Red (RGB: 255,0,0)**: External file links
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: `0.0%` (one decimal)
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Construction
- Place ALL assumptions (growth rates, margins, multiples) in separate cells; reference them, not hardcoded values
- Use `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes with comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required**: Installed for formula recalculation via `recalc.py` (auto-configures on first run).

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

**Before writing**: Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>` to remove any corrupted file.

```python
df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas for ALL calculations (totals, percentages, ratios, differences). The spreadsheet must recalculate when source data changes.

```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Common Workflow
1. **Choose tool**: pandas for data/analysis, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify/fix errors**: Check JSON output; if `status` is `errors_found`, fix identified errors and recalculate

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

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script auto-configures LibreOffice macro on first run, recalculates all formulas across all sheets, scans for Excel errors (#REF!, #DIV/0!, etc.), and returns JSON:

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

## Formula Verification Checklist
- Test 2-3 sample references pull correct values before building full model
- Confirm Excel column mapping (column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Check denominators before using `/` in formulas
- Cross-sheet references use format `Sheet1!A1`
- Verify all referenced cells exist

## Library Notes
- **openpyxl**: 1-based indices (row=1, column=1 = A1); `data_only=True` reads calculated values but saving replaces formulas permanently
- **pandas**: Specify dtypes (`dtype={'id': str}`), use `usecols` for large files, `parse_dates` for dates

# Data Reconciliation

Recover missing values from financial/tabular data using mathematical constraints.

## Core Formulas

**Row/Column Sum**: `Missing = Total - Sum(Known Values)`

**YoY Change**: `Current = Previous × (1 + YoY_Change/100)` | `Previous = Current / (1 + YoY_Change/100)`

**Percentage Share**: `Value = Total × (Share/100)`

**CAGR**: `CAGR = ((End_Value / Start_Value)^(1/years) - 1) × 100` | `End = Start × (1 + CAGR/100)^years` | `Start = End / (1 + CAGR/100)^years`

## Cross-Validation
- Row totals match column totals?
- Percentage shares consistent?
- YoY changes recalculate correctly?

## Recovery Strategy
1. **Identify constraints**: What mathematical relationships exist?
2. **Find solvable cells**: Which missing values have enough information?
3. **Solve in order**: Chain dependencies may require sequential solving (e.g., recover A from Sheet 1 → calculate YoY in Sheet 2 → verify another value)
4. **Validate**: All constraints still hold