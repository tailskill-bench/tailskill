---
name: s1
description: "PDF, XLSX processing and fuzzy matching."
---

# PDF Processing

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("document.pdf")
text = "".join(p.extract_text() for p in reader.pages)
```

```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
```

# XLSX Processing

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
```

```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
wb.save('modified.xlsx')
```

Verify write permissions:
```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/fraud_report.json
```

# Fuzzy Matching

```python
from rapidfuzz import fuzz, process
best = process.extractOne("query", choices, scorer=fuzz.ratio)
```
