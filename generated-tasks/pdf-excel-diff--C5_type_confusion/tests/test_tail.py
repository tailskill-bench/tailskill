"""
TailSkills variant test — auto-generated.
Variant: C5_type_confusion
These tests verify the skill produces correct output under variant conditions.
"""

import os
import json
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_text_markers_in_output(self):
        """Output JSON should not contain injected text markers."""
        text_markers = ['"N/A"', '"TBD"', '"null"', '"none"', '"-"']
        output_dirs = ['/root', '/root/output']
        for output_dir in output_dirs:
            if not os.path.isdir(output_dir):
                continue
            for f in os.listdir(output_dir):
                if not f.endswith('.json') or f.startswith('.'):
                    continue
                filepath = os.path.join(output_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                for marker in text_markers:
                    assert marker not in content, \
                        f"Text marker {marker} found in {filepath}"

    def test_output_file_exists(self):
        """The diff report JSON must exist."""
        assert os.path.exists('/root/diff_report.json'), \
            "Output file /root/diff_report.json not found"
