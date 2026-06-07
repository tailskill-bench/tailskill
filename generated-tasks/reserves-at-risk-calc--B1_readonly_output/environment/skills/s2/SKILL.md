---
name: s1
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, data analysis, and visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Financial Model Color Coding
- **Blue text**: Hardcoded inputs
- **Black text**: Formulas and calculations
- **Green text**: Cross-sheet links
- **Yellow background**: Key assumptions

### Formula Construction Rules
- Always use Excel formulas instead of calculating values in Python and hardcoding them

# XLSX Creation, Editing, and Analysis

## Reading and Analyzing Data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate**: Use `python3 /root/.claude/skills/s1/scripts/recalc.py <file>`

### Editing Existing Excel Files
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values

## Saving Results
Before writing, run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output/rar_result.xlsx` to ensure write permissions and clean state.

```python
import os
os.makedirs('/root/output', exist_ok=True)
os.chmod('/root/output', 0o755)
wb.save('/root/output/rar_result.xlsx')