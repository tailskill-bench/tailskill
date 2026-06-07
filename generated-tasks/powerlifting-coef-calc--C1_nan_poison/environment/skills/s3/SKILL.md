---
name: s1
description: Powerlifting coefficient calculation with data quality handling
allowed-tools: Read Write Edit Bash
---

## Quick Start

```bash
python scripts/experiment_designer.py --input data/ --output results/
python scripts/feature_engineering_pipeline.py --target project/ --analyze
python scripts/model_evaluation_suite.py --config config.yaml --deploy
```

## Reference Documentation

- `references/statistical_methods_advanced.md`
- `references/experiment_design_frameworks.md`
- `references/feature_engineering_patterns.md`

## Common Commands

```bash
python -m pytest tests/ -v --cov
python scripts/train.py --config prod.yaml
docker build -t service:v1 .
kubectl apply -f k8s/
```

---

## Excel Files

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).

### Preserve Existing Templates
- Match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding Standards

- **Blue text (RGB: 0,0,255)**: Hardcoded inputs
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards

- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0`; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use formatting to display all zeros as "-", including percentages (`"$#,##0;($#,##0);-"`)
- **Percentages**: Default to 0.0% format
- **Multiples**: Format as 0.0x (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

- Place ALL assumptions in separate cells; use cell references instead of hardcoded values in formulas (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Verify cell references, check off-by-one errors in ranges, ensure consistency across projection periods
- Test edge cases (zero values, negative numbers); verify no unintended circular references

#### Documentation for Hardcodes
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: Use the `recalc.py` script; it auto-configures LibreOffice on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**Data Quality**: Input XLSX files may contain NaN/Inf in numeric columns. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/data/openipf.xlsx 8` to fill NaN/Inf with column medians, or use `df.fillna(df.median())` after loading.

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating values in Python and hardcoding them.

- ❌ `sheet['B10'] = total` (hardcodes value)
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

## Common Workflow

1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: If `status` is `errors_found`, check `error_summary` for types and locations; fix and recalculate

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
sheet = wb.active
sheet['A1'] = 'New Value'
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON:
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
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Remember row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Verify denominators before division to avoid #DIV/0!
- Use correct cross-sheet format (Sheet1!A1)

## Best Practices

- **pandas**: Best for data analysis, bulk operations, simple data export
- **openpyxl**: Best for complex formatting, formulas, Excel-specific features
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values; **warning**: saving replaces formulas with values permanently
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines

- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values