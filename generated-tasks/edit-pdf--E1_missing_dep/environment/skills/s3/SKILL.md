---
name: s1
description: "Complete guide for reading, editing PDF documents with PyMuPDF, and parsing structured text input."
---

# PDF Editing Skill

## CRITICAL RULES

**NEVER:**
- Use strikethrough lines to cross out text
- Rasterize or flatten the PDF to images
- Convert PDF pages to PNG/JPG and draw on them
- Use pdf-to-image-to-pdf workflows
- Use `add_redact_annot()` with BLACK fill (use WHITE fill instead)
- Add text NEXT TO old values — REPLACE them at the SAME position

**TWO APPROACHES:**

1. **For REPLACING text** (e.g., updating name, email, DOB):
   - Use `draw_rect()` with white fill to cover old text
   - Use `insert_text()` at the SAME position
   - Text layer is preserved

2. **For TRUE REDACTION of sensitive data** (e.g., student ID):
   - Use `add_redact_annot(rect, fill=(1,1,1))` with WHITE fill
   - Call `apply_redactions()` to REMOVE text from PDF structure
   - Then `insert_text()` to add masked value (e.g., "****5678")
   - Original text is completely removed, not just covered

## Setup

PyMuPDF (`fitz`) is pre-installed. Verify:

```bash
python3 -c "import fitz; print('PyMuPDF ready')"
```

If `ModuleNotFoundError: No module named 'fitz'`:

```bash
pip3 install --break-system-packages --no-cache-dir PyMuPDF==1.24.10
```

## Reading PDF Content

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]
text = page.get_text()
print(text)
```

## Finding Text Positions

```python
rects = page.search_for("Label Text")
if rects:
    rect = rects[0]
    # rect.x0, rect.y0 = top-left; rect.x1, rect.y1 = bottom-right
    print(f"Found at: ({rect.x0}, {rect.y0}) to ({rect.x1}, {rect.y1})")
```

## Inserting Text

```python
page.insert_text(
    (x_position, y_position),
    "text to insert",
    fontsize=11,
    color=(0, 0, 0)  # black
)
doc.save("output.pdf")
```

## Fill Empty Form Fields

When a form field is empty, insert text next to the label:

```python
import fitz
from datetime import datetime

doc = fitz.open("input.pdf")
page = doc[0]

# Insert value to the right of label
label_rect = page.search_for("FIELD LABEL:")[0]
page.insert_text((label_rect.x1 + 5, label_rect.y1), "value", fontsize=11)

# Today's date
date_rect = page.search_for("Date")[0]
today = datetime.now().strftime("%Y/%m/%d")
page.insert_text((date_rect.x1 + 5, date_rect.y1), today, fontsize=11)

doc.save("output.pdf")
```

## Replacing Existing Text

When replacing text already in the PDF:

1. Extract PDF text to see current values
2. Compare with correct values from input source
3. For each value that needs changing: **COVER with white rectangle, then insert new text AT THE SAME POSITION**

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

current_text = page.get_text()
print(current_text)

old_value = "..."  # Value found in PDF that's wrong
new_value = "..."  # Correct value from input source

rects = page.search_for(old_value)
if rects:
    rect = rects[0]
    # STEP 1: Draw WHITE rectangle to COMPLETELY COVER old text
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
    # STEP 2: Insert new text at the SAME position
    page.insert_text((rect.x0, rect.y1), new_value, fontsize=11, color=(0, 0, 0))

doc.save("output.pdf")
```

**Key points:**
- `draw_rect(rect, fill=(1,1,1), width=0)` draws a WHITE filled rectangle
- `(1, 1, 1)` is white in RGB (0–1 scale)
- Insert new text at `rect.x0` (same X position), NOT `rect.x1 + offset`
- Text layer is preserved (text remains extractable)

## TRUE REDACTION for Sensitive Data

For sensitive data like student IDs, use TRUE REDACTION that removes original text from the PDF structure. A white rectangle only VISUALLY covers text — tools like pypdf can still extract hidden text.

**CRITICAL DISTINCTION:**
- `draw_rect()` = Visual cover only (text still extractable by machines)
- `add_redact_annot()` + `apply_redactions()` = TRUE redaction (text removed from PDF)

**Example:** "A12345678" → "****5678" (show only last 4 digits)

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

pdf_text = page.get_text()

original_in_pdf = "A88888888"  # Value found in PDF
digits = ''.join(c for c in original_in_pdf if c.isdigit())
masked = "****" + digits[-4:]  # Result: "****8888"

rects = page.search_for(original_in_pdf)
if rects:
    rect = rects[0]
    # STEP 1: Create TIGHT bounding box to avoid covering nearby labels
    tight_rect = fitz.Rect(rect.x0, rect.y0 + 8, rect.x1, rect.y1 - 2)
    # STEP 2: Add redaction annotation with WHITE fill
    page.add_redact_annot(tight_rect, fill=(1, 1, 1))
    # STEP 3: Apply redactions — REMOVES text from PDF structure
    page.apply_redactions()
    # STEP 4: Insert masked value at same position
    page.insert_text((rect.x0, rect.y1), masked, fontsize=11, color=(0, 0, 0))

doc.save("output.pdf")
```

## Workflow: Compare and Update

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

# Step 1: Read PDF current content
pdf_text = page.get_text()
print(pdf_text)

# Step 2: Read input source for correct values
# (parse input file, extract needed values)

# Step 3: For each value that differs, replace it
replacements = {}  # {old_value_in_pdf: correct_value}

for old_val, new_val in replacements.items():
    if old_val == new_val:
        continue
    rects = page.search_for(old_val)
    if rects:
        rect = rects[0]
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        page.insert_text((rect.x0, rect.y1), new_val, fontsize=11, color=(0, 0, 0))

doc.save("output.pdf")
```

## Guidelines

1. **COVER then REPLACE** — White rectangle to cover old text, insert new text at SAME position
2. **Never use strikethrough** — No lines through text
3. **Never rasterize** — No converting PDF to images, no `get_pixmap()` workflows
4. **Never add text NEXT TO old values** — Replace AT the same position
5. **Never use `add_redact_annot()` with black** — Creates black boxes
6. **Preserve all labels** — Form labels must remain visible
7. **Preserve text layer** — Text must remain extractable after editing
8. **Match font size** — Typically 10–12pt for forms

---

# Text Parser Skill

## Overview

Parse structured text files to extract data for filling PDFs.

## Key-Value Parsing

```python
def parse_input(text):
    """Parse key-value pairs from text."""
    data = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            line = line.lstrip('- ').strip()
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

with open("input.txt") as f:
    data = parse_input(f.read())
# data["Name"] -> "John Smith"
# data["Email"] -> "john@example.com"
```

## Common Input Formats

```
- Name: John Smith
- Email: john@example.com
- Phone: 555-1234
```

Or without dashes:
```
Name: John Smith
Email: john@example.com