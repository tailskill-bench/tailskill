#!/usr/bin/env python3
"""Fix output directory permissions."""
import os, sys

for d in ["/root"]:
    if os.path.isdir(d):
        os.chmod(d, 0o755)
print(f"Permissions fixed for /root")
