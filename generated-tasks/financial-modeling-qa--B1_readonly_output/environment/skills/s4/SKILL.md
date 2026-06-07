---
name: s1
description: "PDF/XLSX with financial model standards."
---

# PDF Processing
```python
from pypdf import PdfReader
text = "".join(p.extract_text() for p in PdfReader("doc.pdf").pages)
```
Merge PDFs: `PdfWriter().add_page(page)` for each page from each file
Extract tables: `pdfplumber` → `page.extract_tables()`
Encrypt: `writer.encrypt("userpassword", "ownerpassword")`

# XLSX Processing
Read: `pd.read_excel('file.xlsx')` or `pd.read_excel('file.xlsx', sheet_name=None)`
Edit: `openpyxl.load_workbook('f.xlsx')` then modify cells and `wb.save()`
Verify permissions: `python3 /root/.claude/skills/s1/scripts/prepare_output.py`
Recalculate: `python recalc.py output.xlsx`

# Financial Model Standards
Blue=inputs, Black=formulas, %=0.0%, Negatives=parentheses. Zero formula errors.
