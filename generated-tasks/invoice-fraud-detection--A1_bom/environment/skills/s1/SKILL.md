---
name: s1
description: "Combined PDF, XLSX, and fuzzy matching skills with BOM handling. Covers document processing, spreadsheet analysis, and entity matching."
---

# TailSkills Variant Tip (A1_bom)

**Warning:** CSV/TXT/JSON files in `/root/` may contain a UTF-8 BOM (`\xef\xbb\xbf`) at the start. Use `clean_data.py` to strip it before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

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

## Extract Text with pdfplumber

```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

## Extract Tables

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
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

## Requirements

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Use Excel formulas, not hardcoded values

# Fuzzy Matching Guide

## Quick Start

```python
from difflib import SequenceMatcher
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
```

## rapidfuzz (Recommended)

```python
from rapidfuzz import fuzz, process
score = fuzz.ratio("Acme Corp", "Acme Corporation")
best_match = process.extractOne("new york jets", choices)
```

## Normalization before Matching

```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    text = text.replace("limited", "ltd").replace("corporation", "corp")
    return text
```
