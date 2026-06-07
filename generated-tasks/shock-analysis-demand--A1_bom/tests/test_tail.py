"""
TailSkills variant test — auto-generated.
Variant: A1_bom
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """Output file must exist."""
        output_path = "/root/test - demand.xlsx"
        assert os.path.isfile(output_path), f"Output file not found: {output_path}"
