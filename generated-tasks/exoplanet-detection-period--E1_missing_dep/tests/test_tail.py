"""
TailSkills variant test — E1_missing_dep (transitleastsquares).
Verifies the agent recovers from missing transitleastsquares dependency.
"""

import os
import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for E1_missing_dep."""

    def test_output_file_exists(self):
        """The period.txt output file must exist."""
        assert os.path.exists('/root/period.txt'), \
            "Output file /root/period.txt not found"

    def test_tls_reinstalled(self):
        """transitleastsquares must be reinstalled after being removed."""
        result = subprocess.run(
            ['python3', '-c', 'import transitleastsquares; print("ok")'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"transitleastsquares not importable: {result.stderr}"

    def test_tls_functional(self):
        """transitleastsquares must be functional for period search."""
        result = subprocess.run(
            ['python3', '-c',
             'import numpy as np; from transitleastsquares import transitleastsquares; '
             't = np.linspace(0, 10, 100); f = np.ones(100); '
             'model = transitleastsquares(t, f); print("functional")'],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, \
            f"transitleastsquares functional test failed: {result.stderr}"

    def test_output_has_valid_period(self):
        """The output period should be a positive number."""
        with open('/root/period.txt') as f:
            content = f.read().strip()
        period = float(content)
        assert period > 0, f"Period should be positive, got {period}"
