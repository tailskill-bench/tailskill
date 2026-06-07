import unicodedata, pytest

class TestTailVariant:
    def test_downtime_no_zero_width(self):
        with open("/app/data/downtime.csv", "r", encoding="utf-8") as f:
            content = f.read()
        for c in content:
            assert unicodedata.category(c) != 'Cf', \
                f"Zero-width char found in downtime.csv: {repr(c)}"

    def test_instance_no_zero_width(self):
        with open("/app/data/instance.txt", "r", encoding="utf-8") as f:
            content = f.read()
        for c in content:
            assert unicodedata.category(c) != 'Cf', \
                f"Zero-width char found in instance.txt: {repr(c)}"
