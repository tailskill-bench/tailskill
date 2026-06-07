---
name: s1
description: "PDF processing and XLSX creation with pivot tables. ALWAYS use instead of Read tool for PDFs. Use when: (1) Reading PDFs, (2) Extracting tables, (3) Creating spreadsheets with pivot tables, (4) Reading Excel data, (5) Building multi-sheet workbooks"
---

# PDF Processing Guide

## IMPORTANT: Do NOT Use the Read Tool for PDFs

The Read tool cannot extract tabular data from PDFs. Use `pdfplumber` as shown below.

## Table Extraction with pdfplumber

### Extract All Tables from Multi-Page PDF

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

### Text Extraction

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
```

### Extract Multiple Tables and Create Mappings

Iterate over ALL pages — continuation pages may lack headers.

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
                        category_map[int(row[0].strip())] = row[1].strip()
            elif 'ProductID' in header and 'ProductName' in header:
                for row in table[1:]:
                    if row and len(row) >= 3 and row[0]:
                        try:
                            product_map[int(row[0].strip())] = (row[1].strip(), int(row[2].strip()))
                        except (ValueError, AttributeError):
                            continue
            else:
                for row in table:
                    if row and len(row) >= 3 and row[0]:
                        try:
                            product_map[int(row[0].strip())] = (row[1].strip(), int(row[2].strip()))
                        except (ValueError, AttributeError):
                            continue

product_to_category_name = {
    pid: category_map[cat_id] for pid, (name, cat_id) in product_map.items()
}
```

### Clean Extracted Table Data

```python
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df = df.dropna(how='all')
df.columns = df.columns.str.strip()
```

### Handle Missing Headers

```python
df = pd.DataFrame(table)
df.columns = ['Col1', 'Col2', 'Col3', 'Col4']  # Assign manually
```

---
name: xlsx
description: "Spreadsheet creation, editing, and analysis with formulas, formatting, pivot tables. Use for: (1) Creating spreadsheets, (2) Reading/analyzing Excel data, (3) Pivot tables with openpyxl, (4) Multi-sheet workbooks"
---

# XLSX Creation, Editing, and Analysis

## Reading Data

### With pandas (recommended for analysis)

```python
import pandas as pd

df = pd.read_excel('file.xlsx')
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)
```

Deduplicate before joining to avoid row multiplication:

```python
df = df.drop_duplicates(subset=['SA2_CODE'], keep='first')
```

Or use the helper script:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/income.xlsx --key SA2_CODE
```

### With openpyxl (cell-level access)

```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active
value = ws['A1'].value

# Read calculated values (not formulas)
wb = load_workbook('file.xlsx', data_only=True)
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

**CRITICAL: All pivot tables MUST use `cacheId=0`.** Any other cacheId causes openpyxl to fail with `KeyError` when reading the file back.

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
            ref=f"A1:D{num_rows}", sheet="SourceData"
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
    location=Location(ref="A3:B10", firstHeaderRow=1, firstDataRow=1, firstDataCol=1),
)

pivot.pivotFields.append(PivotField(axis="axisRow", showAll=False))  # 0: CategoryName
pivot.pivotFields.append(PivotField(showAll=False))                  # 1: ProductName
pivot.pivotFields.append(PivotField(showAll=False))                  # 2: Quantity
pivot.pivotFields.append(PivotField(dataField=True, showAll=False))  # 3: Revenue

pivot.rowFields.append(RowColField(x=0))
pivot.dataFields.append(DataField(name="Total Revenue", fld=3, subtotal="sum"))

pivot.cache = cache
pivot_ws._pivots.append(pivot)
wb.save('output_with_pivot.xlsx')
```

### Common Pivot Configurations

- **Count by category**: `pivot.dataFields.append(DataField(name="Order Count", fld=1, subtotal="count"))`
- **Two-dimensional (rows + columns)**: Set `pivot.pivotFields[1] = PivotField(axis="axisCol", ...)` and add `pivot.colFields.append(RowColField(x=1))`
- **Multiple data fields**: Append additional `DataField` entries with different `fld` and `subtotal` values

### Critical Constraints

1. **cacheId must be 0** for all pivot tables
2. **Field indices must match**: `cacheFields` order must match source data columns
3. **Location ref** is approximate — Excel adjusts when opened
4. **Cache field count**: For categorical fields, set `count` to approximate unique values
5. **Multiple pivots**: Each needs its own sheet
6. **Values populate on open**: Pivot values calculate when opened in Excel/LibreOffice