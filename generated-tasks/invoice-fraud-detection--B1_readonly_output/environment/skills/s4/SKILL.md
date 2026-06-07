---
name: s1
description: "PDF, XLSX, fuzzy matching."
---

# PDF & XLSX

PDF: `pypdf.PdfReader` for text, `pdfplumber` for tables
```python
from pypdf import PdfReader
text = "".join(p.extract_text() for p in PdfReader("doc.pdf").pages)
```

XLSX: `pd.read_excel()`, `openpyxl.load_workbook()` for editing
Permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py`

# Fuzzy Matching
`rapidfuzz.process.extractOne(query, choices, scorer=fuzz.ratio)`
