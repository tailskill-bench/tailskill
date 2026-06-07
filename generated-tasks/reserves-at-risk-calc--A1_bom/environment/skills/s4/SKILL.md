---
name: s1
description: "Spreadsheet creation, editing, and analysis for financial data."
---

# Requirements
- No formula errors (#REF!, #DIV/0!, #VALUE!)
- **Blue**: Inputs, **Black**: Formulas, **Green**: Links, **Yellow**: Assumptions
- Use Excel formulas, not hardcoded values

# XLSX Processing

## Reading
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```
BOM: `encoding='utf-8-sig'` or `python3 /root/.claude/skills/s1/scripts/clean_data.py /root`

## Workflow
1. Choose tool: pandas for data, openpyxl for formulas/formatting
2. Create/Load → Modify → Save
3. Recalculate: `python3 /root/.claude/skills/s1/scripts/recalc.py <file>`

## Editing
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## openpyxl
- 1-based indices (row=1, column=1 = A1)
- `data_only=True` reads calculated values; saving with it loses formulas

## Color Coding
- **Blue text**: Hardcoded inputs
- **Black text**: Formulas and calculations
- **Green text**: Cross-sheet links
- **Yellow background**: Key assumptions

## Number Formats
- Years: text strings
- Percentages: 0.0% format
- Negative numbers: use parentheses