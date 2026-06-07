---
name: s1
description: "PDF/XLSX/fuzzy matching with BOM handling."
---

# BOM & Data Cleaning

Strip UTF-8 BOM from CSV/TXT/JSON in `/root/`:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```

# PDF Processing

```python
from pypdf import PdfReader
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

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

Requirements: Zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?). Use Excel formulas, not hardcoded values.

# Fuzzy Matching

```python
from rapidfuzz import fuzz, process
score = fuzz.ratio("Acme Corp", "Acme Corporation")
best_match = process.extractOne("new york jets", choices)
```

```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    text = text.replace("limited", "ltd").replace("corporation", "corp")
    return text