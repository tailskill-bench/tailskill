#!/usr/bin/env python3
"""Fix output directory permissions for read-only variants"""
import sys
import os

target = sys.argv[1] if len(sys.argv) > 1 else "/root/answer.json"
target_dir = os.path.dirname(target)

# Walk up and fix permissions
path = target_dir
while path and path != '/':
    try:
        os.chmod(path, 0o755)
    except OSError:
        pass
    path = os.path.dirname(path)

# Remove any existing file at output path
if os.path.exists(target):
    os.remove(target)

print(f"Fixed permissions for {target_dir}")
