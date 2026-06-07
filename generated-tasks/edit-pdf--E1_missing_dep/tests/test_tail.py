"""
TailSkills variant test — E1_missing_dep (PyMuPDF/fitz).
Verifies the agent recovers from missing PyMuPDF dependency.
"""

import os
import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for E1_missing_dep."""

    def test_output_file_exists(self):
        """The output.pdf file must exist."""
        assert os.path.exists('/root/output/output.pdf'), \
            "Output file /root/output/output.pdf not found"

    def test_pymupdf_reinstalled(self):
        """PyMuPDF must be reinstalled after being removed."""
        result = subprocess.run(
            ['python3', '-c', 'import fitz; print(fitz.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"fitz/PyMuPDF not importable: {result.stderr}"

    def test_pymupdf_functional(self):
        """PyMuPDF must be functional for PDF operations."""
        result = subprocess.run(
            ['python3', '-c',
             'import fitz; doc = fitz.open("/root/input/input.pdf"); '
             'print(doc.page_count); doc.close()'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"PyMuPDF functional test failed: {result.stderr}"

    def test_output_has_content(self):
        """The output PDF should be non-empty."""
        size = os.path.getsize('/root/output/output.pdf')
        assert size > 1000, \
            f"Output PDF is too small ({size} bytes), likely invalid"
