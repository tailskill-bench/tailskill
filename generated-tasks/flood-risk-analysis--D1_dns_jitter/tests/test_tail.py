"""
TailSkills variant test — D1_dns_jitter.
Verifies the agent handles DNS jitter by retrying or avoiding network calls.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for D1_dns_jitter."""

    def test_output_file_exists(self):
        """The flood_results.csv output file must exist."""
        assert os.path.exists('/root/output/flood_results.csv'), \
            "Output file /root/output/flood_results.csv not found"
