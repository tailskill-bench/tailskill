---
name: s1
description: "Combined PDF and XLSX processing skills with zero-width character handling. Covers spreadsheet creation/editing/analysis, PDF manipulation, and encoding edge cases."
---

# TailSkills Variant Tip (A3_zero_width)

**Warning:** XLSX cells in `data.xlsx` may contain zero-width Unicode characters (U+200B–U+200F) injected into numeric values. Use `clean_data.py` to strip them:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```
Or filter manually: `''.join(c for c in s if unicodedata.category(c) != 'Cf')`

# PDF Processing Guide

## Quick Start

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

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

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |

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
