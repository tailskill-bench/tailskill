"""
TailSkills variant test — auto-generated.
Variant: C4_extremes
These tests verify the skill produces correct output under variant conditions.
"""

import os
import csv
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_extreme_values_in_output(self):
        """Output CSV files should not contain extreme values (0, negative) in price columns."""
        output_dirs = ['/app/output', '/root']
        for output_dir in output_dirs:
            if not os.path.isdir(output_dir):
                continue
            for f in os.listdir(output_dir):
                if not f.endswith('.csv') or f.startswith('.'):
                    continue
                filepath = os.path.join(output_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    reader = csv.reader(fh)
                    header = next(reader, None)
                    if header is None:
                        continue
                    # Find price-related columns
                    price_cols = []
                    for idx, col in enumerate(header):
                        lower = col.lower()
                        if 'price' in lower or 'spend' in lower or 'amount' in lower:
                            price_cols.append(idx)
                    if not price_cols:
                        continue
                    for row_num, row in enumerate(reader, 2):
                        for col_idx in price_cols:
                            if col_idx < len(row):
                                try:
                                    val = float(row[col_idx])
                                    assert val > 0, (
                                        f"Extreme value {val} found in {filepath}, "
                                        f"row {row_num}, col {col_idx} ({header[col_idx]})"
                                    )
                                except ValueError:
                                    pass

    def test_output_file_exists(self):
        """At least one output file must exist in /app/output."""
        for output_dir in ['/app/output', '/root']:
            if not os.path.isdir(output_dir):
                continue
            output_files = [f for f in os.listdir(output_dir)
                           if f.endswith(('.xlsx', '.csv', '.json', '.pdf'))
                           and not f.startswith('.')]
            if len(output_files) > 0:
                return
        pytest.fail("No output files found in /app/output or /root")
