---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel Files

- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Color coding**: Blue text = hardcoded inputs; Black = formulas; Green = cross-sheet links; Yellow background = key assumptions
- **Use Excel formulas** instead of calculating in Python and hardcoding values

# XLSX Creation, Editing, and Analysis

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing file
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate**: `python3 /root/.claude/skills/s1/scripts/recalc.py <file>`

## openpyxl Notes
- Cell indices are 1-based (row=1, column=1 → A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving after opening with `data_only=True` replaces formulas with values

## Saving Results
Run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output/rar_result.xlsx` before writing to ensure permissions and clean state.

```python
import os
os.makedirs('/root/output', exist_ok=True)
os.chmod('/root/output', 0o755)
wb.save('/root/output/rar_result.xlsx')