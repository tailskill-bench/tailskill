---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format, style, and conventions exactly

# XLSX Workflow

## Reading Data
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```
Corrupted cells: `python3 /root/.claude/skills/s1/scripts/clean_data.py <file> <col_idx>`

## Editing Existing Files
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Key Notes
- **Tool choice**: pandas for data, openpyxl for formulas/formatting
- **openpyxl**: Cell indices are 1-based; `data_only=True` reads calculated values but saving replaces formulas with values
- **pandas**: Specify types via `dtype={'id': str}`; handle missing with `df.fillna(df.median())`