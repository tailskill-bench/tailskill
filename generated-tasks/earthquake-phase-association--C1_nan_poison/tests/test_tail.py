"""
TailSkills variant test — auto-generated.
Variant: C1_nan_poison
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_nan_in_numeric_output(self):
        """Output should not contain NaN values even if input has them."""
        import os
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not available")

        for f in os.listdir('/root'):
            if f.endswith('.xlsx') and not f.startswith('.'):
                wb = openpyxl.load_workbook(f'/root/{f}', data_only=True)
                for ws in wb.worksheets:
                    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                        for col_idx, cell in enumerate(row):
                            if isinstance(cell, float):
                                assert cell == cell, (
                                    f"NaN found in {f}, sheet '{ws.title}', "
                                    f"row {row_idx}, col {col_idx}"
                                )

