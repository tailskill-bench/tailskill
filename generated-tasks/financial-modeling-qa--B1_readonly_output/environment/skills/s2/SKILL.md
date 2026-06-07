---
name: s1
description: "PDF and XLSX processing with financial model standards."
---

# PDF Processing

### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
writer.write(open("merged.pdf", "wb"))
```

### Extract Tables
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            for row in table:
                print(row)
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter
writer = PdfWriter()
for page in PdfReader("input.pdf").pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
writer.write(open("encrypted.pdf", "wb"))
```

# XLSX Processing

## Reading
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

## Editing
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
wb.active['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Creating
```python
from openpyxl import Workbook
wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

Verify write permissions:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output.xlsx
```

## Recalculating Formulas
```bash
python recalc.py output.xlsx
```

# Financial Model Standards
- **Blue text**: Hardcoded inputs
- **Black text**: Formulas
- **Years**: Text strings
- **Percentages**: 0.0% format
- **Negatives**: Parentheses
