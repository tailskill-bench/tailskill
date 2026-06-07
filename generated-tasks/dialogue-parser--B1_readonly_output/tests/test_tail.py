"""
TailSkills variant test — B1_readonly_output
Verifies output files exist in /app under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_files_exist(self):
        """Output JSON and DOT files must exist in /app."""
        assert os.path.exists("/app/dialogue.json"), "dialogue.json not found in /app"
        assert os.path.exists("/app/dialogue.dot"), "dialogue.dot not found in /app"
