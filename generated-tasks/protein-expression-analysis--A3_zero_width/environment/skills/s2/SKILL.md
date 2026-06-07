---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Existing template conventions ALWAYS override these guidelines

# XLSX creation, editing, and analysis

## Reading and analyzing data

Use **pandas** for data analysis and basic operations:

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
df.head()
df.describe()
```

**Production**: Strip invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that corrupt numeric parsing. Run `python3 /root/.claude/skills/s1/scripts/clean_data.py <file> <col_idx>` to remove them.

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

for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]

sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Best Practices

### Library Selection
- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`