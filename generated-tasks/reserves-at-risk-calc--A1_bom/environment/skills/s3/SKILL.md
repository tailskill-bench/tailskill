---
name: s1
description: "Spreadsheet creation, editing, and analysis for financial data."
license: Proprietary
---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
- No formula errors (#REF!, #DIV/0!, #VALUE!)

### Color Coding
- **Blue**: Inputs, **Black**: Formulas, **Green**: Links, **Yellow**: Assumptions

### Formula Construction Rules
- Always use Excel formulas instead of calculating values in Python and hardcoding them

# XLSX Creation, Editing, and Analysis

## Reading and Analyzing Data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

- For UTF-8 BOM in CSV files: use `encoding='utf-8-sig'` or run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root`

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate**: `python3 /root/.claude/skills/s1/scripts/recalc.py <file>`

## openpyxl Notes
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values