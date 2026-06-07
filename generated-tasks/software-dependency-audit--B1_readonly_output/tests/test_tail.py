"""
TailSkills variant test — auto-generated.
Variant: B1_readonly_output
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """The output file must exist."""
        assert os.path.exists('/root/security_audit.csv'), "Output file /root/security_audit.csv not found"

