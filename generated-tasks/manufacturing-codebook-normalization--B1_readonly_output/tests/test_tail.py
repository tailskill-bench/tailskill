"""
TailSkills variant test — B1_readonly_output
Verifies solution.json exists in /app/output under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """solution.json must exist in /app/output."""
        import os
        assert os.path.exists('/app/output/solution.json'), "Output file /app/output/solution.json not found"
