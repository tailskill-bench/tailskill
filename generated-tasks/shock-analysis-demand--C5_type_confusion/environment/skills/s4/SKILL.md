---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format/style/conventions; template conventions override these guidelines

## Financial Models

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: Formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within same workbook
- **Red (255,0,0)**: External file links
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Construction
- Assumptions (growth rates, margins, multiples) in separate cells
- Cell references not hardcoded: `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes: "Source: [System/Document], [Date], [Reference], [URL]"

# XLSX Creation, Editing, and Analysis

## Critical Requirements

**LibreOffice Required**: Use `recalc.py` to recalculate formulas. Auto-configures on first run.

**Type Confusion Fix**: String-typed numerics break formulas. Run:
```
python3 /root/.claude/skills/s1/scripts/clean_data.py "/root/test - demand.xlsx"
```

**Use Formulas, Not Hardcoded Values**:
- ❌ `sheet['B10'] = total`
- ✅ `sheet['B10'] = '=SUM(B2:B9)'`

## Workflow
1. **Choose tool**: pandas (data/bulk) or openpyxl (formulas/formatting)
2. **Create/Load** → **Modify** → **Save**
3. **Recalculate** (mandatory with formulas): `python recalc.py output.xlsx`
4. **Verify**: Check JSON; if `status` is `errors_found`, review `error_summary`

## Recalculate
```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Verification Checklist
- Test 2-3 sample references
- Confirm column mapping (column 64 = BL, not BK)
- Excel rows 1-indexed (DataFrame row 5 = Excel row 6)
- Check nulls with `pd.notna()`
- Check denominators before `/` to avoid #DIV/0!
- Verify cell references
- Cross-sheet format: `Sheet1!A1`

## Library Notes

### openpyxl
- 1-based indices (row=1, column=1 = A1)
- `data_only=True` reads calculated values
- **Warning**: Saving after `data_only=True` loses formulas permanently
- Formulas preserved but unevaluated—use `recalc.py`

### pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Minimal, concise Python; no unnecessary comments
- Avoid verbose variables and redundant operations
- No unnecessary print statements