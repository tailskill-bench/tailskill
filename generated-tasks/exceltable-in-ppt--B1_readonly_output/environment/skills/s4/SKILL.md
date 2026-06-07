---
name: s1
description: "PPTX manipulation toolkit and Excel/XLSX handling with formula support, OOXML editing, and template workflows."
---

# PPTX Operations

## Reading & Analysis

Text extraction: `python -m markitdown path-to-file.pptx`

Raw XML: `python ooxml/scripts/unpack.py <office_file> <output_dir>`

Key paths: `ppt/presentation.xml`, `ppt/slides/slide{N}.xml`, `ppt/notesSlides/notesSlide{N}.xml`, `ppt/comments/modernComment_*.xml`, `ppt/slideLayouts/`, `ppt/slideMasters/`, `ppt/theme/`, `ppt/media/`

Typography/colors: Read `ppt/theme/theme1.xml` (`<a:clrScheme>`, `<a:fontScheme>`). Slide XML: `<a:rPr>`, `<a:solidFill>`, `<a:srgbClr>`.

## New Presentation (No Template) — html2pptx Workflow

Design: web-safe fonts only (Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact). Strong contrast, clear hierarchy.

Layout: **Two-column preferred** for charts/tables (flexbox 40%/60%). Full-slide for featured content. **NEVER vertically stack** charts/tables below text.

1. **Read [`html2pptx.md`](html2pptx.md) entirely** (NEVER set range limits)
2. Create HTML per slide (720pt × 405pt for 16:9). Use `class="placeholder"` for chart/table areas. Rasterize gradients/icons as PNG via Sharp first.
3. Run JS using [`html2pptx.js`](scripts/html2pptx.js) to convert. Add charts/tables via PptxGenJS API. Save with `pptx.writeFile()`.
4. Validate: `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`

## Edit Existing Presentation — OOXML Workflow

1. **Read [`ooxml.md`](ooxml.md) entirely** (NEVER set range limits)
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML (primarily `ppt/slides/slide{N}.xml`)
4. **Validate**: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## New Presentation (Template) Workflow

1. Extract text: `python -m markitdown template.pptx > template-content.md` (read entirely). Thumbnails: `python scripts/thumbnail.py template.pptx`
2. Save `template-inventory.md`: slides are 0-indexed, list EVERY slide with index and layout code
3. Create `outline.md` with 0-based template mapping array. Match layout to content. Count pieces before selecting layout.
4. Duplicate/reorder: `python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52` (0-based, same index = duplicate)
5. Extract text: `python scripts/inventory.py working.pptx text-inventory.json` (read entirely, NEVER set range limits)

Inventory JSON structure:
```json
{
  "slide-0": {
    "shape-0": {
      "placeholder_type": "TITLE",
      "left": 1.5, "top": 2.0, "width": 7.5, "height": 1.2,
      "paragraphs": [
        {
          "text": "Paragraph text", "bullet": true, "level": 0,
          "alignment": "CENTER", "space_before": 10.0, "space_after": 6.0,
          "line_spacing": 22.4, "font_name": "Arial", "font_size": 14.0,
          "bold": true, "italic": false, "underline": false, "color": "FF0000"
        }
      ]
    }
  }
}
```

Shapes ordered top-to-bottom, left-to-right. Types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null. SLIDE_NUMBER excluded. `bullet: true` always includes `level`. Colors: `color` for RGB ("FF0000"), `theme_color` for theme ("DARK_1").

6. Generate `replacement-text.json`: reference only existing shapes. **ALL text shapes cleared** unless `"paragraphs"` provided. Use `"paragraphs"` (not `"replacement_paragraphs"`). Bullets auto left-aligned — do NOT set `alignment` when `"bullet": true`. Do NOT include bullet symbols (•, -, *). Include original properties. Use shape size for content length. Headers: `"bold": true`. List items: `"bullet": true, "level": 0`. Colors: `"color": "FF0000"` or `"theme_color": "DARK_1"`.

