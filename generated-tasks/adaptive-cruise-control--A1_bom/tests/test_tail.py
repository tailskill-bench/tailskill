"""
TailSkills variant test — auto-generated.
Variant: A1_bom
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_bom_in_output(self):
        """Output files should not contain BOM markers."""
        import os
        for f in os.listdir('/root'):
            if f.endswith(('.csv', '.txt', '.json')):
                with open(f'/root/{f}', 'rb') as fh:
                    head = fh.read(3)
                    assert head != b'\xef\xbb\xbf', f"BOM found in output: {f}"

