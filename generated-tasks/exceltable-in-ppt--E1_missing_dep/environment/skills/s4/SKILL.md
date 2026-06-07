---
name: s1
description: "PPTX manipulation toolkit and Excel table handling for embedded spreadsheets in presentations."
---

# PPTX Creation, Editing, and Analysis

A .pptx file is a ZIP archive of XML files and resources.

## Reading and Analyzing Content

### Text extraction
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
1. Read `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
2. Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colors
3. Grep for color (`<a:solidFill>`, `<a:srgbClr>`) and font references across XML files

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles
- State your content-informed design approach BEFORE writing code
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment
- Be consistent: repeat patterns, spacing, and visual language across slides

### Layout Tips
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns — text/bullets in one, featured content in the other. Use flexbox with unequal widths (e.g., 40%/60%).
- **Full-slide layout**: Let the featured content take up the entire slide.
- **NEVER vertically stack**: Do not place charts/tables below text in a single column.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. **NEVER set range limits.**
2. Create an HTML file for each slide (e.g., 720pt × 405pt for 16:9).
   - Use `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>` for text content
   - Use `class="placeholder"` for chart/table areas (gray background)
   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp, then reference in HTML
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint and save.
   - Use `html2pptx()` for each HTML file
   - Add charts/tables to placeholders via PptxGenJS API
   - Save with `pptx.writeFile()`
4. **Visual validation**: Generate thumbnails and inspect.
   - `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Check for: text cutoff, text overlap, positioning issues, contrast issues
   - Adjust HTML and regenerate if issues found; repeat until correct

## Editing an existing PowerPoint presentation

Work with raw Office Open XML (OOXML): unpack, edit XML, repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely. **NEVER set range limits.**
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
     - Single-column: unified narrative/single topic
     - Two-column: exactly 2 distinct items
     - Three-column: exactly 3 distinct items
     - Image + text: only when you have actual images
     - Quote layouts: only for actual quotes with attribution
     - Never use layouts with more placeholders than content
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
   - Slide indices are 0-based; same index can appear multiple times to duplicate

5. **Extract ALL text using `inventory.py`**:
   ```bash
   python scripts/inventory.py working.pptx text-inventory.json
   ```
   - Read `text-inventory.json` entirely (**NEVER set range limits**)
   - JSON structure:
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
   - Slides: `"slide-0"`, `"slide-1"`, etc.
   - Shapes: ordered by visual position (top-to-bottom, left-to-right) as `"shape-0"`, `"shape-1"`, etc.
   - Placeholder types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
   - `default_font_size` in points from layout placeholders (when available)
   - SLIDE_NUMBER shapes are automatically excluded
   - When `bullet: true`, `level` is always included (even if 0)
   - Spacing in points: `space_before`, `space_after`, `line_spacing` (only when set)
   - Colors: `"color"` for RGB (e.g., `"FF0000"`), `"theme_color"` for theme colors (e.g., `"DARK_1"`)
   - Only non-default values are included

6. **Generate replacement text and save to JSON**:
   - Verify which shapes exist in the inventory — only reference shapes that are present
   - `replace.py` validates all shapes exist; errors shown at once before exit
   - ALL text shapes from inventory are cleared unless you provide `"paragraphs"` for them
   - Add a `"paragraphs"` field to shapes needing content (not `"replacement_paragraphs"`)
   - Shapes without `"paragraphs"` are cleared automatically
   - Bulleted paragraphs are auto left-aligned; do NOT set `alignment` when `"bullet": true`
   - Use shape size to determine appropriate content length
   - Include paragraph properties from the original inventory — not just text
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) — added automatically
   - **Formatting rules**:
     - Headers/titles: typically `"bold": true`
     - List items: `"bullet": true, "level": 0` (level required when bullet is true)
     - Preserve alignment (e.g., `"alignment": "CENTER"`)
     - Include font properties when different from default
     - Colors: `"color": "FF0000"` for RGB, `"theme_color": "DARK_1"` for theme
     - Overlapping shapes: prefer shapes with larger `default_font_size` or more appropriate `placeholder_type`
   - Save to `replacement-text.json`

   Example:
   ```json
   "paragraphs": [
     { "text": "New presentation title text", "alignment": "CENTER", "bold": true },
     { "text": "Section Header", "bold": true },
     { "text": "First bullet point without bullet symbol", "bullet": true, "level": 0 },
     { "text": "Red colored text", "color": "FF0000" },
     { "text": "Theme colored text", "theme_color": "DARK_1" },
     { "text": "Regular paragraph text" }
   ]
   ```

   Shapes not listed are automatically cleared:
   ```json
   {
     "slide-0": {
       "shape-0": { "paragraphs": [...] }
     }
   }
   ```

