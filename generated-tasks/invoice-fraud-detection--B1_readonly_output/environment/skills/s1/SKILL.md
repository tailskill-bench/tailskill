---
name: s1
description: "Combined PDF, XLSX, and fuzzy matching skills with filesystem permission handling."
---

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
wb.save('modified.xlsx')
```

Before saving, verify the output directory has write permissions:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/fraud_report.json
```

# Fuzzy Matching Guide

## rapidfuzz

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
