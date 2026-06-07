---
name: s1
description: "Combined PDF, XLSX, and fuzzy matching skills with zero-width character handling."
---

# Zero-Width Character Handling

XLSX/CSV files may contain zero-width Unicode characters (U+200B–U+200F). Strip them:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```
Manual filter: `''.join(c for c in s if unicodedata.category(c) != 'Cf')`

# PDF Processing

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

- Extract tables: `page.extract_tables()`

# XLSX Processing

Read with pandas:
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

Edit existing files:
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
wb.save('modified.xlsx')
```

# Fuzzy Matching

Use rapidfuzz:
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