---
name: s1
description: "PPTX manipulation toolkit and Excel table handling for embedded spreadsheets in presentations."
---

# PPTX creation, editing, and analysis

## Overview

A .pptx file is a ZIP archive of XML files and resources. Different tools apply depending on whether you are reading, creating from scratch, editing existing slides, or using a template.

## Reading and analyzing content

### Text extraction
```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
Required for: comments, speaker notes, slide layouts, animations, design elements, complex formatting.

#### Unpacking a file
```bash
python ooxml/scripts/unpack.py <office_file> <output_dir>
```
Script location: `skills/pptx/ooxml/scripts/unpack.py` (use `find . -name "unpack.py"` if not found).

#### Key file structures
- `ppt/presentation.xml` — Main presentation metadata and slide references
- `ppt/slides/slide{N}.xml` — Individual slide contents
- `ppt/notesSlides/notesSlide{N}.xml` — Speaker notes
- `ppt/comments/modernComment_*.xml` — Comments
- `ppt/slideLayouts/` — Layout templates
- `ppt/slideMasters/` — Master slide templates
- `ppt/theme/` — Theme and styling
- `ppt/media/` — Images and media

#### Typography and color extraction
When emulating an example design:
1. Read `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
2. Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colors
3. Use grep to find color (`<a:solidFill>`, `<a:srgbClr>`) and font references across XML files

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment
- Be consistent: repeat patterns, spacing, and visual language across slides
- Choose 3–5 colors that work together (dominant + supporting + accent)

### Layout Tips
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns — text/bullets in one, featured content in the other. Use flexbox with unequal widths (e.g., 40%/60%).
- **Full-slide layout**: Featured content takes the entire slide.
- **NEVER vertically stack** charts/tables below text in a single column.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. **NEVER set range limits.**
2. Create an HTML file for each slide (e.g., 720pt × 405pt for 16:9).
   - Use `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>` for text content.
   - Use `class="placeholder"` for chart/table areas (gray background).
   - **CRITICAL**: Rasterize gradients and icons as PNG images using Sharp first, then reference in HTML.
   - Use full-slide or two-column layout for charts/tables/images.
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint.
   - Use `html2pptx()` for each HTML file.
   - Add charts/tables to placeholders via PptxGenJS API.
   - Save with `pptx.writeFile()`.
4. **Visual validation**: Generate thumbnails and inspect.
   ```bash
   python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4
   ```
   Examine thumbnails for: text cutoff, text overlap, positioning issues, contrast issues. Adjust HTML and regenerate if needed.

## Editing an existing PowerPoint presentation

Work with raw OOXML: unpack the .pptx, edit XML, and repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely. **NEVER set range limits.**
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files (primarily `ppt/slides/slide{N}.xml` and related).
4. **CRITICAL**: Validate after each edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Creating a new PowerPoint presentation **using a template**

Duplicate and re-arrange template slides, then replace placeholder content.

### Workflow
1. **Extract template text and create thumbnail grid**:
   ```bash
   python -m markitdown template.pptx > template-content.md
   python scripts/thumbnail.py template.pptx
   ```
   Read `template-content.md` fully (no range limits).

2. **Analyze template and save inventory** as `template-inventory.md`:
   - Slides are 0-indexed (first slide = 0, last slide = count-1)
   - Every slide must be listed individually with its index

3. **Create presentation outline** based on template inventory:
   - Match layout structure to actual content (single-column for unified narrative, two-column for exactly 2 items, etc.)
   - Count content pieces BEFORE selecting layout
   - Save `outline.md` with content and template mapping:
     ```
     template_mapping = [
         0,   # Use slide 0 (Title/Cover)
         34,  # Use slide 34 (B1: Title and body)
         34,  # Use slide 34 again (duplicate)
         50,  # Use slide 50 (E1: Quote)
         54,  # Use slide 54 (F2: Closing + Text)
     ]
     ```

4. **Duplicate, reorder, and delete slides**:
   ```bash
   python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
   ```
   Slide indices are 0-based. Same index can appear multiple times to duplicate.

5. **Extract ALL text using `inventory.py`**:
   ```bash
   python scripts/inventory.py working.pptx text-inventory.json
   ```
   Read `text-inventory.json` fully (no range limits).

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

   Key features:
   - Shapes ordered by visual position (top-to-bottom, left-to-right) as `"shape-0"`, `"shape-1"`, etc.
   - Placeholder types: `TITLE`, `CENTER_TITLE`, `SUBTITLE`, `BODY`, `OBJECT`, or `null`
   - `default_font_size` in points from layout placeholders (when available)
   - Slide number shapes (`SLIDE_NUMBER`) excluded automatically
   - When `bullet: true`, `level` is always included (even if 0)
   - Spacing: `space_before`, `space_after`, `line_spacing` in points (only when set)
   - Colors: `color` for RGB (e.g., `"FF0000"`), `theme_color` for theme colors (e.g., `"DARK_1"`)
   - Only non-default values are included

