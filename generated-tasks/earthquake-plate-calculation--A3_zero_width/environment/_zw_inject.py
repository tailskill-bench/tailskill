"""
TailSkills A3_zero_width: Inject zero-width Unicode characters into JSON data files.
Targets string values in earthquakes_2024.json, PB2002_plates.json, PB2002_boundaries.json.
"""
import json
import os
import random

random.seed(42)

ZW_CHARS = ['\u200b', '\u200c', '\u200d']
TARGET_DIR = "/root"

TARGET_FILES = [
    "earthquakes_2024.json",
    "PB2002_plates.json",
    "PB2002_boundaries.json",
]


def inject_into_string(s):
    """Inject zero-width characters at random positions in a string."""
    if not isinstance(s, str) or len(s) == 0:
        return s
    chars = list(s)
    num_injections = max(1, len(chars) // 15)
    for _ in range(num_injections):
        pos = random.randint(0, len(chars))
        zw = random.choice(ZW_CHARS)
        chars.insert(pos, zw)
    return ''.join(chars)


def inject_into_value(val, depth=0):
    """Recursively inject zero-width chars into string values in JSON structures."""
    if isinstance(val, str):
        return inject_into_string(val)
    elif isinstance(val, dict):
        return {k: inject_into_value(v, depth + 1) for k, v in val.items()}
    elif isinstance(val, list):
        return [inject_into_value(item, depth + 1) for item in val]
    return val


def main():
    for fname in TARGET_FILES:
        fpath = os.path.join(TARGET_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  [skip] {fpath} not found")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        injected = inject_into_value(data)

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(injected, f, ensure_ascii=False)

        print(f"  [injected] {fpath}")


if __name__ == "__main__":
    main()
