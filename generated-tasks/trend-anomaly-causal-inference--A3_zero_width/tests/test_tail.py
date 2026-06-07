"""
TailSkills variant test — auto-generated.
Variant: A3_zero_width
Verifies output CSV and input files do not contain zero-width Unicode characters.
"""

import os
import pytest

ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}


class TestTailVariant:
    """A3_zero_width: Verify no zero-width Unicode characters in output files."""

    def test_no_zero_width_in_output(self):
        """Output and input files should not contain zero-width Unicode characters."""
        for check_dir in ['/app/output', '/app']:
            if not os.path.isdir(check_dir):
                continue
            for f in os.listdir(check_dir):
                if f.endswith(('.csv', '.txt', '.json')):
                    filepath = os.path.join(check_dir, f)
                    with open(filepath, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    for c in ZW_CHARS:
                        assert c not in content, f"Zero-width char U+{ord(c):04X} found in: {filepath}"
