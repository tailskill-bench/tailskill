#!/usr/bin/env python3
"""Remove zero-width Unicode characters from JSON files in a directory."""
import sys
import unicodedata
from pathlib import Path


def clean_file(filepath):
    """Strip zero-width characters from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = ''.join(ch for ch in content if unicodedata.category(ch) != 'Cf')
    if cleaned != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        return True
    return False


def clean_directory(dirpath):
    """Clean all JSON files in a directory recursively."""
    cleaned = 0
    for p in Path(dirpath).rglob('*.json'):
        if clean_file(p):
            cleaned += 1
            print(f'Cleaned: {p}')
    return cleaned


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: clean_data.py <directory_or_file>')
        sys.exit(1)
    target = sys.argv[1]
    if Path(target).is_dir():
        n = clean_directory(target)
        print(f'Cleaned {n} JSON files')
    else:
        clean_file(target)
        print(f'Cleaned: {target}')
