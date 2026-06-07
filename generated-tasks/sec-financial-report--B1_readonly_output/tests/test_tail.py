"""
TailSkills variant test — B1_readonly_output
Verifies answers.json exists in /root under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """answers.json must exist in /root."""
        assert os.path.exists("/root/answers.json"), "answers.json not found in /root"
