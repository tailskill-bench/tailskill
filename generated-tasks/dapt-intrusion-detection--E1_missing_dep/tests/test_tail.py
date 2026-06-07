"""
TailSkills variant test — E1_missing_dep (scapy).
Verifies the agent recovers from missing scapy dependency.
"""

import os
import subprocess
import pytest


class TestTailVariant:
    """Tail-variant specific assertions for E1_missing_dep."""

    def test_output_file_exists(self):
        """The network_stats.csv output file must exist."""
        assert os.path.exists('/root/network_stats.csv'), \
            "Output file /root/network_stats.csv not found"

    def test_scapy_reinstalled(self):
        """Scapy must be reinstalled after being removed."""
        result = subprocess.run(
            ['python3', '-c', 'import scapy; print(scapy.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"scapy not importable: {result.stderr}"

    def test_scapy_functional(self):
        """Scapy rdpcap must be functional."""
        result = subprocess.run(
            ['python3', '-c',
             'from scapy.all import rdpcap, IP, TCP; '
             'pkts = rdpcap("/root/packets.pcap"); '
             'tcp = [p for p in pkts if TCP in p]; '
             'print(len(tcp))'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"scapy rdpcap failed: {result.stderr}"

    def test_output_has_content(self):
        """The output CSV should have more than just headers."""
        with open('/root/network_stats.csv') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        assert len(lines) > 5, \
            f"Output has only {len(lines)} non-comment lines, expected more"
