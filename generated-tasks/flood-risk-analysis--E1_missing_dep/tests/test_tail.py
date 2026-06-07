"""
TailSkills variant test — auto-generated.
Variant: E1_missing_dep
These tests verify the skill produces correct output under variant conditions.
"""

import os
import json
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """The flood_results.csv output file must exist."""
        assert os.path.exists('/root/output/flood_results.csv'), \
            "Output file /root/output/flood_results.csv not found"

    def test_dataretrieval_reinstalled(self):
        """dataretrieval must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('dataretrieval')
        assert mod is not None, "dataretrieval should have been reinstalled by the solver"

    def test_nwis_functional(self):
        """dataretrieval.nwis module must be importable."""
        from dataretrieval import nwis
        assert hasattr(nwis, 'get_iv'), "nwis.get_iv function should exist"

    def test_output_has_content(self):
        """The output CSV should have more than just headers."""
        with open('/root/output/flood_results.csv') as f:
            lines = f.readlines()
        assert len(lines) > 1, "Output CSV should have header + data rows"
