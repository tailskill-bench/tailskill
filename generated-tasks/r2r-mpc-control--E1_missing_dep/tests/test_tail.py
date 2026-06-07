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
        """The metrics.json output file must exist."""
        assert os.path.exists('/root/metrics.json'), \
            "Output file /root/metrics.json not found"

    def test_scipy_reinstalled(self):
        """scipy must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('scipy')
        assert mod is not None, "scipy should have been reinstalled by the solver"

    def test_scipy_linalg_functional(self):
        """scipy.linalg must be functional."""
        from scipy import linalg
        import numpy as np
        A = np.array([[1.0, 2.0], [3.0, 4.0]])
        det = linalg.det(A)
        assert abs(det - (-2.0)) < 1e-10, f"Expected det≈-2, got {det}"

    def test_metrics_has_required_keys(self):
        """The metrics report must contain required keys."""
        with open('/root/metrics.json') as f:
            metrics = json.load(f)
        required_keys = ['settling_time', 'steady_state_error']
        for key in required_keys:
            assert key in metrics, f"metrics.json missing required key: {key}"
