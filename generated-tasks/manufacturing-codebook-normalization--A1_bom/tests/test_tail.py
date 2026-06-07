import os, pytest

class TestTailVariant:
    def test_csv_no_bom(self):
        with open("/app/data/test_center_logs.csv", "rb") as f:
            head = f.read(3)
        assert head != b"\xef\xbb\xbf", "BOM should be stripped from test_center_logs.csv"
