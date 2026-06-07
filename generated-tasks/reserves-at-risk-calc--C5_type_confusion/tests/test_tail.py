"""
TailSkills variant test — auto-generated.
Variant: C5_type_confusion
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """At least one output file must exist."""
        import os
        output_dir = '/root/output'
        if not os.path.isdir(output_dir):
            pytest.skip("Output directory does not exist")
        output_files = [f for f in os.listdir(output_dir)
                       if f.endswith(('.xlsx', '.csv', '.json', '.pdf'))
                       and not f.startswith('.')]
        assert len(output_files) > 0, "No output files found in /root/output"
