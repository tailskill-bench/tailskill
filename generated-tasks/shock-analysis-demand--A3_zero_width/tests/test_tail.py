"""
TailSkills variant test — auto-generated.
Variant: A3_zero_width
"""

import os
import pytest


class TestTailVariant:
    def test_output_file_exists(self):
        output_path = "/root/test - demand.xlsx"
        assert os.path.isfile(output_path), f"Output file not found: {output_path}"
