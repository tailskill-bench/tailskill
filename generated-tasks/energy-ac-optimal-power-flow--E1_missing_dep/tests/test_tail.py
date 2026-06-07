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

    def test_casadi_reinstalled(self):
        """casadi must be available (reinstalled by the solver)."""
        import importlib
        mod = importlib.import_module('casadi')
        assert mod is not None, "casadi should have been reinstalled by the solver"

    def test_casadi_nlpsol_functional(self):
        """CasADi NLP solver must be functional."""
        import casadi as ca
        import numpy as np
        x = ca.MX.sym('x')
        nlp = {'x': x, 'f': (x - 3)**2}
        solver = ca.nlpsol('solver', 'ipopt', nlp, {'ipopt.print_level': 0, 'print_time': False})
        sol = solver(x0=0.0)
        assert abs(float(sol['x']) - 3.0) < 1e-4, \
            f"IPOPT solver should find x≈3, got {float(sol['x'])}"

    def test_report_has_summary(self):
        """The report must contain a summary with solver_status."""
        with open('/root/report.json') as f:
            report = json.load(f)
        assert 'summary' in report, "report.json missing 'summary' key"
        assert report['summary'].get('solver_status') == 'optimal', \
            f"Expected solver_status='optimal', got '{report['summary'].get('solver_status')}'"
