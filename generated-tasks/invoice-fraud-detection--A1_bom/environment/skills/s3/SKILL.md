---
name: s1
description: "Combined PDF, XLSX, and fuzzy matching with BOM handling."
---

# BOM Handling

CSV/TXT/JSON files in `/root/` may contain a UTF-8 BOM (`\xef\xbb\xbf`). Strip it before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

# PDF Processing

## Extract Text

```python
from pypdf import PdfReader
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Extract Tables with pdfplumber

```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

# XLSX Processing

## Reading and Editing

```python
import pandas as pd
from openpyxl import load_workbook

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)

wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Requirements

- Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)
- Use Excel formulas, not hardcoded values

# Fuzzy Matching

## rapidfuzz (Recommended)

```python
from rapidfuzz import fuzz, process
score = fuzz.ratio("Acme Corp", "Acme Corporation")
best_match = process.extractOne("new york jets", choices)
```

## Normalization

```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    text = text.replace("limited", "ltd").replace("corporation", "corp")
    return text