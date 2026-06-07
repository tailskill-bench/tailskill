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
        """The report.json output file must exist."""
        assert os.path.exists('/root/report.json'), \
            "Output file /root/report.json not found"

    def test_cvxpy_reinstalled(self):
        """cvxpy must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('cvxpy')
        assert mod is not None, "cvxpy should have been reinstalled by the solver"

    def test_cvxpy_functional(self):
        """CVXPY solver must be functional."""
        import cvxpy as cp
        import numpy as np
        x = cp.Variable()
        prob = cp.Problem(cp.Minimize((x - 5)**2), [x >= 0])
        prob.solve()
        assert abs(x.value - 5.0) < 1e-4, \
            f"CVXPY solver should find x≈5, got {x.value}"

    def test_report_has_structure(self):
        """The report must contain base_case and counterfactual."""
        with open('/root/report.json') as f:
            report = json.load(f)
        assert 'base_case' in report, "report.json missing 'base_case' key"
        assert 'counterfactual' in report, "report.json missing 'counterfactual' key"
        assert 'impact_analysis' in report, "report.json missing 'impact_analysis' key"
