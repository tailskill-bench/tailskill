"""
TailSkills variant test: verify zero-width characters were cleaned from data file.
"""
import json
import os
import unicodedata


TARGET_FILE = "/root/employee_data.json"


def test_data_file_cleaned():
    """employee_data.json should not contain zero-width Unicode characters after Oracle cleaning."""
    if not os.path.exists(TARGET_FILE):
        return
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    zw_chars = [ch for ch in content if unicodedata.category(ch) == 'Cf']
    assert len(zw_chars) == 0, \
        f"{TARGET_FILE} still contains {len(zw_chars)} zero-width/invisible characters"


def test_output_file_exists():
    """offer_letter_filled.docx should exist as output."""
    assert os.path.exists('/root/offer_letter_filled.docx'), "Output file /root/offer_letter_filled.docx not found"
