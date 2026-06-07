---
name: s1
description: "PDF processing and XLSX creation with pivot tables. ALWAYS use pdf skill instead of Read tool for PDF files. Use when: (1) Reading ANY PDF file, (2) Extracting tables from PDFs, (3) Creating spreadsheets with pivot tables, (4) Reading or analyzing Excel data, (5) Building multi-sheet workbooks"
---

# PDF Processing Guide

## IMPORTANT: Do NOT Use the Read Tool for PDFs

The Read tool cannot properly extract tabular data from PDFs. Always use `pdfplumber`.

## Table Extraction with pdfplumber

```python
import pdfplumber
import pandas as pd

all_tables = []

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) > 1:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined = pd.concat(all_tables, ignore_index=True)
```

Clean extracted data:

```python
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df = df.dropna(how='all')
df.columns = df.columns.str.strip()
```

Handle missing headers by assigning manually: `df.columns = ['Col1', 'Col2', ...]`

## Text Extraction

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
```

Use `page.extract_text(layout=True)` to preserve layout.

## Extract Multiple Tables and Create Mappings

Iterate ALL pages — tables often span multiple pages; continuation pages may lack headers.

```python
import pdfplumber
import pandas as pd

category_map = {}
product_map = {}

with pdfplumber.open("catalog.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table in tables:
            if not table or len(table) < 2:
                continue
            header = [str(cell).strip() if cell else '' for cell in table[0]]

            if 'CategoryID' in header and 'CategoryName' in header:
                for row in table[1:]:
                    if row and len(row) >= 2 and row[0]:
                        cat_id = int(row[0].strip())
                        cat_name = row[1].strip()
                        category_map[cat_id] = cat_name

            elif 'ProductID' in header and 'ProductName' in header:
                for row in table[1:]:
                    if row and len(row) >= 3 and row[0]:
                        try:
                            prod_id = int(row[0].strip())
                            prod_name = row[1].strip()
                            cat_id = int(row[2].strip())
                            product_map[prod_id] = (prod_name, cat_id)
                        except (ValueError, AttributeError):
                            continue
            else:
                for row in table:
                    if row and len(row) >= 3 and row[0]:
                        try:
                            prod_id = int(row[0].strip())
                            prod_name = row[1].strip()
                            cat_id = int(row[2].strip())
                            product_map[prod_id] = (prod_name, cat_id)
                        except (ValueError, AttributeError):
                            continue

product_to_category_name = {
    pid: category_map[cat_id]
    for pid, (name, cat_id) in product_map.items()
}
```

---

---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and pivot tables."
---

# XLSX Creation, Editing, and Analysis

## Reading Data

### With pandas (recommended for analysis)

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

Numeric fields may contain invisible Unicode characters. Clean before casting:

```python
import unicodedata

def clean_value(val):
    return ''.join(c for c in str(val) if unicodedata.category(c) not in ('Cf', 'Cc'))

df['numeric_col'] = df['numeric_col'].apply(lambda x: float(clean_value(x)))
```

Or use the helper script:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/income.xlsx --col 4
```

### With openpyxl (cell-level access)

```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active
value = ws['A1'].value

wb = load_workbook('file.xlsx', data_only=True)  # Read calculated values
```

## Creating Excel Files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active
ws.title = "Data"

ws['A1'] = 'Header'
ws.append(['Row', 'of', 'data'])

ws['A1'].font = Font(bold=True)
ws['A1'].fill = PatternFill('solid', start_color='2c3e50')

wb.save('output.xlsx')
```

## Creating Pivot Tables

**CRITICAL: All pivot tables MUST use `cacheId=0`**. Any other cacheId causes `KeyError` when reading back.

### Basic Pivot Table Structure

```python
from openpyxl import Workbook
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems

wb = Workbook()
data_ws = wb.active
data_ws.title = "SourceData"

data = [
    ["CategoryName", "ProductName", "Quantity", "Revenue"],
    ["Beverages", "Chai", 25, 450.00],
    ["Seafood", "Ikura", 12, 372.00],
]
for row in data:
    data_ws.append(row)

num_rows = len(data)

pivot_ws = wb.create_sheet("PivotAnalysis")

cache = CacheDefinition(
    cacheSource=CacheSource(
        type="worksheet",
        worksheetSource=WorksheetSource(
            ref=f"A1:D{num_rows}",
            sheet="SourceData"
        )
    ),
    cacheFields=[
        CacheField(name="CategoryName", sharedItems=SharedItems(count=8)),
        CacheField(name="ProductName", sharedItems=SharedItems(count=40)),
        CacheField(name="Quantity", sharedItems=SharedItems()),
        CacheField(name="Revenue", sharedItems=SharedItems()),
    ]
)

pivot = TableDefinition(
    name="RevenueByCategory",
    cacheId=0,
    dataCaption="Values",
    location=Location(
        ref="A3:B10",
        firstHeaderRow=1,
        firstDataRow=1,
        firstDataCol=1
    ),
)

pivot.pivotFields.append(PivotField(axis="axisRow", showAll=False))
pivot.pivotFields.append(PivotField(showAll=False))
pivot.pivotFields.append(PivotField(showAll=False))
pivot.pivotFields.append(PivotField(dataField=True, showAll=False))

pivot.rowFields.append(RowColField(x=0))
pivot.dataFields.append(DataField(
    name="Total Revenue",
    fld=3,
    subtotal="sum"
))

pivot.cache = cache
pivot_ws._pivots.append(pivot)

wb.save('output_with_pivot.xlsx')
```

### Common Pivot Table Configurations

- **Count by Category:** `pivot.dataFields.append(DataField(name="Order Count", fld=1, subtotal="count"))`
- **Two-Dimensional (Rows + Columns):** Set `axis="axisCol"` on a field, add `pivot.colFields.append(RowColField(x=1))`
- **Multiple Data Fields:** Append additional `DataField` entries with different `fld` and `subtotal` values

### Pivot Table Constraints

1. **`cacheId` must be 0** — other values cause `KeyError`
2. `cacheFields` order must match source data columns
3. Location `ref` is approximate — Excel adjusts when opened
4. Set `count` parameter for categorical fields to approximate unique values
5. Each pivot table needs its own sheet
6. Pivot values populate when opened in Excel/LibreOffice, not at creation

## Working with Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb['SheetName']

ws['A1'] = 'New Value'
ws.insert_rows(2)

new_ws = wb.create_sheet('Analysis')

wb.save('modified.xlsx')