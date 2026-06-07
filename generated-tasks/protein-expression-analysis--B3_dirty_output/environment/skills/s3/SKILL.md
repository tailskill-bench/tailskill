---
name: s1
description: "Spreadsheet creation, editing, and analysis for proteomics data."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Match existing format/style when modifying files

# XLSX Operations

## Reading

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

**Verify integrity**: Check PK\x03\x04 header bytes. If corrupted, restore with `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/protein_expression.xlsx`.

## Editing

```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Best Practices

- **Tool choice**: pandas for data, openpyxl for formulas/formatting
- **openpyxl**: Cell indices are 1-based; `data_only=True` reads calculated values but saving replaces formulas with values
- **pandas**: Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`