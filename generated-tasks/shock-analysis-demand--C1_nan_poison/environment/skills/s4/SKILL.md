---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and data handling."
license: Proprietary
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- No formula errors (#REF!, #DIV/0!, #VALUE!)

### Preserve Existing Templates
- Match existing format/style when modifying files

## Financial Models

### Color Coding Standards
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs and scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links to other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings ("2024" not "2,024")
- **Currency**: Use `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: Default to `0.0%`
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

- Place assumptions in separate cells; use cell references (`=B5*(1+$B$6)`)

#### Documentation for Hardcodes
- Comment or adjacent cell: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Tool Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Production data**: Run `python3 /root/.claude/skills/s1/scripts/clean_data.py "/root/test - demand.xlsx"` to replace NaN/Inf/None with column medians.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

```python
# WRONG: sheet['B10'] = df['Sales'].sum()
# CORRECT:
sheet['B10'] = '=SUM(B2:B9)'
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: If `status` is `errors_found`, check `error_summary` for error types and locations

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist
- Test 2-3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- Check for null values with `pd.notna()`
- Guard denominators against division by zero (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Use correct cross-sheet format: `Sheet1!A1`

## Library Notes

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving with `data_only=True` permanently loses formulas
- Formulas preserved but not evaluated; use `recalc.py` to update values

### pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Write minimal, concise Python without unnecessary comments
- Avoid unnecessary print statements