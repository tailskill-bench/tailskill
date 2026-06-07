"""
TailSkills variant test — auto-generated.
Variant: C1_nan_poison
These tests verify the skill produces correct output under variant conditions.
"""

import os
import json
import math
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_nan_in_csv_output(self):
        """Output CSV files should not contain NaN values even if input has them."""
        output_dirs = ['/app/output', '/root']
        for output_dir in output_dirs:
            if not os.path.isdir(output_dir):
                continue
            for f in os.listdir(output_dir):
                if not f.endswith('.csv') or f.startswith('.'):
                    continue
                filepath = os.path.join(output_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    for line_num, line in enumerate(fh, 1):
                        parts = line.strip().split(',')
                        for col_num, val in enumerate(parts):
                            if val.lower() in ('nan', 'inf', '-inf', '+inf'):
                                pytest.fail(
                                    f"NaN/Inf found in {filepath}, "
                                    f"line {line_num}, col {col_num}: '{val}'"
                                )

    def test_no_nan_in_json_output(self):
        """Output JSON should not contain NaN/Inf values."""
        output_dirs = ['/app/output', '/root']
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
