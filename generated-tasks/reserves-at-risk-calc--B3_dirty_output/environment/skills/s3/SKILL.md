---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

### Zero Formula Errors
- Deliver with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Financial Model Color Coding
- **Blue text**: Hardcoded inputs
- **Black text**: Formulas and calculations
- **Green text**: Cross-sheet links
- **Yellow background**: Key assumptions

### Formula Construction Rules
- Always use Excel formulas instead of calculating values in Python and hardcoding them

# XLSX Creation, Editing, and Analysis

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate**: `python3 /root/.claude/skills/s1/scripts/recalc.py <file>`

## openpyxl Notes
- Cell indices are 1-based (row=1, column=1 → cell A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving after opening with `data_only=True` replaces formulas with values

## Saving Results
Before writing, run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output/rar_result.xlsx` to ensure write permissions and clean prior artifacts.

```python
import os
os.makedirs('/root/output', exist_ok=True)
os.chmod('/root/output', 0o755)
wb.save('/root/output/rar_result.xlsx')