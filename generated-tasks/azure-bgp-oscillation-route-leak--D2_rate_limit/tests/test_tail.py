"""
TailSkills variant test — B1_readonly_output
Verifies oscillation_report.json exists in /app/output under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """oscillation_report.json must exist in /app/output."""
        import os
        assert os.path.exists('/app/output/oscillation_report.json'), "Output file /app/output/oscillation_report.json not found"
