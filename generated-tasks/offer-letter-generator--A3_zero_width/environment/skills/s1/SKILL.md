---
name: docx
description: Word document manipulation with python-docx - handling split placeholders, headers/footers, nested tables. Includes guidance for cleaning invisible Unicode characters from input data.
---

# Word Document Manipulation with python-docx

## Critical: Split Placeholder Problem

**The #1 issue with Word templates**: Word often splits placeholder text across multiple XML runs. For example, `{{CANDIDATE_NAME}}` might be stored as:
- Run 1: `{{CANDI`
- Run 2: `DATE_NAME}}`

This happens due to spell-check, formatting changes, or Word's internal XML structure.

### Naive Approach (FAILS on split placeholders)

```python
# DON'T DO THIS - won't find split placeholders
for para in doc.paragraphs:
    for run in para.runs:
        if '{{NAME}}' in run.text:  # Won't match if split!
            run.text = run.text.replace('{{NAME}}', value)
```

### Correct Approach: Paragraph-Level Search and Rebuild

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

> **Important**: JSON data files may contain invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that can corrupt placeholder matching and string comparisons. Always clean input data before use:

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

Apply this cleaning to all input JSON files before using them to fill template placeholders.

## Headers and Footers

Headers/footers are separate from main document body:

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

Tables can contain other tables. Must recurse:

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
```

## Common Pitfalls

1. **Forgetting headers/footers** - They're not in `doc.paragraphs`
2. **Missing nested tables** - Must recurse into `cell.tables`
3. **Split placeholders** - Always work at paragraph level, not run level
4. **Losing formatting** - Keep first run's formatting when rebuilding
5. **Conditional markers left behind** - Remove `{{IF_...}}` markers after processing
6. **Invisible chars in data** - Clean zero-width Unicode from JSON before template filling
