"""
TailSkills variant test — auto-generated.
Variant: A3_zero_width
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """At least one output file must exist."""
        import os
        output_files = [f for f in os.listdir('/root')
                       if f.endswith(('.xlsx', '.csv', '.json', '.pdf'))
                       and not f.startswith('.')]
        assert len(output_files) > 0, "No output files found in /root"

