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

    def test_scipy_curve_fit_functional(self):
        """scipy.optimize.curve_fit must be functional."""
        from scipy.optimize import curve_fit
        import numpy as np
        x = np.array([1.0, 2.0, 3.0, 4.0])
        y = 2.0 * x + 1.0
        popt, _ = curve_fit(lambda x, a, b: a * x + b, x, y)
        assert abs(popt[0] - 2.0) < 0.1, f"Expected slope≈2, got {popt[0]}"
        assert abs(popt[1] - 1.0) < 0.1, f"Expected intercept≈1, got {popt[1]}"

    def test_metrics_has_required_keys(self):
        """The metrics report must contain required keys."""
        with open('/root/metrics.json') as f:
            metrics = json.load(f)
        required_keys = ['overshoot', 'settling_time', 'steady_state_error']
        for key in required_keys:
            assert key in metrics, f"metrics.json missing required key: {key}"
