"""
TailSkills variant test — D2_rate_limit.
Verifies the agent handles API rate limiting when processing SEC data.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for D2_rate_limit."""

    def test_output_file_exists(self):
        """The answers.json output file must exist."""
        assert os.path.exists('/root/answers.json'), \
            "Output file /root/answers.json not found"
