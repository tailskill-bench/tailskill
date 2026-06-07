"""TailSkills variant test — B1_readonly_output for glm-lake-mendota."""
import os
import stat
import pytest


class TestTailVariant:
    """B1_readonly_output: output directory was read-only; verify it is now writable."""

    def test_output_dir_writable(self):
        output_dir = "/root/output"
        assert os.path.isdir(output_dir), f"Output directory {output_dir} does not exist"
        mode = os.stat(output_dir).st_mode
        assert mode & stat.S_IWUSR, f"Output directory {output_dir} is not writable"

    def test_output_file_exists(self):
        nc_path = "/root/output/output.nc"
        assert os.path.exists(nc_path), "output.nc not found in /root/output/"
