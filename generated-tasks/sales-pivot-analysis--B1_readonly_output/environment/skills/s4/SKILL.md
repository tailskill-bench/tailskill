---
name: s1
description: "PDF processing and XLSX creation with pivot tables. ALWAYS use pdf skill instead of Read tool for PDF files. Use when: (1) Reading ANY PDF file, (2) Extracting tables from PDFs, (3) Creating spreadsheets with pivot tables, (4) Reading or analyzing Excel data, (5) Building multi-sheet workbooks"
---

# PDF Processing Guide

## IMPORTANT: Do NOT Use the Read Tool for PDFs

The Read tool cannot properly extract tabular data from PDFs — it shows only a limited preview of the first page's text.

- **DO**: Use `pdfplumber` as shown in this skill
- **DO NOT**: Use the Read tool to view PDF contents

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

Iterate over ALL pages (`for page in pdf.pages`) — continuation pages may lack headers.

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

### Clean Extracted Table Data

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]
    df = pd.DataFrame(table[1:], columns=table[0])

    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip()
```

### Handle Missing Headers

```python
table = pdf.pages[0].extract_tables()[0]
df = pd.DataFrame(table)
df.columns = ['Col1', 'Col2', 'Col3', 'Col4']
```

## Quick Reference

| Task | Code |
|------|------|
| Open PDF | `pdfplumber.open("file.pdf")` |
| Get pages | `pdf.pages` |
| Extract tables | `page.extract_tables()` |
| Extract text | `page.extract_text()` |
| Table to DataFrame | `pd.DataFrame(table[1:], columns=table[0])` |

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

### With openpyxl (for cell-level access)
```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active
value = ws['A1'].value

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

Before saving, ensure the output directory exists and is writable:

```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/output.xlsx
```

This helper script checks and fixes directory permissions, and creates missing directories as needed. Alternatively, handle inline:

```python
import os, stat
output_dir = os.path.dirname(output_path) or '.'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
elif not os.access(output_dir, os.W_OK):
    os.chmod(output_dir, stat.S_IRWXU)
```

## Creating Pivot Tables

**CRITICAL: All pivot tables MUST use `cacheId=0`**. Using any other cacheId (1, 2, etc.) will cause openpyxl to fail when reading the file back with `KeyError`.

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

#### Count by Category (Order Count)
```python
pivot.rowFields.append(RowColField(x=0))
pivot.dataFields.append(DataField(
    name="Order Count",
    fld=1,
    subtotal="count"
))
```

#### Two-Dimensional Pivot (Rows and Columns)
```python
pivot.pivotFields[0] = PivotField(axis="axisRow", showAll=False)
pivot.pivotFields[1] = PivotField(axis="axisCol", showAll=False)
pivot.pivotFields[3] = PivotField(dataField=True, showAll=False)

pivot.rowFields.append(RowColField(x=0))
pivot.colFields.append(RowColField(x=1))
pivot.dataFields.append(DataField(name="Revenue", fld=3, subtotal="sum"))
```

#### Multiple Data Fields
```python
pivot.dataFields.append(DataField(name="Order Count", fld=2, subtotal="count"))
pivot.dataFields.append(DataField(name="Total Revenue", fld=3, subtotal="sum"))
```

### Pivot Table Field Configuration Reference

| axis value | Meaning |
|------------|---------|
| `"axisRow"` | Field appears as row labels |
| `"axisCol"` | Field appears as column labels |
| `"axisPage"` | Field is a filter/slicer |
| (none) | Field not used for grouping |

| subtotal value | Aggregation |
|----------------|-------------|
| `"sum"` | Sum of values |
| `"count"` | Count of items |
| `"average"` | Average/mean |
| `"max"` | Maximum value |
| `"min"` | Minimum value |
| `"product"` | Product of values |
| `"stdDev"` | Standard deviation |
| `"var"` | Variance |

### Important Notes

1. **CRITICAL - cacheId must be 0**: ALL pivot tables must use `cacheId=0`. Using 1, 2, etc. will cause `KeyError` when reading the file
2. **Field indices must match**: The order of `cacheFields` must match your source data columns
3. **Location ref**: The `ref` in Location is approximate — Excel will adjust when opened
4. **Cache field count**: For categorical fields, set `count` parameter to approximate number of unique values
5. **Multiple pivots**: Each pivot table needs its own sheet for clarity
6. **Values populate on open**: Pivot table values are calculated when the file is opened in Excel/LibreOffice, not when created

## Working with Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb['SheetName']

ws['A1'] = 'New Value'
ws.insert_rows(2)

new_ws = wb.create_sheet('Analysis')

wb.save('modified.xlsx')