---
name: pdf-xlsx
description: PDF manipulation and Excel spreadsheet toolkit for extraction, creation, merging, and analysis with formulas and formatting.
---

# PDF & Spreadsheet Processing Guide

## PDF Operations

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

**Metadata / Rotate**
```python
reader = PdfReader("document.pdf")
meta = reader.metadata  # meta.title, meta.author
page = reader.pages[0]
page.rotate(90)
```

**Extract Tables to Excel**
```python
import pdfplumber, pandas as pd

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

**Create PDFs**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter
c.drawString(100, height - 100, "Hello World!")
c.save()
```

Multi-page: Use `SimpleDocTemplate`, `Paragraph`, `Spacer`, `PageBreak` from `reportlab.platypus` with `getSampleStyleSheet()`.

**CLI Tools**: `pdftotext -layout input.pdf output.txt` · `qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf` · `pdftk file1.pdf file2.pdf cat output merged.pdf` · `pdfimages -j input.pdf output_prefix`

**OCR** (requires `pytesseract`, `pdf2image`):
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
```

Watermark: `page.merge_page(watermark)`. Encrypt: `writer.encrypt("userpassword", "ownerpassword")`.

# Excel Requirements

## All Excel Files

- **Zero formula errors**: No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`
- **Preserve templates**: Match existing format/style. Existing conventions ALWAYS override guidelines.

## Financial Models

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black (0,0,0)**: ALL formulas and calculations
- **Green (0,128,0)**: Links to other worksheets in same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings ("2024" not "2,024")
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" including percentages: `$#,##0;($#,##0);-`
- **Percentages**: 0.0% · **Multiples**: 0.0x · **Negatives**: Parentheses (123) not -123

### Formula Construction
- ALL assumptions in separate cells; use cell references, not hardcoded values
  - ✅ `=B5*(1+$B$6)` ❌ `=B5*1.05`
- Verify cell references, check off-by-one errors, test edge cases, avoid circular references

### Hardcode Documentation
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

## CRITICAL: Use Formulas, Not Hardcoded Values

❌ `sheet['B10'] = df['Sales'].sum()`
✅ `sheet['B10'] = '=SUM(B2:B9)'`

## Common Workflow

1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Type confusion fix**: XLSX numeric columns may contain text markers ("N/A", "-", "TBD", "null"). Clean before comparison:
   ```bash
   python3 /root/.claude/skills/s1/scripts/clean_data.py /root/employees_current.xlsx 8
   ```
   Second argument is 0-based column index. After cleaning, load with `pd.read_excel()`.
4. **Modify**: Add/edit data, formulas, formatting
5. **Save**: If `PermissionError`:
   ```python
   import os, stat
   output_dir = os.path.dirname(os.path.abspath(output_file))
   os.makedirs(output_dir, exist_ok=True)
   os.chmod(output_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
   ```
6. **Recalculate (MANDATORY)**: `python recalc.py output.xlsx`
7. **Verify**: Check JSON output for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`

### Reading/Analyzing (pandas)

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
df.to_excel('output.xlsx', index=False)
```

### Creating (openpyxl)

```python
from openpyxl import Workbook
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

### Editing (openpyxl)

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON with `status`, `total_errors`, `total_formulas`, `error_summary`. If `status` is `errors_found`, fix and recalculate.

## Formula Verification Checklist

- Test 2-3 sample references before building full model
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check null values with `pd.notna()`
- FY data often in columns 50+
- Search all occurrences, not just first match
- Check denominators before `/` (#DIV/0!)
- Verify cell references (#REF!)
- Cross-sheet references: `Sheet1!A1`

## Key Tips

- openpyxl cell indices are 1-based
- `data_only=True` reads calculated values but saving permanently replaces formulas with values
- Large files: `read_only=True` / `write_only=True`
- Specify types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`