"""
TailSkills variant test — A3_zero_width
Verifies output CSV and input files do not contain zero-width Unicode characters.
"""

import os
import pytest

ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_zero_width_in_output(self):
        """Output and input files should not contain zero-width Unicode characters."""
        scan_dirs = ["/root/output", "/root/data"]
        for scan_dir in scan_dirs:
            if not os.path.isdir(scan_dir):
                continue
            for f in os.listdir(scan_dir):
                if f.endswith(('.csv', '.txt', '.json')):
                    filepath = os.path.join(scan_dir, f)
                    with open(filepath, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    for c in ZW_CHARS:
                        assert c not in content, f"Zero-width char U+{ord(c):04X} found in: {filepath}"
