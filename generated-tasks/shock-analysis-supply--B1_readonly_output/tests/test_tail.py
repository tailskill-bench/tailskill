import os, pytest

class TestTailVariant:
    def test_output_file_exists(self):
        assert os.path.isfile("/root/test-supply.xlsx")

    def test_output_is_valid_xlsx(self):
        with open("/root/test-supply.xlsx", "rb") as f:
            header = f.read(4)
        assert header[:2] == b'PK', "File should be valid XLSX (PK header)"
