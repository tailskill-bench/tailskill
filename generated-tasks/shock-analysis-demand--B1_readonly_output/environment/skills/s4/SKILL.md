---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Every model MUST have ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

## Financial Models

### Color Coding (unless overridden by user or template)
- **Blue (0,0,255)**: Hardcoded inputs / scenario-changeable numbers
- **Black (0,0,0)**: ALL formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024", not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting: `$#,##0;($#,##0);-`
- **Percentages**: 0.0% (one decimal)
- **Multiples**: 0.0x (e.g., EV/EBITDA, P/E)
- **Negatives**: Parentheses (123) not minus -123

### Formula Construction
- Place ALL assumptions in separate cells; reference them, never hardcode into formulas
- Use `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL]"

# XLSX Creation, Editing, and Analysis

## Requirements

**LibreOffice Required for Recalculation**: `recalc.py` uses LibreOffice (auto-configured on first run).

## Reading and Analyzing Data

- Use `pd.read_excel('file.xlsx')` for first sheet; `sheet_name=None` for all sheets dict
- Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py` to fix directory permissions before saving, or check with `os.access('/root', os.W_OK)`

## CRITICAL: Use Formulas, Not Hardcoded Values

- ❌ `sheet['B10'] = df['Sales'].sum()` — hardcodes value
- ✅ `sheet['B10'] = '=SUM(B2:B9)'` — dynamic formula

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify**: Check returned JSON; if `status` is `errors_found`, inspect `error_summary`

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

## Formula Verification Checklist
- Test 2-3 sample references before building full model
- Confirm column mapping (column 64 = BL, not BK)
- Remember row offset: DataFrame row 5 = Excel row 6 (1-indexed)
- Guard division by zero (#DIV/0!)
- Verify all cell references (#REF!)
- Cross-sheet references use format `Sheet1!A1`

## Library Notes
- **openpyxl**: Cell indices are 1-based; `data_only=True` reads calculated values but saving permanently loses formulas; formulas preserved but not evaluated — use `recalc.py`
- **pandas**: Specify dtypes via `dtype={'id': str}`; handle dates via `parse_dates=['date_column']`