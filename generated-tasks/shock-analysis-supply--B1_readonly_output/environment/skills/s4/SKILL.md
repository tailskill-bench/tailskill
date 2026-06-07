---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Template conventions override these guidelines

## Financial Model Standards

**Color Coding**: Blue (0,0,255)=hardcoded inputs; Black (0,0,0)=formulas; Green (0,128,0)=cross-sheet links; Red (255,0,0)=external links; Yellow bg (255,255,0)=key assumptions

**Number Formatting**: Years as text ("2024"); Currency `$#,##0` with units in headers; Zeros as "-" via `$#,##0;($#,##0);-`; Percentages `0.0%`; Multiples `0.0x`; Negatives in parentheses `(123)`

**Formula Rules**: All assumptions in separate cells; use references not hardcoded values (`=B5*(1+$B$6)` not `=B5*1.05`); Document hardcodes: "Source: [System/Document], [Date], [Reference], [URL]"

# XLSX Operations

**LibreOffice Required**: `recalc.py` uses LibreOffice for recalculation. Auto-configures on first run.

**Production Permissions**: If write fails, run `python3 /root/.claude/skills/s1/scripts/prepare_output.py` or use `os.chmod(path, 0o755)`.

## CRITICAL: Use Formulas, Not Hardcoded Values

- ❌ `sheet['B10'] = total` — Hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — Dynamic formula

## Reading Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets
```

## Creating New Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

## Editing Existing Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculating Formulas (MANDATORY IF USING FORMULAS)

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Verify JSON output; if `status` is `errors_found`, review `error_summary`.

## Formula Verification Checklist

- Test 2-3 sample references pull correct values
- Confirm column mapping (column 64 = BL, not BK)
- Row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- Check null values with `pd.notna()`
- Check denominators before `/` to avoid #DIV/0!
- Verify cell references point to intended cells
- Cross-sheet references: `Sheet1!A1`

## Library Notes

- **openpyxl**: 1-based indices; `data_only=True` reads calculated values; **Warning**: Saving after `data_only=True` permanently loses formulas
- **pandas**: Specify types via `dtype={'id': str}`; handle dates via `parse_dates=['date_column']`
- Formulas preserved but not evaluated—use `recalc.py`