Example:
```json
{
  "slide-0": {
    "shape-0": {
      "paragraphs": [
        { "text": "New Title", "alignment": "CENTER", "bold": true },
        { "text": "First bullet point", "bullet": true, "level": 0 },
        { "text": "Red colored text", "color": "FF0000" }
      ]
    }
  }
}
```

7. Apply: `python scripts/replace.py working.pptx replacement-text.json output.pptx`

## Thumbnails & Slide Images

Thumbnails: `python scripts/thumbnail.py template.pptx [output_prefix]` — default 5 cols, max 30 slides/grid. `--cols N` (3–6).

Slide images: `soffice --headless --convert-to pdf template.pptx` then `pdftoppm -jpeg -r 150 template.pdf slide`

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
- **react-icons**: `npm install -g react-icons react react-dom`
- **sharp**: `npm install -g sharp`
- **LibreOffice**: `sudo apt-get install libreoffice`
- **Poppler**: `sudo apt-get install poppler-utils`
- **defusedxml**: `pip install defusedxml`

Read-only dirs: `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>`

---

# Excel Requirements

## Standards

**Zero formula errors**: No #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?. **Preserve existing templates**: match format/style/conventions exactly.

### Financial Model Colors
- **Blue (0,0,255)**: Hardcoded inputs
- **Black (0,0,0)**: Formulas/calculations
- **Green (0,128,0)**: Cross-sheet links within workbook
- **Red (255,0,0)**: External file links
- **Yellow background (255,255,0)**: Key assumptions

### Number Formatting
- Years: text strings ("2024" not "2,024")
- Currency: `$#,##0`; specify units in headers ("Revenue ($mm)")
- Zeros: display as "-" including percentages (`$#,##0;($#,##0);-`)
- Percentages: `0.0%`
- Multiples: `0.0x` (EV/EBITDA, P/E)
- Negatives: parentheses `(123)` not minus `-123`

### Formula Rules
- Assumptions in separate cells; use references (`=B5*(1+$B$6)` not `=B5*1.05`)
- Verify cell references; check off-by-one errors
- Consistent formulas across projection periods
- Test edge cases (zero, negative)
- Hardcode documentation: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

---

# XLSX Operations

**LibreOffice required** for `recalc.py` formula recalculation (auto-configures on first run).

## Reading

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                        # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

## CRITICAL: Use Formulas, Not Hardcoded Values

❌ **WRONG**: `sheet['B10'] = df['Sales'].sum()`
✅ **CORRECT**: `sheet['B10'] = '=SUM(B2:B9)'`

Applies to ALL calculations — totals, percentages, ratios, differences.

## Workflow

1. **Choose tool**: pandas for data/bulk ops, openpyxl for formulas/formatting
2. **Create/Load**: new workbook or existing file
3. **Modify**: data, formulas, formatting
4. **Save**: write to file
5. **Recalculate (MANDATORY with formulas)**: `python recalc.py output.xlsx`
6. **Verify**: check JSON for errors. If `status` is `errors_found`, check `error_summary`, fix, recalculate.

### Create New

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Edit Existing

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculation

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Returns:
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

- Test 2–3 sample references before full model
- Confirm column mapping (column 64 = BL, not BK)
- Excel rows 1-indexed (DataFrame row 5 = Excel row 6)
- Check nulls with `pd.notna()`
- Check denominators before `/` (#DIV/0!)
- Verify references point to intended cells (#REF!)
- Cross-sheet: `Sheet1!A1` format
- Verify all referenced cells exist

## Best Practices

**pandas**: data analysis, bulk ops, simple export. Specify dtypes: `pd.read_excel('file.xlsx', dtype={'id': str})`. Large files: `usecols=['A', 'C', 'E']`. Dates: `parse_dates=['date_column']`.

**openpyxl**: formatting, formulas, Excel features. Cells 1-based (row=1, column=1 = A1). `data_only=True` reads calculated values but **saving replaces formulas permanently**. Formulas preserved but unevaluated — use `recalc.py`.