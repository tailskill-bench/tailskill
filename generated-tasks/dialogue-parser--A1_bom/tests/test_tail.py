"""
TailSkills variant test — A1_bom
Verifies output files and input files do not contain BOM markers.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_bom_in_output(self):
        """Output and input files should not contain BOM markers."""
        for scan_dir in ['/app', '/app/output']:
            if not os.path.isdir(scan_dir):
                continue
            for f in os.listdir(scan_dir):
                if f.endswith(('.csv', '.txt', '.json', '.dot')):
                    filepath = os.path.join(scan_dir, f)
                    with open(filepath, 'rb') as fh:
                        head = fh.read(3)
                        assert head != b'\xef\xbb\xbf', f"BOM found in: {filepath}"
