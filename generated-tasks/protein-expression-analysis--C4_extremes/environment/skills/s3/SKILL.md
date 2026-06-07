---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format, style, conventions

# XLSX Creation, Editing & Analysis

## Reading & Analyzing
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```
- Validate/clean data before processing; run `python3 /root/.claude/skills/s1/scripts/clean_data.py <file> <col_idx>` to restore corrupted cells from backup.

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load** → **Modify** → **Save**

### Editing existing files
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Best Practices

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values
- **Warning**: Saving with `data_only=True` replaces formulas with values

### pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle missing: `df.fillna(df.median())`