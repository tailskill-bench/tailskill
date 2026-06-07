---
name: s1
description: "PDF, XLSX, and fuzzy matching with zero-width char handling."
---

# Zero-Width Character Handling

Strip zero-width Unicode characters (U+200B–U+200F):
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```
Manual: `''.join(c for c in s if unicodedata.category(c) != 'Cf')`

# PDF Processing

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```
- Tables: `page.extract_tables()`

# XLSX Processing

Read: `pd.read_excel('file.xlsx')`

Edit existing:
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
wb.save('modified.xlsx')
```

# Fuzzy Matching

```python
from rapidfuzz import fuzz, process
best_match = process.extractOne("query", choices, scorer=fuzz.ratio)
```

Normalize before matching:
```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())