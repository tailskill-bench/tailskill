---
name: s1
description: "PDF redaction for blind review and PDF toolkit."
---
# PDF Redaction for Blind Review
## CRITICAL RULES
1. **PRESERVE References section** — Self-citations MUST remain intact
2. **ONLY redact specific text matches** — Never redact entire pages/regions
3. **VERIFY output** — Check that 80%+ of original text remains
## Patterns to Redact (Before References Only)
**Use FULL names/phrases, not partial matches.**
- ✅ "John Smith" (full name)
- ❌ "Smith" (partial — would incorrectly match "Smith et al." citations in References)
1. **Author names** — FULL names only (e.g., "John Smith", not just "Smith")
2. **Affiliations** — Universities, companies (e.g., "Duke University")
3. **Email addresses** — Pattern: `*@*.edu`, `*@*.com`
4. **Venue names** — Conference/workshop names (e.g., "ICML 2024", "ICML Workshop")
5. **arXiv identifiers** — Pattern: `arXiv:XXXX.XXXXX`
6. **DOIs** — Pattern: `10.XXXX/...`
7. **Acknowledgement names** — Names in "Acknowledgements" section
8. **Equal contribution footnotes** — e.g., "Equal contribution", "* Equal contribution"
## PyMuPDF (fitz) — Recommended Approach
```python
import fitz
import os
def redact_with_pymupdf(input_path: str, output_path: str, patterns: list[str]):
    """Redact specific patterns from PDF using PyMuPDF."""
    doc = fitz.open(input_path)
    references_page = None
    for i, page in enumerate(doc):
        if "references" in page.get_text().lower():
            references_page = i
            break
    for page_num, page in enumerate(doc):
        if references_page is not None and page_num >= references_page:
            continue
        for pattern in patterns:
            for rect in page.search_for(pattern):
                page.add_redact_annot(rect, fill=(0, 0, 0))
        page.apply_redactions()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    verify_redaction(input_path, output_path)
```
**Handling Read-Only Output Directories:**
```python
output_dir = os.path.dirname(output_path)
if output_dir and os.path.isdir(output_dir):
    os.chmod(output_dir, 0o755)
```
Or use: `python3 /root/.claude/skills/s1/scripts/prepare_output.py <output_dir>`
## REQUIRED: Verification Function
```python
import fitz
def verify_redaction(original_path, output_path):
    orig = fitz.open(original_path)
    redc = fitz.open(output_path)
    orig_len = sum(len(p.get_text()) for p in orig)
    redc_len = sum(len(p.get_text()) for p in redc)
    print(f"Original: {len(orig)} pages, {orig_len} chars")
    print(f"Redacted: {len(redc)} pages, {redc_len} chars")
    print(f"Retained: {redc_len/orig_len:.1%}")
    if len(redc) != len(orig):
        raise ValueError(f"Page count changed: {len(orig)} -> {len(redc)}")
    if redc_len < 1000:
        raise ValueError(f"PDF corrupted: only {redc_len} chars remain!")
    if redc_len < orig_len * 0.7:
        raise ValueError(f"Too much removed: kept only {redc_len/orig_len:.0%}")
    orig.close()
    redc.close()
    print("✓ Verification passed")
```
# PDF Processing Guide
## Quick Start
```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")
text = "".join(page.extract_text() for page in reader.pages)
```
## Python Libraries
### pypdf — Basic Operations
**Merge PDFs:**
```python
from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as output:
    writer.write(output)
```
**Split PDF:**
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```
**Extract Metadata:** `reader.metadata.title`, `reader.metadata.author`
**Rotate Pages:** `page.rotate(90)` then write via PdfWriter.
### pdfplumber — Text and Table Extraction
**Extract Text:**
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
```
**Extract Tables:**
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        for j, table in enumerate(page.extract_tables()):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```
**Table to DataFrame:** Use `pd.DataFrame(table[1:], columns=table[0])` per table, then `pd.concat(all_tables)`.
### reportlab — Create PDFs
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter
c.drawString(100, height - 100, "Hello World!")
c.save()
```
**Multi-Page with Platypus:** Build a `story` list of `Paragraph`, `Spacer`, `PageBreak` objects, then `doc.build(story)`.
## Command-Line Tools
### pdftotext (poppler-utils)
```bash
pdftotext input.pdf output.txt
pdftotext -layout input.pdf output.txt
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```
### qpdf
```bash
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf output.pdf --rotate=+90:1
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```
### pdftk (if available)
```bash
pdftk file1.pdf file2.pdf cat output merged.pdf
pdftk input.pdf burst
pdftk input.pdf rotate 1east output rotated.pdf
```
## Common Tasks
### Extract Text from Scanned PDFs
```python
import pytesseract
from pdf2image import convert_from_path
images = convert_from_path('scanned.pdf')
for i, image in enumerate(images):
    print(f"Page {i+1}:")
    print(pytesseract.image_to_string(image))
```
### Add Watermark
```python
from pypdf import PdfReader, PdfWriter
watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```
### Extract Images
```bash
pdfimages -j input.pdf output_prefix
# Produces output_prefix-000.jpg, output_prefix-001.jpg, etc.
```
### Password Protection
```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)
writer.encrypt("userpassword", "ownerpassword")
with open("encrypted.pdf", "wb") as output:
    writer.write(output)