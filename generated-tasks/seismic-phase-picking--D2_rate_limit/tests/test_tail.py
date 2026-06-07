"""
TailSkills variant test — B1_readonly_output
Verifies output directory is writable and results file exists.
"""
import os
import pytest


class TestTailVariant:

    def test_output_dir_writable(self):
        """Output directory /root must be writable."""
        assert os.path.isdir("/root"), "/root must exist"
        assert os.access("/root", os.W_OK), "/root must be writable"

    def test_output_file_exists(self):
        """results.csv must exist."""
        output = "/root/results.csv"
        assert os.path.isfile(output), f"{output} must exist"
        assert os.path.getsize(output) > 0, f"{output} must not be empty"
