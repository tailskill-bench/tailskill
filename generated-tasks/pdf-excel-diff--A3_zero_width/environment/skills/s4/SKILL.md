---
name: pdf-xlsx
description: PDF and Excel toolkit for extraction, creation, merging, and editing with formulas and formatting.
---

# PDF & Spreadsheet Processing

## PDF Operations

**Merge/Split/Rotate/Watermark/Encrypt (pypdf):**
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as output:
    writer.write(output)
```
Split: iterate `reader.pages`, write each to new `PdfWriter`. Rotate: `page.rotate(90)`. Watermark: `page.merge_page(watermark_page)`. Encrypt: `writer.encrypt("userpassword", "ownerpassword")`.

**Table Extraction (pdfplumber):**
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
if all_tables:
    pd.concat(all_tables, ignore_index=True).to_excel("extracted_tables.xlsx", index=False)
```

**Create PDFs (reportlab):**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph("Title", styles['Title']), Spacer(1, 12), Paragraph("Body.", styles['Normal'])]
doc.build(story)
```

**CLI Tools:**
```bash
pdftotext -layout input.pdf output.txt          # poppler-utils
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
pdfimages -j input.pdf output_prefix
```

**OCR Scanned PDFs:**
```python
from pdf2image import convert_from_path
import pytesseract
images = convert_from_path('scanned.pdf')
text = "\n".join(pytesseract.image_to_string(img) for img in images)
```

## Excel Requirements

- **Zero formula errors**: No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`.
- **Preserve templates**: Match existing format/style/conventions; template conventions override guidelines.

**Color Coding:** Blue=hardcoded inputs, Black=formulas, Green=cross-sheet links, Red=external links, Yellow bg=key assumptions.

**Number Formatting:** Years as text (`"2024"`), Currency `$#,##0`, Zeros as `"-"` (`$#,##0;($#,##0);-`), Percentages `0.0%`, Multiples `0.0x`, Negatives in parentheses.

**Formula Construction:** Assumptions in separate cells: `=B5*(1+$B$6)` not `=B5*1.05`. Document hardcodes with source/date/URL.

## XLSX Workflow

**CRITICAL: Use formulas, not hardcoded values:**
```python
# WRONG
sheet['B10'] = df['Sales'].sum()
# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
```

**Reading:**
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

**Strip zero-width characters:**
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/employees_current.xlsx
```

**Workflow:** 1) Choose tool (pandas=analysis/bulk; openpyxl=formulas/formatting) 2) Create/Load 3) Modify 4) Save (fix `PermissionError` with `os.chmod`) 5) Recalculate: `python recalc.py output.xlsx` 6) Verify JSON for errors.

**Creating/Editing:**
```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

**Recalc Output:** `{"status": "success", "total_errors": 0, "total_formulas": 42, "error_summary": {}}`. If `errors_found`, fix and rerun.

**Verification:** Test sample references, confirm column mapping (col 64=BL), Excel rows 1-indexed (DF row 5→Excel row 6), check `pd.notna()`, guard division by zero, cross-sheet uses `Sheet1!A1`.

**Key:** Cells 1-based, `data_only=True` loses formulas on save, large files use `read_only`/`write_only`, specify dtypes/parse_dates.