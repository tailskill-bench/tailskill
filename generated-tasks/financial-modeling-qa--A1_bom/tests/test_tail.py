import os, glob, pytest

class TestTailVariant:
    def test_no_bom_in_output_files(self):
        for path in glob.glob('/root/*.csv') + glob.glob('/root/*.txt') + glob.glob('/root/*.json'):
            with open(path, 'rb') as f:
                header = f.read(3)
            assert header != b'\xef\xbb\xbf', f"BOM still present in {path}"
