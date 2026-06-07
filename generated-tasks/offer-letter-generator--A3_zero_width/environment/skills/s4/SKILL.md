---
name: docx
description: Word document manipulation with python-docx handling split placeholders, headers/footers, nested tables, and Unicode cleaning.
---

# Word Document Manipulation

## Split Placeholders & Input Cleaning

Word splits placeholders across XML runs (e.g., `{{CANDIDATE_NAME}}` → Run 1: `{{CANDI`, Run 2: `DATE_NAME}}`). **Never search individual runs.** Work at paragraph level. JSON data may contain invisible zero-width Unicode characters (U+200B/C/D) that corrupt matching—clean all input before template filling.

```python
import re, unicodedata, json

def replace_placeholder_robust(paragraph, placeholder, value):
    full_text = paragraph.text
    if placeholder not in full_text:
        return False
    runs = paragraph.runs
    if not runs:
        return False
    new_text = full_text.replace(placeholder, str(value))
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ''
    return True

def clean_string(s):
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.loads(clean_string(f.read()))
```

## Headers, Footers & Nested Tables

Headers/footers are separate from `doc.paragraphs`—iterate explicitly. Tables can nest; recurse into `cell.tables`.

```python
from docx import Document

doc = Document('template.docx')

for section in doc.sections:
    for para in section.header.paragraphs:
        pass
    for para in section.footer.paragraphs:
        pass

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