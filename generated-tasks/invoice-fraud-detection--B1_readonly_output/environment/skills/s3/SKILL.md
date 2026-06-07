---
name: s1
description: "PDF, XLSX, fuzzy matching."
---

# PDF
```python
from pypdf import PdfReader
text = "".join(p.extract_text() for p in PdfReader("doc.pdf").pages)
```
Tables: `pdfplumber` → `page.extract_tables()`

# XLSX
```python
import pandas as pd; df = pd.read_excel('file.xlsx')
from openpyxl import load_workbook; wb = load_workbook('f.xlsx'); wb.save('out.xlsx')
```
Permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py`

# Fuzzy
```python
from rapidfuzz import fuzz, process
process.extractOne("query", choices, scorer=fuzz.ratio)
```
