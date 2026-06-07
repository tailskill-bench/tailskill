---
name: s1
description: "PPTX manipulation toolkit and Excel table handling for embedded spreadsheets in presentations."
---

# PPTX creation, editing, and analysis

## Overview

A .pptx file is a ZIP archive of XML files and resources. Different tools and workflows apply depending on the task.

## Reading and analyzing content

### Text extraction
Convert a presentation to markdown for text-only reading:

```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
Required for: comments, speaker notes, slide layouts, animations, design elements, complex formatting.

#### Unpacking a file
`python ooxml/scripts/unpack.py <office_file> <output_dir>`

Script location: `skills/pptx/ooxml/scripts/unpack.py`. If missing, use `find . -name "unpack.py"`.

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

Before creating any presentation:
1. Consider the subject matter, tone, industry, and mood
2. Check for branding or company identity cues
3. Select a palette that reflects the subject
4. State your design approach before writing code

**Requirements**:
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment
- Be consistent: repeat patterns, spacing, and visual language across slides

#### Color Palette Selection

Choose 3–5 colors that work together (dominant + supporting + accent). Ensure text is readable on backgrounds.

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

**Geometric Patterns**: Diagonal section dividers, asymmetric column widths (30/70, 40/60), rotated text headers (90°/270°), circular/hexagonal frames, triangular accent shapes, overlapping shapes for depth.

**Border & Frame Treatments**: Thick single-color borders (10–20pt) on one side, double-line borders, corner brackets, L-shaped borders, underline accents (3–5pt).

**Typography Treatments**: Extreme size contrast (72pt headlines vs 11pt body), all-caps headers with wide letter spacing, numbered sections in oversized display type, monospace for data/stats, outlined text for emphasis.

**Chart & Data Styling**: Monochrome charts with single accent color, horizontal bar charts, dot plots, minimal gridlines, data labels directly on elements, oversized numbers for key metrics.

**Layout Innovations**: Full-bleed images with text overlays, sidebar column (20–30%), modular grid systems, Z-pattern or F-pattern flow, floating text boxes, magazine-style multi-column layouts.

**Background Treatments**: Solid color blocks (40–60%), gradient fills (vertical/diagonal), split backgrounds, edge-to-edge color bands, negative space as design element.

### Layout Tips
For slides with charts or tables:
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns — text/bullets in one, featured content in the other. Use flexbox with unequal widths (e.g., 40%/60%).
- **Full-slide layout**: Featured content takes the entire slide.
- **NEVER vertically stack** charts/tables below text in a single column.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. Never set range limits. Read the full file for syntax, formatting rules, and best practices.
2. Create an HTML file for each slide with proper dimensions (e.g., 720pt × 405pt for 16:9).
   - Use `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>` for text content.
   - Use `class="placeholder"` for chart/table areas (gray background).
   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp, then reference in HTML.
   - For charts/tables/images, use full-slide or two-column layout.
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint and save.
   - Use `html2pptx()` for each HTML file.
   - Add charts/tables to placeholders via PptxGenJS API.
   - Save with `pptx.writeFile()`.
4. **Visual validation**: Generate thumbnails and inspect.
   - `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Check for: text cutoff, text overlap, positioning issues, contrast issues.
   - If issues found, adjust HTML and regenerate. Repeat until correct.

## Editing an existing PowerPoint presentation

Work with raw Office Open XML (OOXML): unpack, edit XML, repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) completely. Never set range limits.
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files (primarily `ppt/slides/slide{N}.xml` and related).
4. **CRITICAL**: Validate after each edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Creating a new PowerPoint presentation **using a template**

Duplicate and re-arrange template slides, then replace placeholder content.

### Workflow
1. **Extract template text AND create visual thumbnail grid**:
   - Extract text: `python -m markitdown template.pptx > template-content.md`
   - Read `template-content.md` entirely (no range limits).
   - Create thumbnails: `python scripts/thumbnail.py template.pptx`

2. **Analyze template and save inventory**:
   - Review thumbnail grids for layouts, design patterns, visual structure.
   - Save `template-inventory.md`:
     ```markdown
     # Template Inventory Analysis
     **Total Slides: [count]**
     **IMPORTANT: Slides are 0-indexed (first slide = 0, last slide = count-1)**

     ## [Category Name]
     - Slide 0: [Layout code if available] - Description/purpose
     - Slide 1: [Layout code] - Description/purpose
     ```
   - Reference thumbnails to identify layout patterns, image placeholder locations, design consistency, visual hierarchy.

