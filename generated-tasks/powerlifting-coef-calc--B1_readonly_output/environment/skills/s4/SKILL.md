---
name: s1
description: Powerlifting coefficient calculation with data quality handling
allowed-tools: Read Write Edit Bash
---

## Quick Start & Commands

```bash
python scripts/experiment_designer.py --input data/ --output results/
python scripts/feature_engineering_pipeline.py --target project/ --analyze
python scripts/model_evaluation_suite.py --config config.yaml --deploy
```

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

## Excel Standards

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?). Existing template conventions ALWAYS override these guidelines.

### Color Coding
- **Blue (0,0,255):** Hardcoded inputs/scenario-changeable numbers
- **Black (0,0,0):** ALL formulas and calculations
- **Green (0,128,0):** Links from other worksheets in same workbook
- **Red (255,0,0):** External links to other files
- **Yellow background (255,255,0):** Key assumptions needing attention

### Number Formatting
- **Years:** Text strings (`"2024"` not `"2,024"`)
- **Currency:** `$#,##0`; specify units in headers (`"Revenue ($mm)"`)
- **Zeros:** Display as `"-"` including percentages (`$#,##0;($#,##0);-`)
- **Percentages:** `0.0%` (one decimal)
- **Multiples:** `0.0x` (EV/EBITDA, P/E)
- **Negatives:** Parentheses `(123)` not minus `-123`

### Formula Rules
- Place ALL assumptions in separate cells; use references not hardcoded values (`=B5*(1+$B$6)` not `=B5*1.05`)
- Verify cell references; check off-by-one errors in ranges
- Ensure consistent formulas across projection periods
- Test edge cases (zero, negative); verify no circular references
- Document hardcoded values: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

## XLSX Creation, Editing & Analysis

**LibreOffice Required:** Use `recalc.py` for formula recalculation. Auto-configures on first run.

**Output Path:** Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>` to fix permissions and remove stale files.

### Reading Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

df.to_excel('output.xlsx', index=False)
```

### CRITICAL: Use Formulas, Not Hardcoded Values

❌ **WRONG:**
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

✅ **CORRECT:**
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

### Workflow

1. **Choose tool:** pandas for data, openpyxl for formulas/formatting
2. **Create/Load** workbook
3. **Modify** data, formulas, formatting
4. **Save** to file
5. **Recalculate** (MANDATORY IF USING FORMULAS): `python recalc.py output.xlsx`
6. **Verify:** If `status` is `errors_found`, check `error_summary` for error types/locations, fix and recalculate

### Creating New Files

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

### Editing Existing Files

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

### Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON:
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

- [ ] Test 2–3 sample references before building full model
- [ ] Confirm Excel column mapping (column 64 = BL, not BK)
- [ ] Remember rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] Check null values with `pd.notna()`
- [ ] Check denominators before `/` in formulas (#DIV/0!)
- [ ] Verify all cell references point to intended cells (#REF!)
- [ ] Use correct cross-sheet format (`Sheet1!A1`)
- [ ] Test formulas on 2–3 cells before applying broadly
- [ ] Verify all referenced cells exist
- [ ] Test edge cases: zero, negative, very large values

## Library Notes

**openpyxl:** Cell indices 1-based. Use `data_only=True` to read calculated values (WARNING: saving replaces formulas with values permanently). Use `read_only=True`/`write_only=True` for large files. Formulas preserved but not evaluated—use `recalc.py`.

**pandas:** Specify dtypes (`dtype={'id': str}`), read specific columns (`usecols=['A','C','E']`), handle dates (`parse_dates=['date_column']`).

## Code Style

- Write minimal, concise Python without unnecessary comments
- Avoid verbose variable names and redundant operations
- Add comments for complex formulas or important assumptions
- Document data sources for hardcoded values