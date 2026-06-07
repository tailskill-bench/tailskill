---
name: s1
description: "PDF processing and XLSX creation with pivot tables. ALWAYS use instead of Read tool for PDFs. Use when: (1) Reading PDFs, (2) Extracting tables, (3) Creating spreadsheets with pivot tables, (4) Reading Excel data, (5) Building multi-sheet workbooks"
---

# PDF Processing Guide

## IMPORTANT: Do NOT Use the Read Tool for PDFs

**The Read tool cannot properly extract tabular data from PDFs.** It will only show a limited preview of the first page's text content, missing most of the data.

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
            if table and len(table) > 1:  # Has data
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine if same structure
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

When a PDF contains multiple related tables spanning multiple pages, extract from ALL pages and build lookup dictionaries:

```python
import pdfplumber
import pandas as pd

category_map = {}      # CategoryID -> CategoryName
product_map = {}       # ProductID -> (ProductName, CategoryID)

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
                # Continuation page (no header)
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

**Important:** Always iterate over ALL pages (`for page in pdf.pages`) — continuation pages may not have headers.

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
df.columns = ['Col1', 'Col2', 'Col3', 'Col4']  # Assign manually
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

---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and pivot tables. When Claude needs to work with spreadsheets (.xlsx files) for: (1) Creating new spreadsheets with data and formatting, (2) Reading or analyzing Excel data with pandas, (3) Creating pivot tables programmatically with openpyxl, (4) Building multi-sheet workbooks with source data and pivot table sheets, or (5) Any Excel file operations"
---

# XLSX Creation, Editing, and Analysis

## Reading Data

### With pandas (recommended for analysis)
```python
import pandas as pd

df = pd.read_excel('file.xlsx')  # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
df.head()      # Preview
df.describe()  # Statistics
```

When joining datasets on a key column, duplicate keys can cause row multiplication during merge. Deduplicate before joining:

```python
df = df.drop_duplicates(subset=['SA2_CODE'], keep='first')
```

Or use the helper script:
```bash
python3 /root/.claude/skills/s1/scripts/clean_data.py /root/income.xlsx --key SA2_CODE
```

### With openpyxl (for cell-level access)
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

**CRITICAL: All pivot tables MUST use `cacheId=0`**. Using any other cacheId will cause openpyxl to fail with `KeyError` when reading the file back.

### Basic Pivot Table Structure

```python
from openpyxl import Workbook
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems

# 1. Create workbook with source data
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

# 2. Create pivot table sheet
pivot_ws = wb.create_sheet("PivotAnalysis")

# 3. Define the cache
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

# 4. Create pivot table definition
pivot = TableDefinition(
    name="RevenueByCategory",
    cacheId=0,  # MUST be 0
    dataCaption="Values",
    location=Location(
        ref="A3:B10",
        firstHeaderRow=1,
        firstDataRow=1,
        firstDataCol=1
    ),
)

# 5. Configure pivot fields (indexed 0,1,2,3 matching cache field order)
pivot.pivotFields.append(PivotField(axis="axisRow", showAll=False))  # 0: CategoryName
pivot.pivotFields.append(PivotField(showAll=False))                  # 1: ProductName (unused)
pivot.pivotFields.append(PivotField(showAll=False))                  # 2: Quantity (unused)
pivot.pivotFields.append(PivotField(dataField=True, showAll=False))  # 3: Revenue (data)

# 6. Add row field reference
pivot.rowFields.append(RowColField(x=0))  # CategoryName

# 7. Add data field with aggregation
pivot.dataFields.append(DataField(
    name="Total Revenue",
    fld=3,
    subtotal="sum"
))

# 8. Attach cache and add to worksheet
pivot.cache = cache
pivot_ws._pivots.append(pivot)

wb.save('output_with_pivot.xlsx')
```

### Common Pivot Table Configurations

#### Count by Category
```python
pivot.rowFields.append(RowColField(x=0))
pivot.dataFields.append(DataField(name="Order Count", fld=1, subtotal="count"))
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
| `"axisRow"` | Row labels |
| `"axisCol"` | Column labels |
| `"axisPage"` | Filter/slicer |
| (none) | Not used for grouping |

| subtotal value | Aggregation |
|----------------|-------------|
| `"sum"` | Sum |
| `"count"` | Count |
| `"average"` | Average/mean |
| `"max"` | Maximum |
| `"min"` | Minimum |
| `"product"` | Product |
| `"stdDev"` | Standard deviation |
| `"var"` | Variance |

### Important Notes

1. **CRITICAL - cacheId must be 0**: ALL pivot tables must use `cacheId=0`
2. **Field indices must match**: `cacheFields` order must match source data columns
3. **Location ref**: Approximate — Excel adjusts when opened
4. **Cache field count**: For categorical fields, set `count` to approximate unique values
5. **Multiple pivots**: Each pivot table needs its own sheet
6. **Values populate on open**: Pivot values are calculated when opened in Excel/LibreOffice

## Working with Existing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb['SheetName']

ws['A1'] = 'New Value'
ws.insert_rows(2)

new_ws = wb.create_sheet('Analysis')

wb.save('modified.xlsx')