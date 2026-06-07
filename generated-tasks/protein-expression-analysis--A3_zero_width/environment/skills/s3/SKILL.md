---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Output Requirements

## All Excel Files
- **Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve templates**: Match existing format/style/conventions exactly when modifying files. Existing conventions override these guidelines.

# XLSX Creation, Editing & Analysis

## Reading & Analyzing Data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
df.head()
df.describe()
```

**Production**: Strip invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that corrupt numeric parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py <file> <col_idx>` to remove them.

## Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load** → **Modify** → **Save**

### Editing Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active

for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]

sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### openpyxl Notes
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: Saving with `data_only=True` permanently replaces formulas with values

### pandas Notes
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`