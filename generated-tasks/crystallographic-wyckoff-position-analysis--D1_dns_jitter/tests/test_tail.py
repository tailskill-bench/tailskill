"""
TailSkills variant test — B1_readonly_output
Verifies solution.py exists in /root/workspace under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_solution_file_exists(self):
        """solution.py must exist in /root/workspace."""
        assert os.path.exists("/root/workspace/solution.py"), "solution.py not found in /root/workspace"
