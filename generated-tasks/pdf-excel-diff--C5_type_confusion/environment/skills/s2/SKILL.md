---
name: pdf-xlsx
description: PDF manipulation and Excel spreadsheet toolkit for text/table extraction, creation, merging, and Excel file creation, editing, analysis with formulas and formatting.
---

# PDF & Spreadsheet Processing Guide

## PDF Processing

### Quick Start

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

### pypdf Operations

**Merge PDFs**
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as output:
    writer.write(output)
```

**Split PDF**
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

**Extract Metadata**
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
```

**Rotate Pages**
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.rotate(90)
writer.add_page(page)
with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

**Extract Text**
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

**Extract Tables**
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

**Extract Tables to Excel**
```python
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
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter
c.drawString(100, height - 100, "Hello World!")
c.line(100, height - 140, 400, height - 140)
c.save()
```

**Multi-page PDF with Platypus**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph("Report Title", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph("Body text. " * 20, styles['Normal']))
story.append(PageBreak())
story.append(Paragraph("Page 2", styles['Heading1']))
doc.build(story)
```

### Command-Line Tools

**pdftotext (poppler-utils)**
```bash
pdftotext input.pdf output.txt
pdftotext -layout input.pdf output.txt
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

**qpdf**
```bash
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

**pdftk**
```bash
pdftk file1.pdf file2.pdf cat output merged.pdf
pdftk input.pdf burst
pdftk input.pdf rotate 1east output rotated.pdf
```

### Common PDF Tasks

**OCR Scanned PDFs** (requires `pytesseract`, `pdf2image`)
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"
```

**Add Watermark**
```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

**Extract Images**
```bash
pdfimages -j input.pdf output_prefix
```

**Password Protection**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

---

# Excel Requirements

## All Excel Files

- **Zero formula errors**: Deliver with ZERO #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- **Preserve existing templates**: Match existing format, style, and conventions exactly. Existing conventions ALWAYS override guidelines.

## Financial Models

### Color Coding (unless user or template specifies otherwise)
- **Blue (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (RGB: 0,0,0)**: ALL formulas and calculations
- **Green (RGB: 0,128,0)**: Links to other worksheets in same workbook
- **Red (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" including percentages: `$#,##0;($#,##0);-`
- **Percentages**: 0.0% (one decimal)
- **Multiples**: 0.0x (EV/EBITDA, P/E)
- **Negative numbers**: Parentheses (123) not minus -123

### Formula Construction
- Place ALL assumptions in separate cells; use cell references, not hardcoded values in formulas
  - ✅ `=B5*(1+$B$6)` ❌ `=B5*1.05`
- Verify cell references, check off-by-one errors, ensure consistency across periods
- Test edge cases (zero, negative values); verify no unintended circular references

### Hardcode Documentation
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`
Examples:
- `"Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"`
- `"Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"`

---

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding.

❌ **WRONG**: `sheet['B10'] = df['Sales'].sum()`
✅ **CORRECT**: `sheet['B10'] = '=SUM(B2:B9)'`

This applies to ALL calculations—totals, percentages, ratios, differences.

## Common Workflow

1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Type confusion fix**: XLSX numeric columns may contain text markers ("N/A", "-", "TBD", "null"). Clean before comparison:
   ```bash
   python3 /root/.claude/skills/s1/scripts/clean_data.py /root/employees_current.xlsx 8
   ```
   Second argument is 0-based column index. After cleaning, load with `pd.read_excel()`.
4. **Modify**: Add/edit data, formulas, formatting
5. **Save**: Write to file. If `PermissionError`, fix directory permissions:
   ```python
   import os, stat
   output_dir = os.path.dirname(os.path.abspath(output_file))
   os.makedirs(output_dir, exist_ok=True)
   os.chmod(output_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
   ```
6. **Recalculate formulas (MANDATORY)**: `python recalc.py output.xlsx`
7. **Verify and fix errors**: Check JSON output for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`

### Reading and Analyzing Data (pandas)

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.head()
df.info()
df.describe()
df.to_excel('output.xlsx', index=False)
```

### Creating New Excel Files (openpyxl)

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

### Editing Existing Excel Files (openpyxl)

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'
wb.save('modified.xlsx')
```

## Recalculating Formulas

Excel files created/modified by openpyxl contain formula strings but not calculated values. Use `recalc.py`:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script automatically sets up LibreOffice macro on first run, recalculates all formulas, scans for errors, and returns JSON:

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

If `status` is `errors_found`, check `error_summary` for specific error types and locations, fix, and recalculate.

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- FY data often in columns 50+
- Search all occurrences, not just first match
- Check denominators before `/` in formulas (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Cross-sheet references use format `Sheet1!A1`
- Test formulas on 2-3 cells before applying broadly
- Verify all referenced cells exist
- Test edge cases: zero, negative, very large values

## Best Practices

- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features
- openpyxl cell indices are 1-based
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: Saving with `data_only=True` permanently replaces formulas with values
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style

- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements
- In Excel files: add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values
- Include notes for key calculations and model sections