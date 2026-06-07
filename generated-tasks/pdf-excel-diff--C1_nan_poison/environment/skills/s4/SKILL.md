---
name: pdf-xlsx
description: PDF manipulation and Excel spreadsheet toolkit for extraction, creation, merging, and analysis with formulas and formatting.
---

# PDF & Spreadsheet Processing Guide

## PDF Processing

### pypdf – Core Operations

```python
from pypdf import PdfReader, PdfWriter
```

- **Read/extract text**: `reader = PdfReader("document.pdf")` → iterate `reader.pages`, call `page.extract_text()`
- **Merge PDFs**: Create `PdfWriter()`, loop source files, `writer.add_page(page)` for each, `writer.write(output)`
- **Split PDF**: Loop `enumerate(reader.pages)`, write each page to a separate `PdfWriter`
- **Metadata**: `reader.metadata` → `.title`, `.author`, `.subject`, `.creator`
- **Rotate**: `page.rotate(90)`, then write via `PdfWriter`
- **Watermark**: `page.merge_page(watermark_page)` on each page
- **Encrypt**: `writer.encrypt("userpassword", "ownerpassword")` before save

### pdfplumber – Text & Table Extraction

```python
import pdfplumber
```

- **Text**: `page.extract_text()`
- **Tables**: `page.extract_tables()` → list of row-lists
- **Tables → Excel**: Build `pd.DataFrame(table[1:], columns=table[0])` per table, `pd.concat`, then `.to_excel("extracted_tables.xlsx", index=False)`

### reportlab – Create PDFs

- **Simple**: `canvas.Canvas("file.pdf", pagesize=letter)` → `drawString`, `line`, `save`
- **Multi-page**: `SimpleDocTemplate` + Platypus flowables (`Paragraph`, `Spacer`, `PageBreak`) → `doc.build(story)`

### Command-Line Tools

```bash
# pdftotext (poppler-utils)
pdftotext input.pdf output.txt
pdftotext -layout input.pdf output.txt
pdftotext -f 1 -l 5 input.pdf output.txt          # pages 1-5

# qpdf
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf

# pdftk
pdftk file1.pdf file2.pdf cat output merged.pdf
pdftk input.pdf burst
pdftk input.pdf rotate 1east output rotated.pdf

# Extract images
pdfimages -j input.pdf output_prefix
```

### OCR for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
```

# Excel Requirements & Workflow

## Zero Formula Errors

Every delivered Excel model MUST have ZERO formula errors (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`).

## Preserve Existing Templates

Study and EXACTLY match existing format, style, and conventions when modifying files. Existing template conventions ALWAYS override these guidelines.

## Financial Model Standards

### Color Coding (unless overridden)

| Color | RGB | Meaning |
|---|---|---|
| Blue | 0,0,255 | Hardcoded inputs / scenario-changeable numbers |
| Black | 0,0,0 | ALL formulas and calculations |
| Green | 0,128,0 | Links from other worksheets in same workbook |
| Red | 255,0,0 | External links to other files |
| Yellow bg | 255,255,0 | Key assumptions needing attention |

### Number Formatting

- **Years**: text strings (`"2024"`, not `2,024`)
- **Currency**: `$#,##0`; specify units in headers (`Revenue ($mm)`)
- **Zeros**: display as `-` → `$#,##0;($#,##0);-`
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: parentheses `(123)` not minus `-123`

### Formula Construction

- Place ALL assumptions in separate cells; reference them: `=B5*(1+$B$6)` not `=B5*1.05`
- Verify cell references for off-by-one errors; ensure consistent formulas across periods
- Test edge cases (zero, negative); verify no unintended circular references
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

## CRITICAL: Use Formulas, Not Hardcoded Values

```python
# WRONG
sheet['B10'] = df['Sales'].sum()
# CORRECT
sheet['B10'] = '=SUM(B2:B9)'
```

## Workflow

1. **Choose tool**: pandas for data analysis / bulk ops; openpyxl for formulas & formatting
2. **Create/Load**: `Workbook()` or `load_workbook('file.xlsx')`
3. **NaN/Inf cleanup** (C1 variant): `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/employees_current.xlsx 8` (second arg = 0-based column index)
4. **Modify**: add/edit data, formulas, formatting
5. **Save**: `wb.save('output.xlsx')`. On `PermissionError`, fix directory permissions with `os.chmod`
6. **Recalculate (MANDATORY)**: `python recalc.py output.xlsx`
7. **Verify**: check JSON output for errors; fix and recalculate if any found

### Creating New Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B1'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Editing Existing Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating Formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns JSON:

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": { "count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"] }
  }
}
```

## Formula Verification Checklist

- Test 2-3 sample references pull correct values before building full model
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- FY data often in columns 50+
- Search all occurrences, not just first match
- Check denominators before using `/` in formulas
- Cross-sheet references use `Sheet1!A1` format
- Test formulas on 2-3 cells before applying broadly
- Verify all referenced cells exist; test zero, negative, and very large values

## Library Notes

- openpyxl: Cell indices 1-based; `data_only=True` reads calculated values but saving with it permanently replaces formulas with values; formulas preserved but not evaluated—run `recalc.py`
- pandas: Specify dtypes (`dtype={'id': str}`), select columns (`usecols`), parse dates (`parse_dates`)

## Code Style

- Write minimal, concise Python without unnecessary comments
- For Excel: add cell comments on complex formulas or important assumptions; document data sources for hardcoded values