"""
TailSkills variant test — auto-generated.
Variant: B1_readonly_output
Tests whether output files were created despite read-only /root/output directory.
"""

import os
import pytest


class TestTailVariant:
    """B1_readonly_output: Verify output was created in read-only directory."""

    def test_output_files_in_readonly_dir(self):
        """Output files must exist despite read-only /root/output."""
        assert os.path.exists('/root/output/trend_result.csv'), \
            "trend_result.csv not found in read-only /root/output"
        assert os.path.exists('/root/output/dominant_factor.csv'), \
            "dominant_factor.csv not found in read-only /root/output"
