---
name: pdf-xlsx
description: PDF manipulation and Excel spreadsheet toolkit for text/table extraction, creation, merging, and Excel editing with formulas and formatting.
---

# PDF & Spreadsheet Processing Guide

## PDF Processing

### pypdf – Core Operations

**Merge PDFs:**
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

**Split PDF:** Iterate `reader.pages`, write each to a new `PdfWriter`.

**Rotate / Watermark / Encrypt:** Use `page.rotate(90)`, `page.merge_page(watermark_page)`, or `writer.encrypt("userpassword", "ownerpassword")` before saving.

### pdfplumber – Text and Table Extraction

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

### reportlab – Create PDFs

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph("Title", styles['Title']), Spacer(1, 12), Paragraph("Body.", styles['Normal'])]
doc.build(story)
```

### Command-Line Tools

```bash
pdftotext -layout input.pdf output.txt          # poppler-utils
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
pdfimages -j input.pdf output_prefix
```

### OCR Scanned PDFs

Requires `pytesseract` and `pdf2image`:
```python
from pdf2image import convert_from_path
import pytesseract
images = convert_from_path('scanned.pdf')
text = "\n".join(pytesseract.image_to_string(img) for img in images)
```

---

# Excel Requirements

## All Excel Files

- **Zero formula errors**: Deliver with ZERO `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`.
- **Preserve templates**: Match existing format/style/conventions exactly; template conventions always override guidelines.

## Financial Models – Color Coding

| Color | RGB | Meaning |
|---|---|---|
| Blue | 0,0,255 | Hardcoded inputs / scenario-changeable |
| Black | 0,0,0 | Formulas and calculations |
| Green | 0,128,0 | Cross-sheet links (same workbook) |
| Red | 255,0,0 | External file links |
| Yellow bg | 255,255,0 | Key assumptions needing attention |

## Number Formatting

- **Years**: Text strings (`"2024"`, not `2,024`)
- **Currency**: `$#,##0`; specify units in headers (`Revenue ($mm)`)
- **Zeros**: Display as `"-"` including percentages: `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

## Formula Construction

- Place assumptions in separate cells; reference them: `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

---

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

```python
# WRONG
sheet['B10'] = df['Sales'].sum()
# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
```

Applies to totals, percentages, ratios, differences — all calculations.

## Reading Data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

**Zero-width characters**: Strip invisible Unicode (U+200B/C/D, U+FEFF) before processing:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/employees_current.xlsx
```

## Workflow

1. **Choose tool**: pandas for analysis/bulk ops; openpyxl for formulas/formatting.
2. **Create/Load** workbook.
3. **Modify** data, formulas, formatting.
4. **Save** — if `PermissionError`, fix directory permissions:
   ```python
   import os, stat
   os.makedirs(output_dir, exist_ok=True)
   os.chmod(output_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
   ```
5. **Recalculate** (mandatory when using formulas):
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify**: Check JSON output for errors; fix and recalculate if `status` is `errors_found`.

### Creating / Editing Files

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

For existing files: `wb = load_workbook('existing.xlsx')`, then edit and save.

## Recalc Output

```json
{"status": "success", "total_errors": 0, "total_formulas": 42, "error_summary": {}}
```

If `status` is `errors_found`, inspect `error_summary` for locations, fix, and rerun.

## Formula Verification Checklist

- Test 2–3 sample references pull correct values before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 → Excel row 6)
- Check `pd.notna()` for nulls; guard denominators against division by zero
- Cross-sheet references use `Sheet1!A1` format

## Key Reminders

- Cell indices are 1-based (`row=1, column=1` = A1)
- `data_only=True` reads cached values but saving permanently loses formulas
- Large files: use `read_only=True` / `write_only=True`
- Specify dtypes: `pd.read_excel('f.xlsx', dtype={'id': str})`
- Parse dates: `pd.read_excel('f.xlsx', parse_dates=['date_column'])`
- Add comments to cells with complex formulas or important assumptions