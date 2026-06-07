#!/bin/bash
set -e
rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED
pip3 install --no-cache-dir --timeout 300 pymupdf==1.24.0 pdfplumber==0.11.0 pypdf==4.0.0
cat > /tmp/anonymize_pdfs.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import os
import fitz

INPUT_DIR = "/root"
OUTPUT_DIR = "/root/redacted"

REDACT_PATTERNS = {
    "paper1.pdf": {
        "authors": ["Yueqian Lin", "Zhengmian Hu", "Qinsi Wang", "Yudong Liu", "Hengfan Zhang", "Jayakumar Subramanian", "Nikos Vlassis", "Hai Li", "Helen Li", "Hai \"Helen\" Li", "Yiran Chen"],
        "affiliations": ["Duke University", "Adobe"],
        "emails": ["@duke.edu", "@adobe.com"],
        "identifiers": ["arXiv:2509.26542"],
    },
    "paper2.pdf": {
        "authors": ["Jiatong Shi", "Yueqian Lin", "Xinyi Bai", "Keyi Zhang", "Yuning Wu", "Yuxun Tang", "Yifeng Yu", "Qin Jin", "Shinji Watanabe"],
        "affiliations": ["Carnegie Mellon University", "Carnegie Mellon", "Duke Kunshan University", "Duke Kunshan", "Cornell University", "Cornell", "Renmin University of China", "Renmin University", "Georgia Institute of Technology", "Georgia Tech"],
        "emails": ["@cmu.edu", "@duke.edu", "@cornell.edu", "@ruc.edu.cn", "@gatech.edu"],
        "identifiers": ["10.21437/Interspeech.2024-33", "Shengyuan Xu", "Pengcheng Zhu"],
    },
    "paper3.pdf": {
        "authors": ["Yueqian Lin", "Yuzhe Fu", "Jingyang Zhang", "Yudong Liu", "Jianyi Zhang", "Jingwei Sun", "Hai Li", "Yiran Chen"],
        "affiliations": ["Duke University"],
        "emails": ["@duke.edu", "yl768@duke.edu"],
        "identifiers": ["Equal contribution", "ICML Workshop on Machine Learning for Audio"],
    },
}

def redact_text_in_pdf(input_path, output_path, patterns):
    doc = fitz.open(input_path)
    all_patterns = patterns.get("authors", []) + patterns.get("affiliations", []) + patterns.get("emails", []) + patterns.get("identifiers", [])
    for page_num in range(len(doc)):
        page = doc[page_num]
        for pattern in all_patterns:
            for inst in page.search_for(pattern):
                page.add_redact_annot(inst, fill=(0, 0, 0))
        page.apply_redactions()
    doc.save(output_path)
    doc.close()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for pdf_name, patterns in REDACT_PATTERNS.items():
        input_path = os.path.join(INPUT_DIR, pdf_name)
        output_path = os.path.join(OUTPUT_DIR, pdf_name)
        if os.path.exists(input_path):
            redact_text_in_pdf(input_path, output_path, patterns)

if __name__ == "__main__":
    main()
PYTHON_SCRIPT
python3 /tmp/anonymize_pdfs.py