3. **Create presentation outline based on template inventory**:
   - Choose an intro/title template for the first slide.
   - Choose safe, text-based layouts for other slides.
   - **CRITICAL — Match layout structure to actual content**:
     - Single-column: unified narrative/single topic
     - Two-column: exactly 2 distinct items
     - Three-column: exactly 3 distinct items
     - Image + text: only when you have actual images
     - Quote: only for actual quotes with attribution
     - Never use layouts with more placeholders than you have content
   - Count content pieces BEFORE selecting layout.
   - Save `outline.md` with content and template mapping:
     ```
     # Mapping: slide numbers from outline -> template slide indices
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
   Read `text-inventory.json` entirely (no range limits).

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
   - SLIDE_NUMBER shapes are automatically excluded
   - When `bullet: true`, `level` is always included (even if 0)
   - Spacing in points: `space_before`, `space_after`, `line_spacing` (only when set)
   - Colors: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1")
   - Only non-default values are included

6. **Generate replacement text and save to JSON**:
   - Verify which shapes exist in the inventory — only reference shapes that are present.
   - The `replace.py` script validates all shapes exist; errors are shown at once.
   - **AUTOMATIC CLEARING**: ALL text shapes from the inventory are cleared unless you provide `"paragraphs"` for them.
   - Add `"paragraphs"` field to shapes that need content (not `"replacement_paragraphs"`).
   - Paragraphs with bullets are automatically left-aligned. Do not set `alignment` when `"bullet": true`.
   - Use shape size to determine appropriate content length.
   - Include paragraph properties from the original inventory — not just text.
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) in text — they are added automatically.
   - **Formatting rules**:
     - Headers/titles: typically `"bold": true`
     - List items: `"bullet": true, "level": 0` (level required when bullet is true)
     - Preserve alignment (e.g., `"alignment": "CENTER"`)
     - Include font properties when different from default
     - Colors: `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colors
     - Overlapping shapes: prefer shapes with larger `default_font_size` or more appropriate `placeholder_type`
   - Save to `replacement-text.json`.

   Example:
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

   Validation error examples:
   ```
   ERROR: Invalid shapes in replacement JSON:
     - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
   ```
   ```
   ERROR: Replacement text made overflow worse in these shapes:
     - slide-0/shape-2: overflow worsened by 1.25" (was 0.00", now 1.25")
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

Two-step process:

1. **PPTX to PDF**: `soffice --headless --convert-to pdf template.pptx`
2. **PDF to JPEG**: `pdftoppm -jpeg -r 150 template.pdf slide` → `slide-1.jpg`, `slide-2.jpg`, etc.

Options: `-r 150` (DPI), `-jpeg` or `-png`, `-f N` (first page), `-l N` (last page).

Example: `pdftoppm -jpeg -r 150 -f 2 -l 5 template.pdf slide`

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
Unless otherwise stated:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention

### Number Formatting Standards
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use `$#,##0`; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to display as "-", including percentages (e.g., `$#,##0;($#,##0);-`)
- **Percentages**: Default to `0.0%`
- **Multiples**: Format as `0.0x` (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses `(123)` not minus `-123`

### Formula Construction Rules
- Place ALL assumptions in separate cells; use cell references instead of hardcoded values (e.g., `=B5*(1+$B$6)` not `=B5*1.05`)
- Verify cell references, check off-by-one errors, ensure consistency across periods
- Test with edge cases (zero, negative values)
- Document hardcodes: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"

# XLSX creation, editing, and analysis

## Overview

LibreOffice is installed for formula recalculation via `recalc.py` (auto-configures on first run).

## Reading and analyzing data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                        # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # all sheets

df.head()      # preview
df.info()      # column info
df.describe()  # statistics

df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

Always use Excel formulas instead of calculating in Python and hardcoding results.

❌ **Wrong**: `sheet['B10'] = df['Sales'].sum()`
✅ **Correct**: `sheet['B10'] = '=SUM(B2:B9)'`

This applies to ALL calculations — totals, percentages, ratios, differences.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: New workbook or load existing
3. **Modify**: Add/edit data, formulas, formatting
4. **Save**: Write to file
5. **Recalculate (MANDATORY IF USING FORMULAS)**: `python recalc.py output.xlsx`
6. **Verify and fix errors**: Check JSON output for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`

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

The script recalculates all formulas, scans for errors, and returns JSON:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

If `status` is `"errors_found"`, check `error_summary` for types and locations, fix, and recalculate.

## Formula Verification Checklist

- Test 2–3 sample references before building full model
- Confirm column mapping (e.g., column 64 = BL, not BK)
- Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- Check for null values with `pd.notna()`
- Verify denominators before division (`#DIV/0!`)
- Verify all cell references (`#REF!`)
- Cross-sheet references use format `Sheet1!A1`
- Start small: test formulas on 2–3 cells before applying broadly

## Best Practices

### Library Selection
- **pandas**: data analysis, bulk operations, simple export
- **openpyxl**: complex formatting, formulas, Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values, but saving replaces formulas with values permanently
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Formulas are preserved but not evaluated — use `recalc.py`

### Working with pandas
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements