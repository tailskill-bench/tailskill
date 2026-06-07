#!/usr/bin/env python3
"""Fix output directory permissions and remove pre-existing output files."""
import os, sys

output = sys.argv[1] if len(sys.argv) > 1 else "/root/output/rar_result.xlsx"

# Fix parent directory permissions
for d in ["/root", "/root/output"]:
    if os.path.isdir(d):
        os.chmod(d, 0o755)

# Remove dirty output file if it exists and is corrupted
if os.path.isfile(output):
    with open(output, 'rb') as f:
        header = f.read(4)
    if not header.startswith(b'PK'):
        os.remove(output)
        print(f"Removed corrupted file: {output}")

print(f"Permissions fixed for /root and /root/output")
