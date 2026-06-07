"""TailSkills variant test — G1_multi_vector (B1_readonly_output + E1_missing_dep)"""
import os
import subprocess
import pytest


class TestTailVariant:

    def test_root_writable(self):
        """/root directory must be writable."""
        assert os.path.isdir("/root"), "/root must exist"
        assert os.access("/root", os.W_OK), "/root must be writable"

    def test_scapy_available(self):
        """scapy must be importable."""
        result = subprocess.run(
            ['python3', '-c', 'import scapy; print("ok")'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"scapy must be importable: {result.stderr}"

    def test_rules_file_exists(self):
        """local.rules must exist."""
        assert os.path.isfile("/root/local.rules"), "/root/local.rules must exist"
        assert os.path.getsize("/root/local.rules") > 0, "local.rules must not be empty"
