---
name: s1
description: "PDF/XLSX with financial model standards."
---

# PDF Processing
```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("doc.pdf")
text = "".join(p.extract_text() for p in reader.pages)
```
Merge: `PdfWriter().add_page(page)` for each page, then `writer.write()`
Tables: `pdfplumber` → `page.extract_tables()`
Encrypt: `writer.encrypt("userpw", "ownerpw")`

# XLSX Processing
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```
```python
from openpyxl import load_workbook
wb = load_workbook('f.xlsx')
wb.active['A1'] = 'New Value'
wb.save('out.xlsx')
```
Verify permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py`
Recalculate: `python recalc.py output.xlsx`

# Financial Model Standards
- Blue text = Hardcoded inputs; Black text = Formulas
- Years as text strings; Percentages as 0.0%
- Negatives use parentheses
- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
