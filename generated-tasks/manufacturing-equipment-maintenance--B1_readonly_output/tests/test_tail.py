"""
TailSkills variant test — B1_readonly_output
Verifies output files exist in /app/output under readonly directory conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_files_exist(self):
        """At least one output JSON file must exist in /app/output."""
        output_dir = "/app/output"
        assert os.path.isdir(output_dir), f"Output directory {output_dir} does not exist"
        output_files = [f for f in os.listdir(output_dir)
                       if f.endswith('.json') and not f.startswith('.')]
        assert len(output_files) > 0, "No output JSON files found in /app/output"
