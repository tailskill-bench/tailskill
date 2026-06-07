---
name: s1
description: "Word document manipulation with python-docx - handling split placeholders, headers/footers, nested tables."
---

# Word Document Manipulation with python-docx

## Critical: Split Placeholder Problem

Word splits placeholder text across multiple XML runs (e.g., `{{CANDIDATE_NAME}}` becomes `{{CANDI` + `DATE_NAME}}`).

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

    new_text = full_text.replace(placeholder, str(value))

    for i, run in enumerate(runs):
        if i == 0:
            run.text = new_text
        else:
            run.text = ''

    return True
```

## Complete Solution Pattern

```python
from docx import Document
import json
import re

def fill_template(template_path, data_path, output_path):
    with open(data_path) as f:
        data = json.load(f)

    doc = Document(template_path)

    def replace_in_para(para):
        text = para.text
        pattern = r'\{\{([A-Z_]+)\}\}'
        if not re.search(pattern, text):
            return

        new_text = text
        for match in re.finditer(pattern, text):
            key = match.group(1)
            placeholder = match.group(0)
            if key in data:
                new_text = new_text.replace(placeholder, str(data[key]))

        if new_text != text and para.runs:
            para.runs[0].text = new_text
            for run in para.runs[1:]:
                run.text = ''

    for para in doc.paragraphs:
        replace_in_para(para)

    def process_table(table):
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    replace_in_para(para)
                for nested in cell.tables:
                    process_table(nested)

    for table in doc.tables:
        process_table(table)

    for section in doc.sections:
        for para in section.header.paragraphs:
            replace_in_para(para)
        for para in section.footer.paragraphs:
            replace_in_para(para)

    doc.save(output_path)

fill_template('template.docx', 'data.json', 'output.docx')
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

## Dependency Installation

```bash
pip3 install --break-system-packages --no-cache-dir python-docx==1.1.2
```

## Key Constraints

- **Headers/footers**: access via `doc.sections`, not `doc.paragraphs`
- **Nested tables**: recurse into `cell.tables`
- **Split placeholders**: always search at paragraph level, never run-level
- **Formatting preservation**: keep first run's formatting when rebuilding
- **Conditional markers**: remove `{{IF_...}}` and `{{END_IF_...}}` after processing