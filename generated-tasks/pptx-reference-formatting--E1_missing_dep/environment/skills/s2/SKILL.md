---
name: s1
description: Combined skill for pptx-reference-formatting with E1_missing_dep handling. PPTX creation, editing, and analysis.
---

# PPTX creation, editing, and analysis

## Overview

A .pptx file is a ZIP archive of XML files and resources. Use the workflows below to create, edit, or analyze presentations.

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
3. Grep for color (`<a:solidFill>`, `<a:srgbClr>`) and font references across XML files

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles

Before creating any presentation:
1. Analyze content and choose appropriate design elements matching subject matter, tone, and branding
2. State your design approach before writing code

**Requirements**:
- ✅ State content-informed design approach BEFORE writing code
- ✅ Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, and visual language across slides

#### Color Palette Selection

Choose colors that match the specific topic. Consider industry, mood, energy level, audience, and brand identity. Build a palette of 3–5 colors (dominant + supporting + accent). Ensure text contrast on backgrounds.

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

**Border & Frame Treatments**: Thick single-color borders (10–20pt) on one side, double-line contrasting borders, corner brackets, L-shaped borders (top+left or bottom+right), underline accents (3–5pt thick).

**Typography Treatments**: Extreme size contrast (72pt headlines vs 11pt body), all-caps headers with wide letter spacing, numbered sections in oversized display type, monospace (Courier New) for data/stats, condensed fonts (Arial Narrow) for dense info, outlined text for emphasis.

**Chart & Data Styling**: Monochrome charts with single accent color, horizontal bar charts, dot plots, minimal/no gridlines, data labels directly on elements, oversized numbers for key metrics.

**Layout Innovations**: Full-bleed images with text overlays, sidebar column (20–30% width), modular grid systems (3×3, 4×4), Z-pattern or F-pattern content flow, floating text boxes over colored shapes, magazine-style multi-column layouts.

**Background Treatments**: Solid color blocks (40–60% of slide), gradient fills (vertical/diagonal only), split backgrounds (two colors, diagonal or vertical), edge-to-edge color bands, negative space as design element.

### Layout Tips
**When creating slides with charts or tables:**
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns — text/bullets in one, featured content in the other. Use flexbox with unequal widths (e.g., 40%/60%).
- **Full-slide layout**: Let featured content take up the entire slide.
- **NEVER vertically stack**: Do not place charts/tables below text in a single column.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely. **NEVER set range limits.** Read full content for syntax, formatting rules, and best practices.
2. Create an HTML file for each slide (e.g., 720pt × 405pt for 16:9)
   - Use `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>` for text content
   - Use `class="placeholder"` for chart/table areas (gray background)
   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp, then reference in HTML
   - For slides with charts/tables/images, use full-slide or two-column layout
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint and save
   - Use `html2pptx()` to process each HTML file
   - Add charts/tables to placeholders using PptxGenJS API
   - Save with `pptx.writeFile()`
