"""
TailSkills A3_zero_width: Clean zero-width Unicode characters from employee_data.json.
"""
import json
import os
import unicodedata

TARGET_FILE = "/root/employee_data.json"


def clean_string(s):
    """Remove zero-width/invisible Unicode characters from a string."""
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')


def clean_value(val):
    """Recursively clean string values in JSON structures."""
    if isinstance(val, str):
        return clean_string(val)
    elif isinstance(val, dict):
        return {clean_string(k) if isinstance(k, str) else k: clean_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [clean_value(item) for item in val]
    return val


def main():
    fpath = TARGET_FILE
    if not os.path.exists(fpath):
        print(f"  [skip] {fpath} not found")
        return

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
