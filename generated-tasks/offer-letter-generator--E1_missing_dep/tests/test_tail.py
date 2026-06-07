"""
TailSkills variant test — E1_missing_dep (python-docx).
Verifies the agent recovers from missing python-docx dependency.
"""

import os
import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for E1_missing_dep."""

    def test_output_file_exists(self):
        """The offer_letter_filled.docx output file must exist."""
        assert os.path.exists('/root/offer_letter_filled.docx'), \
            "Output file /root/offer_letter_filled.docx not found"

    def test_docx_reinstalled(self):
        """python-docx must be reinstalled after being removed."""
        result = subprocess.run(
            ['python3', '-c', 'import docx; print(docx.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"python-docx not importable: {result.stderr}"

    def test_docx_functional(self):
        """python-docx Document must be functional."""
        result = subprocess.run(
            ['python3', '-c',
             'from docx import Document; '
             'doc = Document("/root/offer_letter_template.docx"); '
             'print(len(doc.paragraphs))'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"python-docx functional test failed: {result.stderr}"

    def test_output_has_content(self):
        """The output DOCX should be non-empty."""
        size = os.path.getsize('/root/offer_letter_filled.docx')
        assert size > 5000, \
            f"Output DOCX is too small ({size} bytes), likely invalid"