6. **Generate replacement text and save to JSON**:
   - Only reference shapes that exist in the inventory
   - **AUTOMATIC CLEARING**: ALL text shapes from inventory are cleared unless you provide `"paragraphs"` for them
   - Paragraphs with bullets are automatically left-aligned — do NOT set `alignment` when `"bullet": true`
   - Use shape size to determine appropriate content length
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) in text — they are added automatically
   - **Formatting rules**:
     - Headers/titles: typically `"bold": true`
     - List items: `"bullet": true, "level": 0` (level required when bullet is true)
     - Preserve alignment (e.g., `"alignment": "CENTER"`)
     - Include font properties when different from default
     - Colors: `"color": "FF0000"` for RGB, `"theme_color": "DARK_1"` for theme
     - Overlapping shapes: prefer shapes with larger `default_font_size` or more appropriate `placeholder_type`
   - Save to `replacement-text.json`:
     ```json
     {
       "slide-0": {
         "shape-0": {
           "paragraphs": [
             { "text": "New Title", "alignment": "CENTER", "bold": true },
             { "text": "First bullet point", "bullet": true, "level": 0 },
             { "text": "Red text", "color": "FF0000" }
           ]
         }
       }
     }
     ```

7. **Apply replacements**:
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```
   The script extracts inventory, validates shapes, clears all text, applies new paragraphs with formatting, and saves.

## Creating Thumbnail Grids

```bash
python scripts/thumbnail.py template.pptx [output_prefix]
```
- Creates `thumbnails.jpg` (or `thumbnails-1.jpg`, `thumbnails-2.jpg`, etc. for large decks)
- Default: 5 columns, max 30 slides per grid (5×6)
- Custom prefix: `python scripts/thumbnail.py template.pptx workspace/my-grid`
- Adjust columns: `--cols 4` (range: 3–6; 3 cols = 12 slides/grid, 4 = 20, 5 = 30, 6 = 42)
- Slides are zero-indexed

## Converting Slides to Images

1. **Convert PPTX to PDF**: `soffice --headless --convert-to pdf template.pptx`
2. **Convert PDF pages to JPEG**: `pdftoppm -jpeg -r 150 template.pdf slide`
   Creates `slide-1.jpg`, `slide-2.jpg`, etc. Options: `-r 150` (DPI), `-jpeg` or `-png`, `-f N` (first page), `-l N` (last page).

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
- **react-icons**: `npm install -g react-icons react react-dom`
- **sharp**: `npm install -g sharp`
- **LibreOffice**: `sudo apt-get install libreoffice`
- **Poppler**: `sudo apt-get install poppler-utils`
- **defusedxml**: `pip install defusedxml`

> **Handling Read-Only Output Directories**: Before writing output files, ensure the directory is writable:
> ```python
> import os
> output_dir = os.path.dirname(output_path) or '.'
> if os.path.isdir(output_dir):
>     os.chmod(output_dir, 0o755)
> ```
> Or: `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>`

---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).

### Preserve Existing Templates
Study and EXACTLY match existing format, style, and conventions when modifying files. Existing template conventions ALWAYS override these guidelines.

## Financial models

### Color Coding Standards
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, scenario-changeable numbers
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links from other worksheets in same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., `"2024"` not `2,024`)
- **Currency**: `$#,##0`; specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display as `"-"`, including percentages (`$#,##0;($#,##0);-`)
- **Percentages**: Default `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate cells; use cell references, not hardcoded values in formulas
  - Example: `=B5*(1+$B$6)` not `=B5*1.05`
- Verify cell references, check off-by-one errors, ensure consistency across periods
- Test edge cases (zero, negative values); verify no unintended circular references

### Documentation for Hardcodes
Format: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX creation, editing, and analysis

## Overview

Tools: **pandas** for data analysis/bulk operations, **openpyxl** for formulas/formatting/Excel-specific features.

**LibreOffice Required for Formula Recalculation**: The `recalc.py` script uses LibreOffice and auto-configures on first run.

## Reading and analyzing data

```python
import pandas as pd
df = pd.read_excel('file.xlsx')                        # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

❌ **WRONG**: `sheet['B10'] = df['Sales'].sum()`
✅ **CORRECT**: `sheet['B10'] = '=SUM(B2:B9)'`

This applies to ALL calculations — totals, percentages, ratios, differences.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`

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
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'
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
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Verify denominators before division (`#DIV/0!`)
- Verify all cell references (`#REF!`)
- Cross-sheet references use format `Sheet1!A1`
- Start small: test formulas on 2–3 cells before applying broadly

## Key openpyxl Notes
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: Saving a file opened with `data_only=True` permanently replaces formulas with values
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Formulas are preserved but not evaluated — use `recalc.py`