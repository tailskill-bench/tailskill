"""
TailSkills variant test — auto-generated.
Variant: B1_readonly_output
"""

import os
import pytest


class TestTailVariant:
    def test_output_file_exists(self):
        output_path = "/root/test - demand.xlsx"
        assert os.path.isfile(output_path), f"Output file not found: {output_path}"

    def test_output_is_valid_xlsx(self):
        output_path = "/root/test - demand.xlsx"
        with open(output_path, "rb") as f:
            header = f.read(4)
        assert header.startswith(b"PK"), f"Output file is not a valid XLSX (ZIP): {header}"
