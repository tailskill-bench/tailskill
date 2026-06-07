---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format, style, and conventions when modifying files

# XLSX Creation, Editing, and Analysis

## Reading Data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

**Production**: If output dirs are read-only, check `os.access(path, os.W_OK)`. Fix with `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root`.

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load** → **Modify** → **Save**

### Editing Existing Files
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Key Notes

### openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- `data_only=True` reads calculated values; saving replaces formulas with values

### pandas
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`