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
        output_dir = '/root/redacted'
        output_files = [f for f in os.listdir(output_dir)
                       if f.endswith(('.xlsx', '.csv', '.json', '.pdf'))
                       and not f.startswith('.')]
        assert len(output_files) > 0, f"No output files found in {output_dir}"

