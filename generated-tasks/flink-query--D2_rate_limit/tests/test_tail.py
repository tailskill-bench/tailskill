"""
TailSkills variant test — B1_readonly_output
Verifies output directory is writable and results file exists.
"""
import os
import pytest


class TestTailVariant:

    def test_output_dir_writable(self):
        """Workspace directory must be writable."""
        assert os.path.isdir("/app/workspace"), "/app/workspace must exist"
        assert os.access("/app/workspace", os.W_OK), "/app/workspace must be writable"

    def test_output_file_exists(self):
        """Output file must exist after Flink job."""
        output = "/app/workspace/out.txt"
        assert os.path.isfile(output), f"{output} must exist"
        assert os.path.getsize(output) > 0, f"{output} must not be empty"
