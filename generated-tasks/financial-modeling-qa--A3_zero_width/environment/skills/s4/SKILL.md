---
name: s1
description: "PDF/XLSX with zero-width char handling."
---

# Zero-Width Characters
Strip from `data.xlsx`: `python3 /root/.claude/skills/s1/scripts/clean_data.py`
Or: `''.join(c for c in s if unicodedata.category(c) != 'Cf')`

# PDF Processing

### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)
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

# XLSX Processing

## Requirements
- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Use Excel formulas, not hardcoded values
- Place assumptions in separate cells

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

## Recalculating Formulas
```bash
python recalc.py output.xlsx
```

## Financial Model Standards
- **Blue text**: Hardcoded inputs
- **Black text**: Formulas
- **Years**: Format as text strings
- **Percentages**: 0.0% format
- **Negative numbers**: Use parentheses