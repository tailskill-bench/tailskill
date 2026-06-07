---
name: s1
description: "PPTX manipulation toolkit and Excel table handling for embedded spreadsheets in presentations."
---

# PPTX creation, editing, and analysis

## Overview

A .pptx file is a ZIP archive of XML files and resources. Use the workflows below depending on the task.

## Reading and analyzing content

### Text extraction
```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
Needed for: comments, speaker notes, slide layouts, animations, design elements, complex formatting.

#### Unpacking a file
`python ooxml/scripts/unpack.py <office_file> <output_dir>`

Script location: `skills/pptx/ooxml/scripts/unpack.py` relative to project root. If missing, use `find . -name "unpack.py"`.

#### Key file structures
* `ppt/presentation.xml` — Main presentation metadata and slide references
* `ppt/slides/slide{N}.xml` — Individual slide contents
* `ppt/notesSlides/notesSlide{N}.xml` — Speaker notes
* `ppt/comments/modernComment_*.xml` — Comments
* `ppt/slideLayouts/` — Layout templates
* `ppt/slideMasters/` — Master slide templates
* `ppt/theme/` — Theme and styling
* `ppt/media/` — Images and media

#### Typography and color extraction
When emulating an example design:
1. Read `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
2. Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colors
3. Use grep to find color (`<a:solidFill>`, `<a:srgbClr>`) and font references across XML files

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles

Before creating any presentation:
1. Consider the subject matter, tone, industry, and mood
2. Check for branding or company identity cues
3. Select a palette that reflects the subject
4. State your design approach BEFORE writing code

**Requirements**:
- ✅ State your content-informed design approach BEFORE writing code
- ✅ Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, and visual language across slides

#### Color Palette Selection

Choose colors creatively based on topic, industry, mood, energy level, target audience, and brand identity. Pick 3–5 colors that work together (dominant + supporting + accent). Ensure text is clearly readable on backgrounds.

**Example palettes** (adapt or create your own):

