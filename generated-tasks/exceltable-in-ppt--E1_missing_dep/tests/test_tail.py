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
        """At least one output file must exist."""
        import os
        assert os.path.exists('/root/results.pptx'), "Output file /root/results.pptx not found"

