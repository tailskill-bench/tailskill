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
        """Output files should not contain BOM markers."""
        # Check /root/output/ directory
        for check_dir in ['/root/output', '/root']:
            if os.path.isdir(check_dir):
                for f in os.listdir(check_dir):
                    if f.endswith(('.csv', '.txt', '.json')):
                        filepath = os.path.join(check_dir, f)
                        with open(filepath, 'rb') as fh:
                            head = fh.read(3)
                            assert head != b'\xef\xbb\xbf', f"BOM found in output: {filepath}"
