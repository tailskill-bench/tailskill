---
name: s1
description: "Combined PDF and XLSX processing skills with BOM handling. Covers spreadsheet creation/editing/analysis, PDF manipulation, and encoding edge cases."
---

# TailSkills Variant Tip (A1_bom)

**Warning:** CSV/TXT/JSON files in `/root/` may contain a UTF-8 BOM (`\xef\xbb\xbf`) at the start. Use `clean_data.py` to strip it before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

# PDF Processing Guide

## Common Operations

### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as output:
    writer.write(output)
```

### Extract Tables with pdfplumber
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                print(row)
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

# XLSX Processing Guide

## Requirements

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Use Excel formulas, not hardcoded values
- Place assumptions in separate cells

## Reading and Analysis

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

## Editing Existing Files

```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Creating New Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
wb.save('output.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py output.xlsx
```

The script recalculates formulas via LibreOffice and reports any errors.

## Financial Model Standards

- **Blue text**: Hardcoded inputs
- **Black text**: Formulas
- **Years**: Format as text strings
- **Percentages**: 0.0% format
- **Negative numbers**: Use parentheses