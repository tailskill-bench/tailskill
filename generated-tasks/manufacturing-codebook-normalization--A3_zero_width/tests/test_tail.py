import csv, unicodedata, pytest

class TestTailVariant:
    def test_csv_no_zero_width(self):
        with open("/app/data/test_center_logs.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for val in row.values():
                    if val:
                        for c in val:
                            assert unicodedata.category(c) != 'Cf', \
                                f"Zero-width char found in row {row.get('record_id')}: {repr(val[:40])}"
