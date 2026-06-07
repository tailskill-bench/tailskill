"""
TailSkills A3_zero_width: Clean zero-width Unicode characters from data files.
Strips all Unicode Cf (format) category characters from JSON files.
"""
import json
import os
import sys
import unicodedata


TARGET_DIR = "/root"
TARGET_FILES = [
    "earthquakes_2024.json",
    "PB2002_plates.json",
    "PB2002_boundaries.json",
]


def clean_string(s):
    """Remove zero-width/invisible Unicode characters from a string."""
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')


def clean_value(val):
    """Recursively clean string values in JSON structures."""
    if isinstance(val, str):
        cleaned = clean_string(val)
        return cleaned
    elif isinstance(val, dict):
        return {clean_string(k) if isinstance(k, str) else k: clean_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [clean_value(item) for item in val]
    return val


def main():
    for fname in TARGET_FILES:
        fpath = os.path.join(TARGET_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  [skip] {fpath} not found")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            raw = f.read()

        cleaned_raw = clean_string(raw)
        data = json.loads(cleaned_raw)
        cleaned = clean_value(data)

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False)

        print(f"  [cleaned] {fpath}")


if __name__ == "__main__":
    main()
