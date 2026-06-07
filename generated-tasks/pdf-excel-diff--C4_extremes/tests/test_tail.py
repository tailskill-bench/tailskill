"""
TailSkills variant test — auto-generated.
Variant: C4_extremes
These tests verify the skill produces correct output under variant conditions.
"""

import os
import json
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_extreme_values_in_output(self):
        """Output JSON should not contain extreme injected values (-999, -1, 999999)."""
        output_dirs = ['/root', '/root/output']
        extreme_values = [-999, -1, 999999]
        for output_dir in output_dirs:
            if not os.path.isdir(output_dir):
                continue
            for f in os.listdir(output_dir):
                if not f.endswith('.json') or f.startswith('.'):
                    continue
                filepath = os.path.join(output_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                for ev in extreme_values:
                    assert str(ev) not in content, \
                        f"Extreme value {ev} found in {filepath}"

    def test_output_file_exists(self):
        """The diff report JSON must exist."""
        assert os.path.exists('/root/diff_report.json'), \
            "Output file /root/diff_report.json not found"
