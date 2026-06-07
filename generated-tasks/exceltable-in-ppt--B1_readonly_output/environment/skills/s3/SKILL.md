---
name: s1
description: "PPTX manipulation toolkit and Excel table handling for embedded spreadsheets in presentations."
---

# PPTX creation, editing, and analysis

## Reading and analyzing content

### Text extraction
```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`

Key file structures:
* `ppt/presentation.xml` — Main presentation metadata and slide references
* `ppt/slides/slide{N}.xml` — Individual slide contents
* `ppt/notesSlides/notesSlide{N}.xml` — Speaker notes
* `ppt/comments/modernComment_*.xml` — Comments
* `ppt/slideLayouts/` — Layout templates
* `ppt/slideMasters/` — Master slide templates
* `ppt/theme/` — Theme and styling
* `ppt/media/` — Images and media

Typography and color extraction: Read `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`). Examine slide XML for actual font usage (`<a:rPr>`) and colors (`<a:solidFill>`, `<a:srgbClr>`).

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint.

### Design Requirements
- State your design approach BEFORE writing code
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment

### Layout Rules
- **Two-column layout (PREFERRED)** for charts/tables: Header spanning full width, then two columns with flexbox (e.g., 40%/60%)
- **Full-slide layout**: Let featured content take up the entire slide
- **NEVER vertically stack** charts/tables below text in a single column

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. **NEVER set range limits.**
2. Create an HTML file for each slide (e.g., 720pt × 405pt for 16:9). Use `class="placeholder"` for chart/table areas. Rasterize gradients and icons as PNG images FIRST using Sharp.
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint. Add charts/tables to placeholders using PptxGenJS API. Save with `pptx.writeFile()`.
4. **Visual validation**: `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`. Check for text cutoff, overlap, positioning, contrast issues. Adjust and regenerate if needed.

## Editing an existing PowerPoint presentation

Work with raw OOXML: unpack the .pptx, edit XML, and repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) completely. **NEVER set range limits.**
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files (primarily `ppt/slides/slide{N}.xml` and related)
4. **CRITICAL**: Validate after each edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Creating a new PowerPoint presentation **using a template**

Duplicate and re-arrange template slides, then replace placeholder content.

### Workflow
1. **Extract template text AND create visual thumbnail grid**:
   - Extract text: `python -m markitdown template.pptx > template-content.md`
   - Read `template-content.md` entirely (**NEVER set range limits**)
   - Create thumbnails: `python scripts/thumbnail.py template.pptx`

2. **Analyze template and save inventory** as `template-inventory.md`:
   - Slides are 0-indexed (first slide = 0, last slide = count-1)
   - List EVERY slide individually with its index and layout code

3. **Create presentation outline** with template mapping:
   - Match layout structure to actual content (single-column for unified narrative, two-column for exactly 2 items, etc.)
   - Count content pieces BEFORE selecting layout
   - Verify each placeholder will be filled with meaningful content
   - Save `outline.md` with 0-based template mapping array

4. **Duplicate, reorder, and delete slides**:
   ```bash
   python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
   ```
   Slide indices are 0-based. Same index can appear multiple times to duplicate.

5. **Extract ALL text using `inventory.py`**:
   ```bash
   python scripts/inventory.py working.pptx text-inventory.json
   ```
   Read `text-inventory.json` entirely (**NEVER set range limits**).

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

   Key features: Shapes ordered by visual position (top-to-bottom, left-to-right). Placeholder types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null. Slide number shapes (SLIDE_NUMBER) automatically excluded. When `bullet: true`, `level` is always included. Colors: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1").

6. **Generate replacement text and save to JSON**:
   - Only reference shapes that exist in the inventory
   - **AUTOMATIC CLEARING**: ALL text shapes cleared unless you provide `"paragraphs"` for them
   - Add `"paragraphs"` field (not `"replacement_paragraphs"`)
   - Paragraphs with bullets are automatically left-aligned; do NOT set `alignment` when `"bullet": true`
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) in text
   - Include paragraph properties from the original inventory
   - Use shape size to determine appropriate content length
   - **ESSENTIAL FORMATTING**: Headers/titles: `"bold": true`. List items: `"bullet": true, "level": 0`. Preserve alignment. Include font properties when different from default. Colors: `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colors.
   - Save to `replacement-text.json`

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

7. **Apply replacements**:
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```
   The script validates shapes, clears all text shapes, applies new text with formatting, and saves.

## Creating Thumbnail Grids

```bash
python scripts/thumbnail.py template.pptx [output_prefix]
```

- Default: 5 columns, max 30 slides per grid (5×6)
- Custom prefix: `python scripts/thumbnail.py template.pptx workspace/my-grid`
- Adjust columns: `--cols 4` (range: 3–6; 3 cols = 12 slides/grid, 4 = 20, 5 = 30, 6 = 42)
- Slides are zero-indexed

## Converting Slides to Images

1. Convert PPTX to PDF: `soffice --headless --convert-to pdf template.pptx`
2. Convert PDF pages to JPEG: `pdftoppm -jpeg -r 150 template.pdf slide` (creates `slide-1.jpg`, `slide-2.jpg`, etc.)

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
- **react-icons**: `npm install -g react-icons react react-dom`
- **sharp**: `npm install -g sharp`
- **LibreOffice**: `sudo apt-get install libreoffice`
- **Poppler**: `sudo apt-get install poppler-utils`
- **defusedxml**: `pip install defusedxml`

> **Handling Read-Only Output Directories**: Before writing output files, ensure the directory is writable: `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>`

---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
Study and EXACTLY match existing format, style, and conventions when modifying files. Existing template conventions ALWAYS override these guidelines.

## Financial models

### Color Coding Standards
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0` format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%` format
- **Multiples**: Format as `0.0x` for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate assumption cells; use cell references instead of hardcoded values (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Verify all cell references are correct; check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)

### Documentation Requirements for Hardcodes
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

---

# XLSX creation, editing, and analysis

## Important Requirements

**LibreOffice Required for Formula Recalculation**: The `recalc.py` script uses LibreOffice to recalculate formula values. It auto-configures on first run.

## Reading and analyzing data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                        # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating values in Python and hardcoding them.

❌ **WRONG**: `sheet['B10'] = df['Sales'].sum()`
✅ **CORRECT**: `sheet['B10'] = '=SUM(B2:B9)'`

This applies to ALL calculations — totals, percentages, ratios, differences, etc.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**:
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify and fix errors**: Script returns JSON with error details. If `status` is `errors_found`, check `error_summary` for specific error types and locations. Fix and recalculate.

### Creating new Excel files

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

### Editing existing Excel files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
wb.save('modified.xlsx')
```

## Recalculating formulas

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

- Test 2–3 sample references before building full model
- Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Check denominators before using `/` in formulas (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Cross-sheet references: use correct format (`Sheet1!A1`)
- Verify all referenced cells exist

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, simple data export
- **openpyxl**: Best for complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently replaced with values
- Formulas are preserved but not evaluated — use `recalc.py` to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`