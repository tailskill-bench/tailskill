"""
TailSkills variant test — auto-generated.
Variant: A1_bom
Tests that no BOM markers remain in output CSV/text/JSON files.
"""

import os
import pytest


class TestTailVariant:
    """A1_bom: Verify no BOM markers in output files."""

    def test_no_bom_in_output(self):
        """Output files in /root should not contain BOM markers."""
        for f in os.listdir('/root'):
            if f.endswith(('.csv', '.txt', '.json')):
                with open(f'/root/{f}', 'rb') as fh:
                    head = fh.read(3)
                    assert head != b'\xef\xbb\xbf', f"BOM found in output: {f}"
