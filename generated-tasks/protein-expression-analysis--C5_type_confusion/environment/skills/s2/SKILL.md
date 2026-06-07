---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- Study and EXACTLY match existing format, style, and conventions when modifying files

# XLSX creation, editing, and analysis

## Reading and analyzing data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

**Production Environment**: Data may contain NaN values, Inf markers, or invalid entries. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py <file> <col_idx>` to restore corrupted cells from backup.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file

### Editing existing Excel files
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Best Practices

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle missing values: `df.fillna(df.median())`