4. **Visual validation**: Generate thumbnails and inspect
   - `python scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Examine thumbnail image for: text cutoff, text overlap, positioning issues, contrast issues
   - If issues found, adjust HTML margins/spacing/colors and regenerate
   - Repeat until all slides are visually correct

## Editing an existing PowerPoint presentation

Work with raw Office Open XML (OOXML): unpack, edit XML, repack.

### Workflow
1. **MANDATORY — READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely. **NEVER set range limits.** Read full content before any editing.
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files (primarily `ppt/slides/slide{N}.xml` and related)
4. **CRITICAL**: Validate after each edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

> **TailSkills: Missing Dependency (lxml)**
>
> If code fails with `ModuleNotFoundError: No module named 'lxml'`:
> ```bash
> pip3 install --break-system-packages lxml
> ```
> Python's built-in `xml.etree.ElementTree` can handle basic XML but has limited XPath namespace support. For complex OOXML editing with namespaces, installing lxml is strongly recommended.

## Creating a new PowerPoint presentation **using a template**

Duplicate and re-arrange template slides, then replace placeholder content.

### Workflow
1. **Extract template text AND create visual thumbnail grid**:
   * Extract text: `python -m markitdown template.pptx > template-content.md`
   * Read `template-content.md` entirely — **NEVER set range limits**
   * Create thumbnail grids: `python scripts/thumbnail.py template.pptx`

2. **Analyze template and save inventory to a file**:
   * Review thumbnail grid(s) for slide layouts, design patterns, visual structure
   * Create `template-inventory.md`:
     ```markdown
     # Template Inventory Analysis
     **Total Slides: [count]**
     **IMPORTANT: Slides are 0-indexed (first slide = 0, last slide = count-1)**

     ## [Category Name]
     - Slide 0: [Layout code if available] - Description/purpose
     - Slide 1: [Layout code] - Description/purpose
     [... EVERY slide must be listed individually with its index ...]
     ```
   * This inventory file is REQUIRED for selecting templates in the next step

3. **Create presentation outline based on template inventory**:
   * Choose an intro/title template for the first slide (one of the first templates)
   * Choose safe, text-based layouts for other slides
   * **CRITICAL — Match layout structure to actual content**:
     - Single-column: unified narrative or single topic
     - Two-column: ONLY when you have exactly 2 distinct items
     - Three-column: ONLY when you have exactly 3 distinct items
     - Image + text: ONLY when you have actual images to insert
     - Quote: ONLY for actual quotes with attribution, never for emphasis
     - Never use layouts with more placeholders than you have content
   * Count content pieces BEFORE selecting layout
   * Verify each placeholder will be filled with meaningful content
   * Save `outline.md` with content AND template mapping:
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

4. **Duplicate, reorder, and delete slides using `rearrange.py`**:
   ```bash
   python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52
   ```
   Slide indices are 0-based. Same index can appear multiple times to duplicate.

5. **Extract ALL text using the `inventory.py` script**:
   ```bash
   python scripts/inventory.py working.pptx text-inventory.json
   ```
   Read `text-inventory.json` entirely — **NEVER set range limits**.

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
   - Shapes: Ordered by visual position (top-to-bottom, left-to-right) as `"shape-0"`, `"shape-1"`, etc.
   - Placeholder types: TITLE, CENTER_TITLE, SUBTITLE, BODY, OBJECT, or null
   - `default_font_size` in points from layout placeholders (when available)
   - SLIDE_NUMBER shapes are automatically excluded
   - When `bullet: true`, `level` is always included (even if 0)
   - Spacing: `space_before`, `space_after`, `line_spacing` in points (only when set)
   - Colors: `color` for RGB (e.g., "FF0000"), `theme_color` for theme colors (e.g., "DARK_1")
   - Only non-default values are included

6. **Generate replacement text and save to JSON**
   - Verify which shapes exist in the inventory — only reference shapes that are actually present
   - The replace.py script validates all shapes exist; errors are shown at once before exit
   - **AUTOMATIC CLEARING**: ALL text shapes from inventory are cleared unless you provide `"paragraphs"` for them
   - Add `"paragraphs"` field to shapes that need content (not `"replacement_paragraphs"`)
   - Paragraphs with bullets are automatically left-aligned — do NOT set `alignment` when `"bullet": true`
   - Use shape size to determine appropriate content length
   - Include paragraph properties from the original inventory — not just text
   - When `bullet: true`, do NOT include bullet symbols (•, -, *) in text — they are added automatically
   - **Formatting rules**:
     - Headers/titles: typically `"bold": true`
     - List items: `"bullet": true, "level": 0` (level required when bullet is true)
     - Preserve alignment properties (e.g., `"alignment": "CENTER"`)
     - Include font properties when different from default
     - Colors: `"color": "FF0000"` for RGB or `"theme_color": "DARK_1"` for theme colors
     - Overlapping shapes: prefer shapes with larger `default_font_size` or more appropriate `placeholder_type`
   - Save to `replacement-text.json`

   Example paragraphs field:
   ```json
   "paragraphs": [
     { "text": "New presentation title text", "alignment": "CENTER", "bold": true },
     { "text": "Section Header", "bold": true },
     { "text": "First bullet point without bullet symbol", "bullet": true, "level": 0 },
     { "text": "Red colored text", "color": "FF0000" },
     { "text": "Theme colored text", "theme_color": "DARK_1" },
     { "text": "Regular paragraph text without special formatting" }
   ]
   ```

   Shapes not listed in replacement JSON are automatically cleared:
   ```json
   {
     "slide-0": {
       "shape-0": { "paragraphs": [...] }
     }
   }
   ```

7. **Apply replacements using `replace.py`**:
   ```bash
   python scripts/replace.py working.pptx replacement-text.json output.pptx
   ```
   The script extracts inventory, validates shapes, clears all text, applies new text with formatting, and saves.

   Example validation errors:
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
- Custom prefix: `python scripts/thumbnail.py template.pptx workspace/my-grid`
- Adjust columns: `--cols 4` (range: 3–6)
- Grid limits: 3 cols = 12 slides/grid, 4 cols = 20, 5 cols = 30, 6 cols = 42
- Slides are zero-indexed (Slide 0, Slide 1, etc.)

## Converting Slides to Images

Two-step process:

1. **Convert PPTX to PDF**:
   ```bash
   soffice --headless --convert-to pdf template.pptx
   ```

2. **Convert PDF pages to JPEG images**:
   ```bash
   pdftoppm -jpeg -r 150 template.pdf slide
   ```
   Creates `slide-1.jpg`, `slide-2.jpg`, etc.

Options:
- `-r 150`: Resolution in DPI
- `-jpeg`: JPEG output (use `-png` for PNG)
- `-f N`: First page
- `-l N`: Last page
- `slide`: Output file prefix

Example for specific range:
```bash
pdftoppm -jpeg -r 150 -f 2 -l 5 template.pdf slide
```

## Code Style Guidelines

When generating code for PPTX operations: write concise code, avoid verbose variable names and redundant operations, avoid unnecessary print statements.

## Dependencies

Required dependencies (should already be installed):

- **markitdown**: `pip install "markitdown[pptx]"` (text extraction)
- **pptxgenjs**: `npm install -g pptxgenjs` (creating presentations via html2pptx)
- **playwright**: `npm install -g playwright` (HTML rendering in html2pptx)
- **react-icons**: `npm install -g react-icons react react-dom` (icons)
- **sharp**: `npm install -g sharp` (SVG rasterization and image processing)
- **LibreOffice**: `sudo apt-get install libreoffice` (PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (pdftoppm for PDF to images)
- **defusedxml**: `pip install defusedxml` (secure XML parsing)