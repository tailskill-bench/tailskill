#!/usr/bin/env python3
"""Fix read-only directories for output writing"""
import sys, os, stat

output = sys.argv[1] if len(sys.argv) > 1 else "/root/nasa_budget_recovered.xlsx"

path = os.path.dirname(os.path.abspath(output))
while path != "/":
    try:
        os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    except OSError:
        pass
    parent = os.path.dirname(path)
    if parent == path:
        break
    path = parent

for d in ["/root"]:
    if os.path.isdir(d):
        try:
            os.chmod(d, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        except OSError:
            pass

print(f"Permissions fixed for {output}")
