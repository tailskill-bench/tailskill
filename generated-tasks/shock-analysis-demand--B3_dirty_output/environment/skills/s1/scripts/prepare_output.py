#!/usr/bin/env python3
"""Fix output directory permissions and remove pre-existing corrupted output files."""
import os, sys

for d in ["/root"]:
    if os.path.isdir(d):
        os.chmod(d, 0o755)

output = "/root/test - demand.xlsx"
if os.path.isfile(output):
    with open(output, "rb") as f:
        header = f.read(4)
    if not header.startswith(b"PK"):
        os.remove(output)
        print(f"Removed corrupted file: {output}")

print(f"Permissions fixed for /root")