1. **Classic Blue**: Deep navy (#1C2833), slate gray (#2E4053), silver (#AAB7B8), off-white (#F4F6F6)
2. **Teal & Coral**: Teal (#5EA8A7), deep teal (#277884), coral (#FE4447), white (#FFFFFF)
3. **Bold Red**: Red (#C0392B), bright red (#E74C3C), orange (#F39C12), yellow (#F1C40F), green (#2ECC71)
4. **Warm Blush**: Mauve (#A49393), blush (#EED6D3), rose (#E8B4B8), cream (#FAF7F2)
5. **Burgundy Luxury**: Burgundy (#5D1D2E), crimson (#951233), rust (#C15937), gold (#997929)
6. **Deep Purple & Emerald**: Purple (#B165FB), dark blue (#181B24), emerald (#40695B), white (#FFFFFF)
7. **Cream & Forest Green**: Cream (#FFE1C7), forest green (#40695B), white (#FCFCFC)
8. **Pink & Purple**: Pink (#F8275B), coral (#FF574A), rose (#FF737D), purple (#3D2F68)
9. **Lime & Plum**: Lime (#C5DE82), plum (#7C3A5F), coral (#FD8C6E), blue-gray (#98ACB5)
10. **Black & Gold**: Gold (#BF9A4A), black (#000000), cream (#F4F6F6)
11. **Sage & Terracotta**: Sage (#87A96B), terracotta (#E07A5F), cream (#F4F1DE), charcoal (#2C2C2C)
12. **Charcoal & Red**: Charcoal (#292929), red (#E33737), light gray (#CCCBCB)
13. **Vibrant Orange**: Orange (#F96D00), light gray (#F2F2F2), charcoal (#222831)
14. **Forest Green**: Black (#191A19), green (#4E9F3D), dark green (#1E5128), white (#FFFFFF)
15. **Retro Rainbow**: Purple (#722880), pink (#D72D51), orange (#EB5C18), amber (#F08800), gold (#DEB600)
16. **Vintage Earthy**: Mustard (#E3B448), sage (#CBD18F), forest green (#3A6B35), cream (#F4F1DE)
17. **Coastal Rose**: Old rose (#AD7670), beaver (#B49886), eggshell (#F3ECDC), ash gray (#BFD5BE)
18. **Orange & Turquoise**: Light orange (#FC993E), grayish turquoise (#667C6F), white (#FCFCFC)

#### Visual Details Options

**Geometric Patterns**: Diagonal section dividers, asymmetric column widths (30/70, 40/60, 25/75), rotated text headers (90°/270°), circular/hexagonal frames, triangular accent shapes, overlapping shapes for depth.

**Border & Frame Treatments**: Thick single-color borders (10–20pt) on one side, double-line borders, corner brackets, L-shaped borders, underline accents (3–5pt).

**Typography Treatments**: Extreme size contrast (72pt headlines vs 11pt body), all-caps headers with wide letter spacing, oversized display type for numbered sections, monospace (Courier New) for data/stats, condensed fonts for dense info, outlined text for emphasis.

**Chart & Data Styling**: Monochrome charts with single accent color, horizontal bar charts, dot plots, minimal gridlines, data labels directly on elements, oversized numbers for key metrics.

**Layout Innovations**: Full-bleed images with text overlays, sidebar column (20–30% width), modular grid systems (3×3, 4×4), Z-pattern or F-pattern flow, floating text boxes over colored shapes, magazine-style multi-column layouts.

**Background Treatments**: Solid color blocks (40–60% of slide), gradient fills (vertical/diagonal only), split backgrounds (two colors, diagonal or vertical), edge-to-edge color bands, negative space as design element.

### Layout Tips
**When creating slides with charts or tables:**
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns — text/bullets in one, featured content in the other. Use flexbox with unequal widths (e.g., 40%/60%).
- **Full-slide layout**: Let featured content take up the entire slide.
- **NEVER vertically stack**: Do not place charts/tables below text in a single column.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. **NEVER set range limits.** Read the full file for syntax, formatting rules, and best practices.
2. Create an HTML file for each slide (e.g., 720pt × 405pt for 16:9).
   - Use `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>` for text content
   - Use `class="placeholder"` for chart/table areas (gray background)
   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp, then reference in HTML
   - For slides with charts/tables/images, use full-slide or two-column layout
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint.
   - Use `html2pptx()` for each HTML file
   - Add charts/tables to placeholders using PptxGenJS API
   - Save with `pptx.writeFile()`
4. **Visual validation**: Generate thumbnails and inspect.
   - `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Check for: text cutoff, text overlap, positioning issues, contrast issues
   - Adjust HTML and regenerate if issues found; repeat until correct

## Editing an existing PowerPoint presentation

Work with raw OOXML: unpack the .pptx, edit XML, and repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) completely. **NEVER set range limits.** Read the full file before any editing.
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

2. **Analyze template and save inventory**:
   - Review thumbnail grids for layouts, design patterns, visual structure
   - Save `template-inventory.md`:
     ```markdown
     # Template Inventory Analysis
     **Total Slides: [count]**
     **IMPORTANT: Slides are 0-indexed (first slide = 0, last slide = count-1)**

     ## [Category Name]
     - Slide 0: [Layout code if available] - Description/purpose
     - Slide 1: [Layout code] - Description/purpose
     [... EVERY slide listed individually with its index ...]
     ```

3. **Create presentation outline based on template inventory**:
   - Choose an intro/title template for the first slide
   - Choose safe, text-based layouts for other slides
   - **CRITICAL — Match layout structure to actual content**:
     - Single-column: unified narrative / single topic
     - Two-column: exactly 2 distinct items
     - Three-column: exactly 3 distinct items
     - Image + text: only when you have actual images
     - Quote layouts: only for actual quotes with attribution
     - Never use layouts with more placeholders than you have content
   - Count content pieces BEFORE selecting layout
   - Verify each placeholder will be filled with meaningful content
   - Save `outline.md` with content AND template mapping:
     ```
     # Template slides to use (0-based indexing)
     # WARNING: Verify indices are within range! Template with 73 slides has indices 0-72
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
   Read `text-inventory.json` entirely (**NEVER set range limits**).

   Inventory JSON structure:
   ```json
   {
     "slide-0": {
       "shape-0": {
         "placeholder_type": "TITLE",
         "left": 1.5,
         "top": 2.0,
         "width": 7.5,
         "height": 1.2,
         "paragraphs": [
           {
             "text": "Paragraph text",
             "bullet": true,
             "level": 0,
             "alignment": "CENTER",
             "space_before": 10.0,
             "space_after": 6.0,
             "line_spacing": 22.4,
             "font_name": "Arial",
             "font_size": 14.0,
             "bold": true,
             "italic": false,
             "underline": false,
             "color": "FF0000"
           }
         ]
       }
     }
   }
   ```

   Key features:
   - Slides: `"slide-0"`, `"slide-1"`, etc.
   - Shapes: ordered by visual position (top-to-bottom, left-to-right) as `"shape-0"`, `"shape-1"`, etc.
   - Placeholder types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
   - `default_font_size` in points from layout placeholders (when available)
   - Slide number shapes (SLIDE_NUMBER) are automatically excluded
   - When `bullet: true`, `level` is always included (even if 0)
   - Spacing: `space_before`, `space_after`, `line_spacing` in points (only when set)
   - Colors: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1")
   - Only non-default values are included

6. **Generate replacement text and save to JSON**:
   - Verify which shapes exist in the inventory — only reference shapes that are actually present
   - `replace.py` validates all shapes exist; errors show available shapes/slides
   - **AUTOMATIC CLEARING**: ALL text shapes from inventory are cleared unless you provide `"paragraphs"` for them
   - Add a `"paragraphs"` field to shapes that need content (not `"replacement_paragraphs"`)
   - Paragraphs with bullets are automatically left-aligned; do NOT set `alignment` when `"bullet": true`
   - Use shape size to determine appropriate content length
   - Include paragraph properties from the original inventory — not just text
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) in text — they are added automatically
   - **ESSENTIAL FORMATTING RULES**:
     - Headers/titles: typically `"bold": true`
     - List items: `"bullet": true, "level": 0` (level required when bullet is true)
     - Preserve alignment properties (e.g., `"alignment": "CENTER"`)
     - Include font properties when different from default
     - Colors: `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colors
     - Overlapping shapes: prefer shapes with larger `default_font_size` or more appropriate `placeholder_type`
   - Save to `replacement-text.json`

   Example:
   ```json
   {
     "slide-0": {
       "shape-0": {
         "paragraphs": [
           { "text": "New Title", "alignment": "CENTER", "bold": true },
           { "text": "Section Header", "bold": true },
           { "text": "First bullet point", "bullet": true, "level": 0 },
           { "text": "Red colored text", "color": "FF0000" },
           { "text": "Theme colored text", "theme_color": "DARK_1" },
           { "text": "Regular paragraph text" }
         ]
       }
     }
   }
   ```

7. **Apply replacements**:
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```
   The script extracts inventory, validates shapes, clears all text shapes, applies new text with formatting, and saves.

   Example validation errors:
   ```
   ERROR: Invalid shapes in replacement JSON:
     - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
     - Slide 'slide-999' not found in inventory
   ```

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

1. **Convert PPTX to PDF**:
   ```bash
   soffice --headless --convert-to pdf template.pptx
   ```
2. **Convert PDF pages to JPEG**:
   ```bash
   pdftoppm -jpeg -r 150 template.pdf slide
   ```
   Creates `slide-1.jpg`, `slide-2.jpg`, etc.

   Options: `-r 150` (DPI), `-jpeg` or `-png`, `-f N` (first page), `-l N` (last page).

## Code Style Guidelines
- Write concise code; avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
- **react-icons**: `npm install -g react-icons react react-dom`
- **sharp**: `npm install -g sharp`
- **LibreOffice**: `sudo apt-get install libreoffice`
- **Poppler**: `sudo apt-get install poppler-utils`
- **defusedxml**: `pip install defusedxml`

> **Handling Read-Only Output Directories**
>
> Before writing output files, ensure the directory is writable:
>
> ```python
> import os
> output_dir = os.path.dirname(output_path) or '.'
> if os.path.isdir(output_dir):
>     os.chmod(output_dir, 0o755)
> ```
>
> Or: `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_path>`

---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
Study and EXACTLY match existing format, style, and conventions when modifying files. Existing template conventions ALWAYS override these guidelines.

## Financial models

### Color Coding Standards
Unless otherwise stated by the user or existing template:
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
- Verify no unintended circular references

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
df.head()
df.info()
df.describe()
df.to_excel('output.xlsx', index=False)
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
sheet.append(['Row', 'of', 'data'])
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
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
sheet.delete_cols(3)
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'
wb.save('modified.xlsx')
```

## Recalculating formulas

```bash
python recalc.py <excel_file> [timeout_seconds]
```

The script auto-sets up LibreOffice macro on first run, recalculates all formulas in all sheets, scans ALL cells for Excel errors, and returns JSON:

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
- FY data often in columns 50+
- Search all occurrences, not just first match
- Check denominators before using `/` in formulas (#DIV/0!)
- Verify all cell references point to intended cells (#REF!)
- Cross-sheet references: use correct format (`Sheet1!A1`)
- Start small: test formulas on 2–3 cells before applying broadly
- Verify all referenced cells exist
- Test edge cases: zero, negative, very large values

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, simple data export
- **openpyxl**: Best for complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are permanently replaced with values
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Formulas are preserved but not evaluated — use `recalc.py` to update values

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements