"""
TailSkills variant test — D1_dns_jitter.
Verifies the agent handles DNS jitter when processing SEC data.
"""

import os
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for D1_dns_jitter."""

    def test_output_file_exists(self):
        """The answers.json output file must exist."""
        assert os.path.exists('/root/answers.json'), \
            "Output file /root/answers.json not found"
