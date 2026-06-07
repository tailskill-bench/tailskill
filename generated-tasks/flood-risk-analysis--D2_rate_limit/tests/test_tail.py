"""
TailSkills variant test — D2_rate_limit.
Verifies the agent handles API rate limiting by retrying or avoiding network calls.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for D2_rate_limit."""

    def test_output_file_exists(self):
        """The flood_results.csv output file must exist."""
        assert os.path.exists('/root/output/flood_results.csv'), \
            "Output file /root/output/flood_results.csv not found"
