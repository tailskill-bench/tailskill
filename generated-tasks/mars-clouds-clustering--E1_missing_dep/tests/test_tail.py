"""
TailSkills variant test — E1_missing_dep (scikit-learn).
Verifies the agent recovers from missing scikit-learn dependency.
"""

import os
import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for E1_missing_dep."""

    def test_output_file_exists(self):
        """The pareto_frontier.csv output file must exist."""
        assert os.path.exists('/root/pareto_frontier.csv'), \
            "Output file /root/pareto_frontier.csv not found"

    def test_sklearn_reinstalled(self):
        """scikit-learn must be reinstalled after being removed."""
        result = subprocess.run(
            ['python3', '-c', 'import sklearn; print(sklearn.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"sklearn not importable: {result.stderr}"

    def test_sklearn_functional(self):
        """sklearn DBSCAN must be functional."""
        result = subprocess.run(
            ['python3', '-c',
             'from sklearn.cluster import DBSCAN; '
             'import numpy as np; '
             'X = np.array([[1,2],[2,2],[2,3],[8,7],[8,8]]); '
             'db = DBSCAN(eps=3).fit(X); print(len(db.labels_))'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"sklearn DBSCAN test failed: {result.stderr}"

    def test_output_has_content(self):
        """The output CSV should have data rows."""
        with open('/root/pareto_frontier.csv') as f:
            lines = [l.strip() for l in f if l.strip()]
        assert len(lines) > 1, \
            f"Output has only {len(lines)} lines, expected header + data"
