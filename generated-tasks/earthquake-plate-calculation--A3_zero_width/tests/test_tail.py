"""
TailSkills variant test: verify zero-width characters were cleaned from data files.
"""
import json
import os
import unicodedata


TARGET_DIR = "/root"
TARGET_FILES = [
    "earthquakes_2024.json",
    "PB2002_plates.json",
    "PB2002_boundaries.json",
]


def test_data_files_cleaned():
    """Data files should not contain zero-width Unicode characters after Oracle cleaning."""
    for fname in TARGET_FILES:
        fpath = os.path.join(TARGET_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        zw_chars = [ch for ch in content if unicodedata.category(ch) == 'Cf']
        assert len(zw_chars) == 0, \
            f"{fpath} still contains {len(zw_chars)} zero-width/invisible characters"


def test_answer_json_exists():
    """answer.json should exist as output."""
    assert os.path.exists("/root/answer.json"), "answer.json not found at /root/answer.json"


def test_answer_valid_json():
    """answer.json should be valid JSON with required fields."""
    with open("/root/answer.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    required_fields = ["id", "place", "time", "magnitude", "latitude", "longitude", "distance_km"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
