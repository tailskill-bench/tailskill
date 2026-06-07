#!/usr/bin/env python3
"""Strip BOM from CSV/text files."""
import sys

for path in sys.argv[1:]:
    with open(path, 'rb') as f:
        data = f.read()
    if data.startswith(b'\xef\xbb\xbf'):
        with open(path, 'wb') as f:
            f.write(data[3:])
        print(f"Stripped BOM from {path}")
    else:
        print(f"No BOM found in {path}")
