---
name: pdf-xlsx
description: PDF and Excel toolkit for extraction, creation, merging, OCR, and spreadsheet editing with formulas and formatting.
---

# PDF & Spreadsheet Processing Guide

## PDF Operations

### pypdf - Merge, Split, Metadata, Rotate, Watermark, Encrypt

```python
from pypdf import PdfWriter, PdfReader

# Merge
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as output:
    writer.write(output)
```

```python
# Split
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
meta = reader.metadata  # .title, .author, .subject, .creator

# Rotate
page = reader.pages[0]
page.rotate(90)

# Watermark
watermark = PdfReader("watermark.pdf").pages[0]
for page in reader.pages:
    page.merge_page(watermark)

# Encrypt
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
if all_tables:
    pd.concat(all_tables, ignore_index=True).to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph("Report Title", styles['Title']),
         Spacer(1, 12),
         Paragraph("Body text. " * 20, styles['Normal']),
         PageBreak(),
         Paragraph("Page 2", styles['Heading1'])]
doc.build(story)
```

### Command-Line Tools

```bash
# pdftotext (poppler-utils)
pdftotext input.pdf output.txt
pdftotext -layout input.pdf output.txt
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5

# qpdf
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf

# pdftk
pdftk file1.pdf file2.pdf cat output merged.pdf
pdftk input.pdf burst

# Extract images
pdfimages -j input.pdf output_prefix
```

### Scanned PDF OCR

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
```

# Excel Requirements & Standards

## Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

## Preserve Existing Templates
Study and EXACTLY match existing format, style, and conventions. Existing template conventions ALWAYS override these guidelines.

## Financial Model Color Coding
Unless stated by user or existing template:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets in same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

## Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: $#,##0; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" via formatting ("$#,##0;($#,##0);-")
- **Percentages**: 0.0% (one decimal)
- **Multiples**: 0.0x (EV/EBITDA, P/E)
- **Negatives**: Parentheses (123) not minus -123

## Formula Construction
- Place ALL assumptions in separate cells; reference them instead of hardcoding
- Use `=B5*(1+$B$6)` not `=B5*1.05`
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

```python
# WRONG
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Reading and Analyzing Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

**CSV BOM Note**: If garbled headers, use `encoding='utf-8-sig'` or run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root` to strip BOM from all CSV/TXT/JSON files.

## Creating New Excel Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

## Editing Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'
wb.save('modified.xlsx')
```

## Recalculating Formulas (MANDATORY)

LibreOffice is installed. Use `recalc.py` to recalculate all formulas:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script auto-configures LibreOffice on first run, recalculates all formulas, scans for errors, and returns JSON:

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

If `status` is `errors_found`, check `error_summary` for error types and locations, fix, and recalculate.

## Formula Verification Checklist

- [ ] Test 2-3 sample references before building full model
- [ ] Confirm Excel column mapping (column 64 = BL, not BK)
- [ ] Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] Check for null values with `pd.notna()`
- [ ] Check denominators before `/` to avoid #DIV/0!
- [ ] Cross-sheet references use format `Sheet1!A1`
- [ ] Test formulas on 2-3 cells before applying broadly

## Library Notes

**openpyxl**: Cell indices are 1-based. Use `data_only=True` to read calculated values (warning: saving with `data_only=True` permanently replaces formulas with values). For large files use `read_only=True`/`write_only=True`.

**pandas**: Specify dtypes to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`. For large files read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`. Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`.