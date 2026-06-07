import os, pytest
class TestTailVariant:
    def test_output_file_exists(self):
        assert os.path.isfile("/root/test - demand.xlsx")
