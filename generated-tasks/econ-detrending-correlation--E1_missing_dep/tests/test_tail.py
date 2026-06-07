"""
TailSkills variant test — auto-generated.
Variant: E1_missing_dep
These tests verify the skill produces correct output under variant conditions.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_output_file_exists(self):
        """The answer file must exist."""
        assert os.path.exists('/root/answer.txt'), \
            "Output file /root/answer.txt not found"

    def test_statsmodels_reinstalled(self):
        """statsmodels must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('statsmodels')
        assert mod is not None, "statsmodels should have been reinstalled by the solver"

    def test_hpfilter_functional(self):
        """HP filter must be functional for data processing."""
        from statsmodels.tsa.filters.hp_filter import hpfilter
        import numpy as np
        data = np.random.randn(100)
        cycle, trend = hpfilter(data, lamb=100)
        assert len(cycle) == 100
        assert len(trend) == 100
