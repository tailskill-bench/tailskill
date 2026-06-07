---
name: s1
description: "PDF and XLSX processing with BOM handling."
---
# BOM Handling
Files in `/root/` may contain UTF-8 BOM (`\xef\xbb\xbf`). Strip before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

# PDF Processing
```python
from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)
```
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                print(row)
```
```python
from pypdf import PdfReader, PdfWriter
writer = PdfWriter()
for page in PdfReader("input.pdf").pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as f:
    writer.write(f)
```

# XLSX Processing
**Constraints**: Zero formula errors (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`). Use Excel formulas, not hardcoded values. Place assumptions in separate cells.
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
wb.active['A1'] = 'New Value'
wb.save('modified.xlsx')
```
```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws['A1'] = 'Hello'
ws['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```
Recalculate: `python recalc.py output.xlsx`

**Formatting**: Blue text=hardcoded inputs, Black text=formulas, Years=text strings, Percentages=`0.0%`, Negatives=parentheses.