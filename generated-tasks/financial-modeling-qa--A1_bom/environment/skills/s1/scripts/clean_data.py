"""Strip UTF-8 BOM from CSV/TXT/JSON files in /root/."""
import os, glob

targets = glob.glob('/root/*.csv') + glob.glob('/root/*.txt') + glob.glob('/root/*.json')
for path in targets:
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'\xef\xbb\xbf':
        with open(path, 'wb') as f:
            f.write(data[3:])
        print(f"Stripped BOM from {path}")
