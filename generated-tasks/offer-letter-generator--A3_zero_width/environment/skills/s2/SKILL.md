---
name: docx
description: Word document manipulation with python-docx - handling split placeholders, headers/footers, nested tables. Includes guidance for cleaning invisible Unicode characters from input data.
---

# Word Document Manipulation with python-docx

## Critical: Split Placeholder Problem

Word often splits placeholder text across multiple XML runs (e.g., `{{CANDIDATE_NAME}}` → Run 1: `{{CANDI`, Run 2: `DATE_NAME}}`).

**Never search individual runs.** Always work at paragraph level:

```python
import re

def replace_placeholder_robust(paragraph, placeholder, value):
    """Replace placeholder that may be split across runs."""
    full_text = paragraph.text
    if placeholder not in full_text:
        return False

    runs = paragraph.runs
    if not runs:
        return False

    char_to_run = []
    for run in runs:
        for char in run.text:
            char_to_run.append(run)

    start_idx = full_text.find(placeholder)
    end_idx = start_idx + len(placeholder)

    if start_idx >= len(char_to_run):
        return False

    new_text = full_text.replace(placeholder, str(value))

    for i, run in enumerate(runs):
        if i == 0:
            run.text = new_text
        else:
            run.text = ''

    return True
```

## Cleaning Input Data

JSON data files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that corrupt placeholder matching. Clean all input JSON before template filling:

```python
import unicodedata
import json

def clean_string(s):
    """Remove zero-width/invisible Unicode characters."""
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

with open('data.json', 'r', encoding='utf-8') as f:
    raw = f.read()
cleaned = clean_string(raw)
data = json.loads(cleaned)
```

## Headers and Footers

Headers/footers are separate from `doc.paragraphs` and must be iterated explicitly:

```python
from docx import Document

doc = Document('template.docx')

for section in doc.sections:
    header = section.header
    for para in header.paragraphs:
        pass
    footer = section.footer
    for para in footer.paragraphs:
        pass
```

## Nested Tables

Tables can contain other tables. Recurse into `cell.tables`:

```python
def process_table(table, data):
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                replace_in_paragraph(para, data)
            for nested_table in cell.tables:
                process_table(nested_table, data)
```

## Conditional Sections

For `{{IF_CONDITION}}...{{END_IF_CONDITION}}` patterns:

```python
def handle_conditional(doc, condition_key, should_include, data):
    start_marker = '{{IF_' + condition_key + '}}'
    end_marker = '{{END_IF_' + condition_key + '}}'

    for para in doc.paragraphs:
        text = para.text
        if start_marker in text and end_marker in text:
            if should_include:
                new_text = text.replace(start_marker, '').replace(end_marker, '')
                for key, val in data.items():
                    new_text = new_text.replace('{{' + key + '}}', str(val))
            else:
                new_text = ''
            if para.runs:
                para.runs[0].text = new_text
                for run in para.runs[1:]:
                    run.text = ''