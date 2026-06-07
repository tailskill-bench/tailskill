import os, pytest

class TestTailVariant:
    def test_csv_no_bom(self):
        with open("/app/data/downtime.csv", "rb") as f:
            head = f.read(3)
        assert head != b"\xef\xbb\xbf", "BOM should be stripped from downtime.csv"
