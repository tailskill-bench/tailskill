"""
TailSkills variant test — A3_zero_width
Verifies answer.json exists and data files were cleaned properly.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """answer.json must exist in /root."""
        assert os.path.exists('/root/answer.json'), "Output file /root/answer.json not found"

    def test_data_files_cleaned(self):
        """JSON data files should not contain zero-width characters."""
        import unicodedata
        from pathlib import Path
        zw_found = False
        for p in Path('/root/DATA').rglob('*.json'):
            content = p.read_text(encoding='utf-8')
            if any(unicodedata.category(ch) == 'Cf' for ch in content):
                zw_found = True
                break
        assert not zw_found, "Zero-width characters still present in data files"
