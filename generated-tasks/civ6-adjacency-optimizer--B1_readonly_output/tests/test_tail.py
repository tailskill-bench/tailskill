"""
TailSkills variant test — B1_readonly_output
Verifies scenario_3.json exists in /output under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """Output file must exist in /output."""
        import os
        assert os.path.exists('/output/scenario_3.json'), "Output file /output/scenario_3.json not found"
