"""
TailSkills variant test — A3_zero_width
Verifies output JSON does not contain zero-width Unicode characters.
"""

import json
import os
import pytest

ZW_CHARS = {"\u200b", "\u200c", "\u200d", "\ufeff"}
ZW_CATS = {"Cf", "Cc"}


def _has_zw(text):
    return any(c in ZW_CHARS for c in text)


class TestTailVariant:
    """Tail-variant specific assertions."""

    def test_no_zero_width_in_output(self):
        """Output JSON files should not contain zero-width Unicode characters."""
        scan_dirs = ["/app", "/app/output"]
        for scan_dir in scan_dirs:
            if not os.path.isdir(scan_dir):
                continue
            for f in os.listdir(scan_dir):
                if f.endswith(".json"):
                    filepath = os.path.join(scan_dir, f)
                    with open(filepath, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    assert not _has_zw(content), f"Zero-width chars found in: {filepath}"