7. **Apply replacements**:
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```
   - Extracts inventory of ALL text shapes via inventory.py
   - Validates shapes in replacement JSON exist in inventory
   - Clears text from ALL inventory shapes
   - Applies new text only to shapes with `"paragraphs"` defined
   - Preserves formatting via paragraph properties
   - Handles bullets, alignment, font properties, colors automatically

   Validation error examples:
   ```
   ERROR: Invalid shapes in replacement JSON:
     - Shape 'shape-99' not found on 'slide-0'. Available shapes: shape-0, shape-1, shape-4
     - Slide 'slide-999' not found in inventory
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
- Custom prefix: `python scripts/thumbnail.py template.pptx my-grid` (include path for specific directory, e.g., `workspace/my-grid`)
- Adjust columns: `--cols 4` (range: 3–6)
- Grid limits: 3 cols = 12 slides/grid, 4 cols = 20, 5 cols = 30, 6 cols = 42
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

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"`
- **pptxgenjs**: `npm install -g pptxgenjs`
- **playwright**: `npm install -g playwright`
- **react-icons**: `npm install -g react-icons react react-dom`
- **sharp**: `npm install -g sharp`
- **LibreOffice**: `sudo apt-get install libreoffice`
- **Poppler**: `sudo apt-get install poppler-utils`
- **defusedxml**: `pip install defusedxml`

> **TailSkills: Handling Read-Only Output Directories**
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
>
> This must be done **before** any file write operations.

# Excel Requirements

## Zero Formula Errors
Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

## Preserve Existing Templates
- Study and EXACTLY match existing format, style, and conventions
- Existing template conventions ALWAYS override these guidelines

## Financial Model Standards

### Color Coding
- **Blue (0,0,255)**: Hardcoded inputs/scenario inputs
- **Black (0,0,0)**: ALL formulas and calculations
- **Green (0,128,0)**: Cross-sheet links within same workbook
- **Red (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting
- **Years**: Text strings (`"2024"` not `"2,024"`)
- **Currency**: `$#,##0`; specify units in headers (`"Revenue ($mm)"`)
- **Zeros**: Display as `"-"` including percentages (`$#,##0;($#,##0);-`)
- **Percentages**: `0.0%`
- **Multiples**: `0.0x` (EV/EBITDA, P/E)
- **Negatives**: Parentheses `(123)` not minus `-123`

### Formula Rules
- ALL assumptions in separate cells; use cell references: `=B5*(1+$B$6)` not `=B5*1.05`
- Verify cell references; check off-by-one errors
- Consistent formulas across projection periods
- Test edge cases (zero, negative values)
- Document hardcodes: `"Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"`

# XLSX Creation, Editing, and Analysis

**LibreOffice Required for Formula Recalculation**: `recalc.py` uses LibreOffice to recalculate formula values. Auto-configures on first run.

## Reading Data

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                        # First sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

df.head()      # Preview
df.info()      # Column info
df.describe()  # Statistics

df.to_excel('output.xlsx', index=False)
```

## CRITICAL: Use Formulas, Not Hardcoded Values

### ❌ WRONG
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

### ✅ CORRECT
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**:
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify and fix errors**: Check JSON output for `status`, `error_summary`

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

- [ ] Test 2–3 sample references before building full model
- [ ] Confirm Excel column mapping (e.g., column 64 = BL, not BK)
- [ ] Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] Check for null values with `pd.notna()`
- [ ] FY data often in columns 50+
- [ ] Search all occurrences, not just first
- [ ] Check denominators before using `/` in formulas (#DIV/0!)
- [ ] Verify all cell references point to intended cells (#REF!)
- [ ] Use correct format for cross-sheet references (`Sheet1!A1`)
- [ ] Test formulas on 2–3 cells before applying broadly
- [ ] Verify all referenced cells exist
- [ ] Test edge cases: zero, negative, very large values

## Best Practices

- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values; **Warning**: saving replaces formulas with values
- For large files: `read_only=True` for reading, `write_only=True` for writing
- Formulas preserved but not evaluated — use `recalc.py`
- Specify data types: `pd.read_excel('file.xlsx', dtype={'id': str})`
- Read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- For Excel files: add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values