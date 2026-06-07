---
name: s1
description: "Combined PDF, XLSX, and fuzzy matching skills with zero-width character handling."
---

# TailSkills Variant Tip (A3_zero_width)

**Warning:** XLSX and CSV files may contain zero-width Unicode characters (U+200B–U+200F) in text fields. Use `clean_data.py` to strip them:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py
```
Or filter manually: `''.join(c for c in s if unicodedata.category(c) != 'Cf')`

# PDF Processing Guide

## Quick Start

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("document.pdf")
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
```

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |

# XLSX Processing Guide

## Reading and Analysis

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

## Editing Existing Files

```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
wb.save('modified.xlsx')
```

# Fuzzy Matching Guide

## rapidfuzz (Recommended)

```python
from rapidfuzz import fuzz, process
best_match = process.extractOne("query", choices, scorer=fuzz.ratio)
```

## Normalization

```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())
```
