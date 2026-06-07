import os, stat, pytest

class TestTailVariant:
    def test_root_is_writable(self):
        mode = os.stat('/root').st_mode
        assert mode & stat.S_IWUSR, "/root should be writable after prepare_output.py"
