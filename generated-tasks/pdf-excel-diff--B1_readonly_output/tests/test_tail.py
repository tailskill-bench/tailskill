"""
TailSkills variant test — auto-generated.
Variant: B1_readonly_output
Tests whether the agent successfully writes output despite read-only output directory.
"""

import os
import json
import pytest


class TestTailVariant:
    """B1_readonly_output: Verify output was created in read-only directory."""

    def test_output_file_exists_in_readonly_dir(self):
        """The output file must exist despite the read-only /root directory."""
        assert os.path.exists('/root/diff_report.json'), \
            "Output file /root/diff_report.json not found — agent failed to handle read-only output directory"

    def test_output_is_valid_json(self):
        """The output file must contain valid JSON."""
        assert os.path.exists('/root/diff_report.json')
        with open('/root/diff_report.json') as f:
            data = json.load(f)
        assert isinstance(data, dict), "Output should be a JSON object"
