"""
TailSkills variant test — auto-generated.
Variant: C1_nan_poison
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_nan_in_output_json(self):
        """Output JSON should not contain NaN/Inf string values."""
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
                assert '"NaN"' not in content and '"nan"' not in content, \
                    f"NaN string found in {filepath}"
                assert '"Inf"' not in content and '"inf"' not in content, \
                    f"Inf string found in {filepath}"
